"""
MCC/MNC veritabanını GitHub'dan indirir ve data/ klasörüne kaydeder.
Kullanım: python download_data.py
"""
import json
import os
import ssl
import sys
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "mcc_mnc_list.json")

SOURCE_URL = (
    "https://raw.githubusercontent.com/pbakondy/mcc-mnc-list/master/mcc-mnc-list.json"
)


def download():
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"İndiriliyor: {SOURCE_URL}")
    ctx = ssl._create_unverified_context()  # macOS sertifika sorunu için
    try:
        with urllib.request.urlopen(SOURCE_URL, timeout=30, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as exc:
        print(f"[HATA] İndirme başarısız: {exc}", file=sys.stderr)
        sys.exit(1)

    # Validate JSON
    try:
        records = json.loads(raw)
        assert isinstance(records, list), "Beklenen format: JSON array"
    except (json.JSONDecodeError, AssertionError) as exc:
        print(f"[HATA] JSON ayrıştırma hatası: {exc}", file=sys.stderr)
        sys.exit(1)

    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        fh.write(raw)

    print(f"✅ {len(records)} operatör kaydı indirildi → {DATA_FILE}")


if __name__ == "__main__":
    download()
