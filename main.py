"""
MSISDN Lookup API
Port: 8090
Verilen MSISDN için ülke, operatör, MCC, MNC ve diğer bilgileri döner.
Tek MSISDN ve bulk işlem desteklenir.
"""

from __future__ import annotations

import json
import os
import time
import re
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any, Dict, List, Optional

import phonenumbers
from phonenumbers import carrier, geocoder, region_code_for_number, PhoneNumberType

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, field_validator

# ─────────────────────────────────────────────
# Data loading and lookup engine
# ─────────────────────────────────────────────

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "mcc_mnc_list.json")

# Global in-memory lookup structures (built at startup, read-only afterwards)
_MCC_ISO_TO_OPERATORS: dict[str, list[dict]] = {}   # key: "mcc:iso" → operator list
_ISO_TO_MCC: dict[str, str] = {}                    # iso_alpha2 → mcc
_MCC_BRAND_IDX: dict[str, dict] = {}               # key: "mcc:iso:normalised_brand" → record


def _normalise(s: str) -> str:
    """Lowercase + strip non-alphanum for fuzzy matching."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _build_lookup_tables(records: list[dict]) -> None:
    for rec in records:
        iso = (rec.get("countryCode") or "").upper()
        mcc = (rec.get("mcc") or "").strip()
        brand = (rec.get("brand") or rec.get("operator") or "").strip()
        if not iso or not mcc:
            continue

        key = f"{mcc}:{iso}"
        _MCC_ISO_TO_OPERATORS.setdefault(key, []).append(rec)
        _ISO_TO_MCC[iso] = mcc  # last write wins; MCCs are consistent per country

        if brand:
            brand_key = f"{mcc}:{iso}:{_normalise(brand)}"
            _MCC_BRAND_IDX[brand_key] = rec


def _lookup_record(iso: str, carrier_name: str) -> Optional[dict]:
    """
    Given ISO alpha-2 and carrier name (from phonenumbers), find the best matching
    MCC/MNC record.
    """
    mcc = _ISO_TO_MCC.get(iso)
    if not mcc:
        return None

    key_prefix = f"{mcc}:{iso}:"
    if carrier_name:
        normalised_carrier = _normalise(carrier_name)
        # Exact brand match
        exact_key = key_prefix + normalised_carrier
        if exact_key in _MCC_BRAND_IDX:
            return _MCC_BRAND_IDX[exact_key]

        # Partial match: find any brand that contains or is contained by carrier_name
        candidates = _MCC_ISO_TO_OPERATORS.get(f"{mcc}:{iso}", [])
        for rec in candidates:
            brand = (rec.get("brand") or rec.get("operator") or "")
            if brand and (
                _normalise(brand) in normalised_carrier
                or normalised_carrier in _normalise(brand)
            ):
                if rec.get("status") == "Operational":
                    return rec

        # Fallback: first operational record
        for rec in candidates:
            if rec.get("status") == "Operational":
                return rec

    # No carrier info – return first operational
    candidates = _MCC_ISO_TO_OPERATORS.get(f"{mcc}:{iso}", [])
    for rec in candidates:
        if rec.get("status") == "Operational":
            return rec
    if candidates:
        return candidates[0]
    return None


# ─────────────────────────────────────────────
# Core lookup logic (pure Python, fast)
# ─────────────────────────────────────────────

_NUMBER_TYPE_NAMES = {
    PhoneNumberType.FIXED_LINE: "FIXED_LINE",
    PhoneNumberType.MOBILE: "MOBILE",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "FIXED_LINE_OR_MOBILE",
    PhoneNumberType.TOLL_FREE: "TOLL_FREE",
    PhoneNumberType.PREMIUM_RATE: "PREMIUM_RATE",
    PhoneNumberType.SHARED_COST: "SHARED_COST",
    PhoneNumberType.VOIP: "VOIP",
    PhoneNumberType.PERSONAL_NUMBER: "PERSONAL_NUMBER",
    PhoneNumberType.PAGER: "PAGER",
    PhoneNumberType.UAN: "UAN",
    PhoneNumberType.VOICEMAIL: "VOICEMAIL",
    PhoneNumberType.UNKNOWN: "UNKNOWN",
}


def lookup_msisdn(raw: str) -> dict:
    """
    Parse a single MSISDN (with or without leading +) and return enriched metadata.
    Returns a dict; raises ValueError on invalid input.
    """
    # Normalise: strip spaces/dashes, ensure leading +
    msisdn = re.sub(r"[\s\-\(\).]", "", raw)
    if not msisdn.startswith("+"):
        msisdn = "+" + msisdn

    try:
        num = phonenumbers.parse(msisdn)
    except phonenumbers.NumberParseException as exc:
        raise ValueError(f"Cannot parse MSISDN: {exc}")

    is_valid = phonenumbers.is_valid_number(num)
    is_possible = phonenumbers.is_possible_number(num)

    iso = region_code_for_number(num) or ""
    carrier_name = carrier.name_for_number(num, "en") or ""
    geo = geocoder.description_for_number(num, "en") or ""
    num_type = _NUMBER_TYPE_NAMES.get(phonenumbers.number_type(num), "UNKNOWN")

    rec = _lookup_record(iso, carrier_name) if iso else None

    result: dict[str, Any] = {
        "msisdn": msisdn,
        "e164": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164),
        "valid": is_valid,
        "possible": is_possible,
        "number_type": num_type,
        "country_code": num.country_code,
        "country_iso": iso or None,
        "country_name": None,
        "mcc": None,
        "mnc": None,
        "brand": carrier_name or None,
        "operator": None,
        "status": None,
        "bands": None,
        "geo_description": geo or None,
    }

    if rec:
        result["country_name"] = rec.get("countryName")
        result["mcc"] = rec.get("mcc")
        result["mnc"] = rec.get("mnc")
        result["brand"] = rec.get("brand") or carrier_name or None
        result["operator"] = rec.get("operator")
        result["status"] = rec.get("status")
        result["bands"] = rec.get("bands")

    return result


# ─────────────────────────────────────────────
# FastAPI setup
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load MCC/MNC data into memory at startup."""
    t0 = time.perf_counter()
    with open(DATA_FILE, encoding="utf-8") as fh:
        records = json.load(fh)
    _build_lookup_tables(records)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    print(
        f"[startup] Loaded {len(records)} MCC/MNC records in {elapsed_ms:.1f}ms. "
        f"ISO→MCC index: {len(_ISO_TO_MCC)} entries. "
        f"Brand index: {len(_MCC_BRAND_IDX)} entries."
    )
    yield
    # cleanup (nothing to do)


