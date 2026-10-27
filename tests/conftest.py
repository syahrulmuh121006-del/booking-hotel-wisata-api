from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app

PREFIX = get_settings().api_prefix


@pytest.fixture
def client():
    """TestClient dengan database in-memory baru untuk tiap test (terisolasi)."""
    return TestClient(create_app(seed=False))


@pytest.fixture
def staf():
    return {"X-API-Key": get_settings().kunci_staf}


@pytest.fixture
def admin():
    return {"X-API-Key": get_settings().kunci_admin}


def hotel_payload(**override):
    data = {
        "nama": "Hotel Pantai Losari",
        "kota": "Makassar",
        "bintang": 4,
        "alamat": "Jl. Penghibur No. 10, Makassar",
        "fasilitas": ["wifi", "kolam renang"],
    }
    data.update(override)
    return data


def kamar_payload(**override):
    data = {"tipe": "deluxe", "harga_per_malam": 750000, "kapasitas": 2, "jumlah_unit": 2}
    data.update(override)
    return data


def destinasi_payload(**override):
    data = {
        "nama": "Rammang-Rammang",
        "kategori": "bahari",
        "kota": "Maros",
        "deskripsi": "Kawasan karst dengan susur sungai dan pemandangan batu kapur.",
        "harga_tiket": 25000,
        "kuota_harian": 5,
    }
    data.update(override)
    return data


def booking_hotel_payload(hotel_id, kamar_id, **override):
    data = {
        "hotel_id": hotel_id,
        "kamar_id": kamar_id,
        "nama_tamu": "Andi Baso",
        "email": "andi@example.com",
        "tanggal_checkin": (date.today() + timedelta(days=7)).isoformat(),
        "tanggal_checkout": (date.today() + timedelta(days=9)).isoformat(),
        "jumlah_tamu": 2,
        "jumlah_kamar": 1,
    }
    data.update(override)
    return data


def booking_wisata_payload(destinasi_id, **override):
    data = {
        "destinasi_id": destinasi_id,
        "nama_pemesan": "Siti Aisyah",
        "email": "siti@example.com",
        "tanggal_kunjungan": (date.today() + timedelta(days=5)).isoformat(),
        "jumlah_tiket": 3,
    }
    data.update(override)
    return data


@pytest.fixture
def hotel(client, staf):
    res = client.post(f"{PREFIX}/hotels", json=hotel_payload(), headers=staf)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def kamar(client, staf, hotel):
    res = client.post(f"{PREFIX}/hotels/{hotel['id']}/rooms", json=kamar_payload(), headers=staf)
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def destinasi(client, staf):
    res = client.post(f"{PREFIX}/destinations", json=destinasi_payload(), headers=staf)
    assert res.status_code == 201
    return res.json()
