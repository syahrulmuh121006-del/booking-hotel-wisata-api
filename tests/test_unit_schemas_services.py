"""Unit test murni (tanpa HTTP): schema, repository, aturan status, pagination, dependency override."""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.errors import ConflictError
from app.dependencies.auth import Pengguna, Peran, verifikasi_api_key
from app.main import create_app
from app.repositories.memory import InMemoryRepository
from app.schemas.booking import BookingHotelCreate, BookingWisataCreate, StatusBooking
from app.schemas.common import paginate
from app.schemas.hotel import HotelCreate, HotelUpdate
from app.services.status_rules import validasi_transisi
from tests.conftest import PREFIX, hotel_payload


def _besok(n=1):
    return date.today() + timedelta(days=n)


def test_schema_hotel_menolak_bintang_nol():
    with pytest.raises(ValidationError):
        HotelCreate(**hotel_payload(bintang=0))


def test_schema_hotel_strip_whitespace():
    h = HotelCreate(**hotel_payload(nama="  Hotel Baru  "))
    assert h.nama == "Hotel Baru"


def test_schema_hotel_update_semua_opsional():
    assert HotelUpdate().model_dump(exclude_unset=True) == {}


def test_schema_booking_hotel_checkout_harus_setelah_checkin():
    with pytest.raises(ValidationError):
        BookingHotelCreate(
            hotel_id=1, kamar_id=1, nama_tamu="Budi Santoso", email="b@x.com",
            tanggal_checkin=_besok(3), tanggal_checkout=_besok(3), jumlah_tamu=1,
        )


def test_schema_booking_hotel_maksimal_30_malam():
    with pytest.raises(ValidationError):
        BookingHotelCreate(
            hotel_id=1, kamar_id=1, nama_tamu="Budi Santoso", email="b@x.com",
            tanggal_checkin=_besok(1), tanggal_checkout=_besok(40), jumlah_tamu=1,
        )


def test_schema_booking_hotel_valid_default_jumlah_kamar():
    b = BookingHotelCreate(
        hotel_id=1, kamar_id=1, nama_tamu="Budi Santoso", email="b@x.com",
        tanggal_checkin=_besok(1), tanggal_checkout=_besok(2), jumlah_tamu=1,
    )
    assert b.jumlah_kamar == 1


def test_schema_booking_wisata_menolak_tanggal_lampau():
    with pytest.raises(ValidationError):
        BookingWisataCreate(
            destinasi_id=1, nama_pemesan="Siti Aisyah", email="s@x.com",
            tanggal_kunjungan=_besok(-2), jumlah_tiket=1,
        )


def test_paginate_halaman_terakhir_sebagian():
    hasil = paginate(list(range(5)), halaman=3, per_halaman=2)
    assert hasil == {"data": [4], "total": 5, "halaman": 3, "per_halaman": 2}


def test_paginate_halaman_di_luar_jangkauan_kosong():
    assert paginate([1, 2], halaman=9, per_halaman=10)["data"] == []


def test_repository_crud():
    repo = InMemoryRepository()
    a = repo.add({"nama": "A"})
    b = repo.add({"nama": "B"})
    assert (a["id"], b["id"]) == (1, 2)
    assert repo.get(1)["nama"] == "A"
    assert repo.update(1, {"nama": "A2"})["nama"] == "A2"
    assert [i["nama"] for i in repo.list(lambda i: i["nama"] == "B")] == ["B"]
    assert repo.delete(2) is True
    assert repo.delete(2) is False
    assert repo.get(2) is None
    assert repo.update(99, {}) is None


def test_repository_mengembalikan_salinan():
    repo = InMemoryRepository()
    repo.add({"nama": "A"})
    repo.get(1)["nama"] = "DIUBAH"
    assert repo.get(1)["nama"] == "A"


def test_transisi_status_valid():
    validasi_transisi(StatusBooking.DIKONFIRMASI, StatusBooking.DIBATALKAN)
    validasi_transisi(StatusBooking.DIKONFIRMASI, StatusBooking.SELESAI)


@pytest.mark.parametrize("awal", [StatusBooking.DIBATALKAN, StatusBooking.SELESAI])
def test_transisi_status_dari_status_akhir_ditolak(awal):
    with pytest.raises(ConflictError):
        validasi_transisi(awal, StatusBooking.DIKONFIRMASI)


def test_dependency_override_melewati_autentikasi():
    app = create_app(seed=False)
    app.dependency_overrides[verifikasi_api_key] = lambda: Pengguna(peran=Peran.ADMIN)
    client = TestClient(app)
    res = client.post(f"{PREFIX}/hotels", json=hotel_payload())  # tanpa header X-API-Key
    assert res.status_code == 201
    app.dependency_overrides.clear()
    assert client.post(f"{PREFIX}/hotels", json=hotel_payload(nama="Hotel Lain")).status_code == 401


def test_instance_app_terisolasi_satu_sama_lain():
    app1, app2 = create_app(seed=False), create_app(seed=False)
    assert app1.state.db is not app2.state.db


def test_seed_mengisi_data_contoh():
    app = create_app(seed=True)
    client = TestClient(app)
    assert client.get(f"{PREFIX}/hotels").json()["total"] >= 1
    assert client.get(f"{PREFIX}/destinations").json()["total"] >= 2
