# 📡 MSISDN Lookup API

Verilen telefon numaralarına (MSISDN) göre **ülke**, **operatör**, **MCC**, **MNC**, **hat türü** ve coğrafi bilgileri anında döndüren yüksek performanslı bir REST API.

**Python · FastAPI · port 8090**

---

## ✨ Özellikler

- 🚀 **Yüksek performans** — 11.000+ lookup/sn (bulk), ~1ms/istek (single)
- 🌍 **231 ülke, 3.094 operatör** desteği
- 📦 **Bulk endpoint** — tek istekle 10.000'e kadar MSISDN
- 🔢 **Esnek format** — `+905321234567`, `905321234567`, `00905321234567` hepsi kabul edilir
- ✅ **Validasyon** — Google libphonenumber ile RFC standardı doğrulama
- 💾 **Tamamen offline** — Tüm veri sunucu başlangıcında RAM'e yüklenir, dış servis bağımlılığı yok
- 📖 **Swagger UI** — `/docs` adresinde otomatik API dokümantasyonu

---

## 📋 Döndürülen Alanlar

| Alan | Tip | Açıklama |
|---|---|---|
| `msisdn` | string | Alınan ham numara |
| `e164` | string | E.164 standardında formatlanmış numara |
| `valid` | bool | Numaranın geçerli olup olmadığı |
| `possible` | bool | Numaranın mümkün uzunlukta olup olmadığı |
| `number_type` | string | `MOBILE`, `FIXED_LINE`, `FIXED_LINE_OR_MOBILE`, `VOIP`, vb. |
| `country_code` | int | Uluslararası telefon alan kodu (örn. `90`) |
| `country_iso` | string | ISO 3166-1 alfa-2 ülke kodu (örn. `TR`) |
| `country_name` | string | Ülke adı (İngilizce) |
| `mcc` | string | Mobile Country Code — 3 haneli |
| `mnc` | string | Mobile Network Code — 2-3 haneli |
| `brand` | string | Operatör marka adı (örn. `Turkcell`) |
| `operator` | string | Operatörün resmi tam adı |
| `status` | string | `Operational`, `Not operational`, `Unknown` |
| `bands` | string | Desteklenen frekans bantları |
| `geo_description` | string | Coğrafi konum açıklaması |
| `error` | string \| null | Hata mesajı (geçersiz numara için) |

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.9+
- pip

### 1. Repoyu klonla

```bash
git clone https://github.com/kullanici/msisdn-lookup-api.git
cd msisdn-lookup-api
```

### 2. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

### 3. MCC/MNC veritabanını indir

```bash
python download_data.py
```