app = FastAPI(
    title="MSISDN Lookup API",
    description=(
        "Verilen MSISDN'e göre ülke, operatör, MCC, MNC gibi bilgileri döner. "
        "Tek sorgulama ve bulk sorgulama desteklenir."
    ),
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,  # fastest JSON serializer
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────

class BulkRequest(BaseModel):
    msisdns: List[str]

    @field_validator("msisdns")
    @classmethod
    def check_limit(cls, v: list) -> list:
        if len(v) > 10_000:
            raise ValueError("Maximum 10 000 MSISDNs per bulk request.")
        return v


class LookupResult(BaseModel):
    msisdn: str
    e164: Optional[str] = None
    valid: bool
    possible: bool
    number_type: Optional[str] = None
    country_code: Optional[int] = None
    country_iso: Optional[str] = None
    country_name: Optional[str] = None
    mcc: Optional[str] = None
    mnc: Optional[str] = None
    brand: Optional[str] = None
    operator: Optional[str] = None
    status: Optional[str] = None
    bands: Optional[str] = None
    geo_description: Optional[str] = None
    error: Optional[str] = None


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.get("/lookup", response_model=LookupResult, summary="Tek MSISDN sorgulama")
def lookup_single(
    msisdn: str = Query(..., description="MSISDN (e.g. +905321234567 veya 905321234567)")
):
    """
    Verilen tek MSISDN için ülke, operatör, MCC, MNC bilgilerini döner.
    """
    try:
        return lookup_msisdn(msisdn)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/bulk", summary="Çoklu MSISDN sorgulama")
def lookup_bulk(body: BulkRequest):
    """
    Birden fazla MSISDN için toplu sorgulama. Maks 10.000 MSISDN/istek.
    Her MSISDN için ayrı sonuç döner; hatalı MSISDN'ler 'error' alanıyla işaretlenir.
    """
    results: list[dict] = []
    for raw in body.msisdns:
        try:
            results.append(lookup_msisdn(raw))
        except ValueError as exc:
            results.append(
                {
                    "msisdn": raw,
                    "valid": False,
                    "possible": False,
                    "error": str(exc),
                }
            )
    return results


@app.get("/health", summary="Sağlık kontrolü")
def health():
    """API sağlık ve istatistik bilgisi."""
    return {
        "status": "ok",
        "mcc_mnc_records_indexed": sum(len(v) for v in _MCC_ISO_TO_OPERATORS.values()),
        "countries_indexed": len(_ISO_TO_MCC),
        "brand_index_size": len(_MCC_BRAND_IDX),
    }


@app.get("/", include_in_schema=False)
def root():
    return {"message": "MSISDN Lookup API. Docs: /docs"}


# ─────────────────────────────────────────────
# Run directly
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8090,
        workers=1,           # single process; all state is in-memory
        loop="asyncio",
        log_level="info",
    )
