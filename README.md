# API Booking Hotel & Destinasi Wisata (Sulawesi Selatan)

Tugas Pemrograman Lanjut Pekan 07 — REST API dengan **FastAPI + Pydantic V2**.

Memenuhi ketentuan tugas:

| Ketentuan | Implementasi |
|---|---|
| Modular | `routers/` → `services/` → `repositories/`, plus `schemas/`, `dependencies/`, `core/` |
| Contract data | DTO Pydantic V2 (`Create` / `Update` / `Response`) + validator kustom di `app/schemas/` |
| Unit test | `pytest` + `TestClient`, **80+ test** (minimal 15) di `tests/` |
| Git | Riwayat commit bertahap + CI GitHub Actions (`.github/workflows/ci.yml`) |

Skema API ini dirancang khusus: domain **pemesanan hotel + tiket destinasi wisata**, dengan field berbahasa Indonesia
(`kamar`, `kuota_harian`, `jumlah_malam`, dst.), aturan bisnis ketersediaan kamar, dan kuota harian wisata.

## Struktur

```
app/
├── main.py                  # create_app(), registrasi router
├── seed.py                  # data contoh untuk server
├── core/        config.py, errors.py          # setting + penanganan error terpusat
├── dependencies/ auth.py, database.py         # X-API-Key, RBAC, injeksi DB
├── schemas/     hotel, kamar, destinasi, booking, common   # KONTRAK DATA
├── repositories/ memory.py, database.py       # penyimpanan in-memory
├── services/    *_service.py, status_rules.py # logika bisnis
└── routers/     hotels, rooms, destinations, hotel_bookings, destination_bookings
tests/
```

## Menjalankan

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Dokumentasi interaktif: <http://localhost:8000/docs> · ReDoc: `/redoc` · OpenAPI: `/openapi.json`

## Menjalankan test

```bash
pytest
```

## Autentikasi & hak akses

Kirim header `X-API-Key`. Nilai bawaan (ubah lewat env `STAF_API_KEY` / `ADMIN_API_KEY`):

- Staf: `staf-key-2026`
- Admin: `admin-key-2026`

| Aksi | Akses |
|---|---|
| `GET` katalog (hotel, kamar, destinasi) | Publik |
| `POST` booking hotel / wisata | Publik (pelanggan) |
| `POST`/`PATCH` hotel, kamar, destinasi; `GET`/`PATCH` booking | Staf atau Admin |
| `DELETE` apa pun | Admin saja |

401 = key tidak ada/salah, 403 = peran tidak cukup.

## Daftar endpoint (prefix `/api/v1`)

| Method | Path | Keterangan | Sukses |
|---|---|---|---|
| GET | `/hotels?kota=&bintang_min=&q=&halaman=&per_halaman=` | Daftar hotel | 200 |
| POST | `/hotels` | Tambah hotel | 201 |
| GET/PATCH/DELETE | `/hotels/{hotel_id}` | Detail / ubah / hapus | 200/200/204 |
| GET/POST | `/hotels/{hotel_id}/rooms` | Kamar milik hotel | 200/201 |
| GET/PATCH/DELETE | `/hotels/{hotel_id}/rooms/{kamar_id}` | Detail / ubah / hapus kamar | 200/200/204 |
| GET | `/destinations?kategori=&kota=&harga_maks=&q=` | Daftar destinasi | 200 |
| POST | `/destinations` | Tambah destinasi | 201 |
| GET/PATCH/DELETE | `/destinations/{destinasi_id}` | Detail / ubah / hapus | 200/200/204 |
| POST | `/hotel-bookings` | Booking hotel | 201 |
| GET | `/hotel-bookings?status=&hotel_id=` | Daftar booking hotel | 200 |
| GET/PATCH/DELETE | `/hotel-bookings/{id}` | Detail / ubah status / hapus | 200/200/204 |
| POST | `/destination-bookings` | Pesan tiket wisata | 201 |
| GET | `/destination-bookings?status=&destinasi_id=` | Daftar booking wisata | 200 |
| GET/PATCH/DELETE | `/destination-bookings/{id}` | Detail / ubah status / hapus | 200/200/204 |

Status code: 400 aturan bisnis dilanggar, 404 tidak ditemukan, 409 konflik (duplikat / kamar penuh / kuota habis /
transisi status tidak valid), 422 validasi skema.

## Aturan bisnis

- Booking hotel: `tanggal_checkout > tanggal_checkin`, maksimal 30 malam, check-in tidak boleh lampau.
- `jumlah_tamu` ≤ `kapasitas × jumlah_kamar` (jika tidak → 400).
- Ketersediaan: total kamar pada booking aktif yang tanggalnya beririsan + permintaan ≤ `jumlah_unit` (jika tidak → 409).
  Check-out dan check-in di hari yang sama tidak dianggap beririsan.
- `total_harga = jumlah_malam × harga_per_malam × jumlah_kamar`.
- Booking wisata: total tiket aktif per tanggal ≤ `kuota_harian` (jika tidak → 409); `total_harga = harga_tiket × jumlah_tiket`.
- Status booking: `dikonfirmasi → dibatalkan | selesai`; status akhir tidak bisa diubah lagi (409).
- Hotel/kamar/destinasi yang masih punya booking aktif tidak bisa dihapus (409).

## Format error seragam

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "path": "/api/v1/hotels",
  "message": "Data yang dikirim tidak valid.",
  "details": [{"field": "body -> bintang", "msg": "Input should be less than or equal to 5"}]
}
```

Kode: `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `BUSINESS_RULE_VIOLATION`.

## Contoh pemakaian

```bash
# tambah hotel
curl -X POST localhost:8000/api/v1/hotels -H "X-API-Key: staf-key-2026" -H "Content-Type: application/json" \
  -d '{"nama":"Hotel Pantai Losari","kota":"Makassar","bintang":4,"alamat":"Jl. Penghibur No. 10","fasilitas":["wifi"]}'

# booking hotel (publik)
curl -X POST localhost:8000/api/v1/hotel-bookings -H "Content-Type: application/json" \
  -d '{"hotel_id":1,"kamar_id":1,"nama_tamu":"Andi Baso","email":"andi@example.com","tanggal_checkin":"2030-01-10","tanggal_checkout":"2030-01-12","jumlah_tamu":2}'
```

> Catatan: data disimpan in-memory sehingga hilang saat server restart (sesuai lingkup tugas).

## Push ke GitHub

```bash
git remote add origin https://github.com/<username>/<nama-repo>.git
git branch -M main
git push -u origin main
```