> Alternatif olarak `data/mcc_mnc_list.json` dosyasını elle oluşturun (bkz. [Veri Kaynağı](#veri-kaynağı)).

### 4. Sunucuyu başlat

```bash
# Tek worker (varsayılan)
python main.py

# veya start.sh ile
./start.sh

# Çoklu worker (CPU sayısına göre)
./start.sh 4

# veya uvicorn ile doğrudan
python -m uvicorn main:app --host 0.0.0.0 --port 8090 --workers 2
```

Sunucu `http://localhost:8090` adresinde çalışmaya başlar.

---

## 🔌 API Kullanımı

### GET `/lookup` — Tek MSISDN Sorgulama

**Parametreler:**

| Parametre | Zorunlu | Açıklama |
|---|---|---|
| `msisdn` | ✅ | Sorgulanacak telefon numarası |

**Örnek İstek:**

```bash
curl "http://localhost:8090/lookup?msisdn=+905321234567"
```

**Örnek Yanıt — 🇹🇷 Türkiye / Turkcell:**

```json
{
  "msisdn": "+905321234567",
  "e164": "+905321234567",
  "valid": true,
  "possible": true,
  "number_type": "MOBILE",
  "country_code": 90,
  "country_iso": "TR",
  "country_name": "Turkey",
  "mcc": "286",
  "mnc": "01",
  "brand": "Turkcell",
  "operator": "Turkcell Iletisim Hizmetleri A.S.",
  "status": "Operational",
  "bands": "GSM 900 / UMTS 900 / UMTS 2100 / LTE 800 / LTE 1800 / LTE 2100 / LTE 2600",
  "geo_description": "Turkey",
  "error": null
}
```

**Örnek Yanıt — 🇹🇷 Türkiye / Vodafone:**

```json
{
  "msisdn": "+905421234567",
  "e164": "+905421234567",
  "valid": true,
  "possible": true,
  "number_type": "MOBILE",
  "country_code": 90,
  "country_iso": "TR",
  "country_name": "Turkey",
  "mcc": "286",
  "mnc": "02",
  "brand": "Vodafone",
  "operator": "Vodafone Turkey",
  "status": "Operational",
  "bands": "GSM 900 / UMTS 2100 / LTE 800 / LTE 900 / LTE 1800 / LTE 2100 / LTE 2600 / TD-LTE 2600",
  "geo_description": "Turkey",
  "error": null
}
```

**Örnek Yanıt — 🇩🇪 Almanya / Vodafone:**

```json
{
  "msisdn": "+4915212345678",
  "e164": "+4915212345678",
  "valid": true,
  "possible": true,
  "number_type": "MOBILE",
  "country_code": 49,
  "country_iso": "DE",
  "country_name": "Germany",
  "mcc": "262",
  "mnc": "02",
  "brand": "Vodafone",
  "operator": "Vodafone D2 GmbH",
  "status": "Operational",
  "bands": "GSM 900 / LTE 700 / LTE 800 / LTE 900 / LTE 1800 / LTE 2100 / LTE 2600 / 5G 700 / 5G 1800 / 5G 3500",
  "geo_description": "Germany",
  "error": null
}
```

**Örnek Yanıt — 🇫🇷 Fransa / SFR:**

```json
{
  "msisdn": "+33612345678",
  "e164": "+33612345678",
  "valid": true,
  "possible": true,
  "number_type": "MOBILE",
  "country_code": 33,
  "country_iso": "FR",
  "country_name": "France",
  "mcc": "208",
  "mnc": "13",
  "brand": "SFR",
  "operator": "Altice",
  "status": "Operational",
  "bands": "GSM 900 / UMTS 900 / UMTS 2100 / LTE 800 / LTE 1800 / LTE 2100 / LTE 2600 / 5G 3500",
  "geo_description": "France",
  "error": null
}
```

**Örnek Yanıt — 🇷🇺 Rusya / MTS:**

```json
{
  "msisdn": "+79161234567",
  "e164": "+79161234567",
  "valid": true,
  "possible": true,
  "number_type": "MOBILE",
  "country_code": 7,
  "country_iso": "RU",
  "country_name": "Russian Federation",
  "mcc": "250",
  "mnc": "01",
  "brand": "MTS",
  "operator": "Mobile TeleSystems",
  "status": "Operational",
  "bands": "GSM 900 / GSM 1800 / UMTS 900 / UMTS 2100 / LTE 800 / LTE 900 / LTE 1800 / LTE 2100 / LTE 2600 / TD-LTE 2600 / 5G 4700",
  "geo_description": "Russia",
  "error": null
}
```

**Örnek Yanıt — 🇨🇳 Çin / China Mobile:**

```json
{
  "msisdn": "+8613800138000",
  "e164": "+8613800138000",
  "valid": true,
  "possible": true,
  "number_type": "MOBILE",
  "country_code": 86,
  "country_iso": "CN",
  "country_name": "China",
  "mcc": "460",
  "mnc": "08",
  "brand": "China Mobile",
  "operator": "China Mobile",
  "status": "Unknown",
  "bands": "Unknown",
  "geo_description": "Beijing",
  "error": null
}
```

**Örnek Yanıt — 🇺🇸 ABD (San Francisco):**

```json
{
  "msisdn": "+14155552671",
  "e164": "+14155552671",
  "valid": true,
  "possible": true,
  "number_type": "FIXED_LINE_OR_MOBILE",
  "country_code": 1,
  "country_iso": "US",
  "country_name": "United States of America",
  "mcc": "316",
  "mnc": "010",
  "brand": "Nextel",
  "operator": "Nextel Communications",
  "status": "Not operational",
  "bands": "iDEN 800",
  "geo_description": "San Francisco, CA",
  "error": null
}
```

**Örnek Yanıt — 🇯🇵 Japonya / KDDI:**

```json
{
  "msisdn": "+819012345678",
  "e164": "+819012345678",
  "valid": true,
  "possible": true,
  "number_type": "MOBILE",
  "country_code": 81,
  "country_iso": "JP",
  "country_name": "Japan",
  "mcc": "441",
  "mnc": "00",
  "brand": "KDDI",
  "operator": "Wireless City Planning Inc.",
  "status": "Operational",
  "bands": "TD-LTE 2500",
  "geo_description": "Japan",
  "error": null
}
```

**Örnek Yanıt — ❌ Geçersiz Numara (HTTP 400):**

```bash
curl "http://localhost:8090/lookup?msisdn=invalid_number"
```

```json
{
  "detail": "Cannot parse MSISDN: (1) The string supplied did not seem to be a phone number."
}
```

---

### POST `/bulk` — Çoklu MSISDN Sorgulama

Tek bir istekle 10.000'e kadar MSISDN sorgulayabilirsiniz.

**Request Body:**

```json
{
  "msisdns": ["<msisdn1>", "<msisdn2>", "..."]
}
```

**Örnek İstek:**

```bash
curl -X POST "http://localhost:8090/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "msisdns": [
      "+905321234567",
      "+905059876543",
      "+447911123456",
      "+14155552671",
      "bad_num"
    ]
  }'
```

**Örnek Yanıt:**

```json
[
  {
    "msisdn": "+905321234567",
    "e164": "+905321234567",
    "valid": true,
    "possible": true,
    "number_type": "MOBILE",
    "country_code": 90,
    "country_iso": "TR",
    "country_name": "Turkey",
    "mcc": "286",
    "mnc": "01",
    "brand": "Turkcell",
    "operator": "Turkcell Iletisim Hizmetleri A.S.",
    "status": "Operational",
    "bands": "GSM 900 / UMTS 900 / UMTS 2100 / LTE 800 / LTE 1800 / LTE 2100 / LTE 2600",
    "geo_description": "Turkey"
  },
  {
    "msisdn": "+905059876543",
    "e164": "+905059876543",
    "valid": true,
    "possible": true,
    "number_type": "MOBILE",
    "country_code": 90,
    "country_iso": "TR",
    "country_name": "Turkey",
    "mcc": "286",
    "mnc": "01",
    "brand": "Turkcell",
    "operator": "Turkcell Iletisim Hizmetleri A.S.",
    "status": "Operational",
    "bands": "GSM 900 / UMTS 900 / UMTS 2100 / LTE 800 / LTE 1800 / LTE 2100 / LTE 2600",
    "geo_description": "Turkey"
  },
  {
    "msisdn": "+447911123456",
    "e164": "+447911123456",
    "valid": true,
    "possible": true,
    "number_type": "MOBILE",
    "country_code": 44,
    "country_iso": "GG",
    "country_name": "Guernsey (United Kingdom)",
    "mcc": "234",
    "mnc": "50",
    "brand": "JT",
    "operator": "JT Group Limited",
    "status": "Operational",
    "bands": "GSM 1800 / UMTS 900 / UMTS 2100 / LTE 800 / LTE 1800 / LTE 2600",
    "geo_description": "Guernsey"
  },
  {
    "msisdn": "+14155552671",
    "e164": "+14155552671",
    "valid": true,
    "possible": true,
    "number_type": "FIXED_LINE_OR_MOBILE",
    "country_code": 1,
    "country_iso": "US",
    "country_name": "United States of America",
    "mcc": "316",
    "mnc": "010",
    "brand": "Nextel",
    "operator": "Nextel Communications",
    "status": "Not operational",
    "bands": "iDEN 800",
    "geo_description": "San Francisco, CA"
  },
  {
    "msisdn": "bad_num",
    "valid": false,
    "possible": false,
    "error": "Cannot parse MSISDN: (1) The string supplied did not seem to be a phone number."
  }
]
```

> ℹ️ Hatalı numara içeren satirlar `"error"` alanıyla işaretlenir; diğer sonuçlar etkilenmez.

---

### GET `/health` — Sağlık Kontrolü

```bash
curl "http://localhost:8090/health"
```

```json
{
  "status": "ok",
  "mcc_mnc_records_indexed": 2988,
  "countries_indexed": 231,
  "brand_index_size": 2268
}
```

---

### GET `/docs` — Swagger UI

Tarayıcıdan `http://localhost:8090/docs` adresine giderek interaktif API dokümantasyonuna ulaşabilirsiniz.

---

## 📂 Proje Yapısı

```
msisdn-lookup-api/
├── main.py               # FastAPI uygulaması & lookup engine
├── download_data.py      # MCC/MNC veritabanını indir
├── requirements.txt      # Python bağımlılıkları
├── start.sh              # Sunucu başlatma scripti
└── data/
    └── mcc_mnc_list.json # MCC/MNC veritabanı (3094 kayıt)
```

---

## ⚡ Performans

Test ortamı: Apple M-series, Python 3.14, tek worker (uvicorn)

| Senaryo | Sonuç |
|---|---|
| **Bulk — 1.000 MSISDN** | ~87ms → **11.463 lookup/sn** |
| **Single endpoint** | ~1ms/istek → **~970 req/sn** |
| **Startup süresi** | ~9ms (RAM'e yükleme) |
| **RAM kullanımı** | ~45 MB (3094 kayıt + index) |

### Milyonlarca Sorgu İçin

Çok core kullanmak için `gunicorn` ile birden fazla worker başlatın:

```bash
pip install gunicorn
gunicorn main:app -w 8 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8090
```

---

## 🔢 MSISDN Format Desteği

API aşağıdaki tüm formatlarda numara kabul eder:

| Format | Örnek |
|---|---|
| E.164 (+ ile) | `+905321234567` |
| Ülke kodu (+ olmadan) | `905321234567` |
| 00 ön eki | `00905321234567` |
| Boşluk/tire ile | `+90 532 123 45 67` |

---

## 🧩 Mimarisi

```
HTTP İsteği
    │
    ▼
FastAPI (async endpoint)
    │
    ▼
phonenumbers.parse()          ← Google libphonenumber
    │
    ├── region_code_for_number()   → ISO kodu (TR, DE, FR...)
    ├── carrier.name_for_number()  → Operatör adı (Turkcell...)
    ├── geocoder.description()     → Coğrafi açıklama
    └── number_type()              → MOBILE / FIXED_LINE / ...
    │
    ▼
In-Memory Hash Lookup
    │
    ├── ISO → MCC eşlemesi        → O(1)
    └── MCC:ISO:Brand index       → O(1)
    │
    ▼
JSON Yanıt (orjson ile serialize)
```

### Lookup Stratejisi

1. **Tam eşleşme:** `phonenumbers` kütüphanesinin döndürdüğü carrier adı, MCC/MNC veritabanındaki brand ile normalize edilerek karşılaştırılır.
2. **Kısmi eşleşme:** Brand adı, carrier adını içeriyorsa ya da tam tersi ise `Operational` kayıt seçilir.
3. **Fallback:** Carrier eşleşmesi bulunamazsa, ülkeye ait ilk `Operational` operatör döndürülür.

---

## ⚠️ Kısıtlamalar ve Önemli Notlar

> **MNP (Numara Taşıma) desteği yoktur.**
>
> Bu API, statik prefix tabanlı eşleştirme yapar. Eğer bir abone numarasını başka bir operatöre taşımışsa (Mobile Number Portability), API orijinal operatörü döndürebilir. Gerçek zamanlı ve doğru operatör tespiti için HLR (Home Location Register) lookup hizmetleri gerekir.

Kullanım senaryolarına göre doğruluk beklentisi:

| Senaryo | Doğruluk |
|---|---|
| Ülke tespiti | ✅ ~%99.9 |
| MCC tespiti | ✅ ~%99 |
| Numara tipi (MOBILE vs FIXED) | ✅ ~%95 |
| Operatör / MNC (taşıma olmadan) | ✅ ~%80-90 |
| Operatör / MNC (taşımalı hatlar) | ⚠️ Güvenilmez |

---

## 📡 Veri Kaynağı

Operatör veritabanı [pbakondy/mcc-mnc-list](https://github.com/pbakondy/mcc-mnc-list) kaynağından alınmaktadır (Wikipedia tabanlı, topluluk tarafından güncellenmektedir). Veriyi güncellemek için:

```bash
python download_data.py
```

---

## 🐍 Python'dan Kullanım Örneği

```python
import requests

BASE = "http://localhost:8090"

# Tek sorgulama
r = requests.get(f"{BASE}/lookup", params={"msisdn": "+905321234567"})
data = r.json()
print(f"Ülke: {data['country_name']}, Operatör: {data['brand']}, MCC: {data['mcc']}, MNC: {data['mnc']}")
# → Ülke: Turkey, Operatör: Turkcell, MCC: 286, MNC: 01

# Bulk sorgulama
msisdns = ["+905321234567", "+905421234567", "+4915212345678", "+33612345678"]
r = requests.post(f"{BASE}/bulk", json={"msisdns": msisdns})
for item in r.json():
    print(f"{item['msisdn']:20} → {item['country_iso']} / {item['brand']} (MCC:{item['mcc']} MNC:{item['mnc']})")
```

**Çıktı:**
```
+905321234567        → TR / Turkcell (MCC:286 MNC:01)
+905421234567        → TR / Vodafone (MCC:286 MNC:02)
+4915212345678       → DE / Vodafone (MCC:262 MNC:02)
+33612345678         → FR / SFR (MCC:208 MNC:13)
```

---

## 🛠️ Bağımlılıklar

| Paket | Versiyon | Açıklama |
|---|---|---|
| `fastapi` | ≥0.100 | Web framework |
| `uvicorn` | ≥0.22 | ASGI sunucu |
| `phonenumbers` | ≥8.13 | Google libphonenumber Python portu |
| `orjson` | ≥3.9 | Hızlı JSON serializasyonu |

---

## 📄 Lisans

MIT License. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🤝 Katkıda Bulunma

Pull request ve issue'lar memnuniyetle karşılanır. Yeni bir özellik eklemeden önce bir issue açmanız önerilir.
