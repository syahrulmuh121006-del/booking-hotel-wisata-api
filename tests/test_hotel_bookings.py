from datetime import date, timedelta

from tests.conftest import PREFIX, booking_hotel_payload


def _buat(client, hotel, kamar, **override):
    return client.post(
        f"{PREFIX}/hotel-bookings", json=booking_hotel_payload(hotel["id"], kamar["id"], **override)
    )


def test_booking_hotel_berhasil_dan_total_harga_benar(client, hotel, kamar):
    res = _buat(client, hotel, kamar)
    assert res.status_code == 201
    data = res.json()
    assert data["kode_booking"] == "BKH-0001"
    assert data["jumlah_malam"] == 2
    assert data["total_harga"] == 2 * 750000
    assert data["status"] == "dikonfirmasi"


def test_total_harga_dikali_jumlah_kamar(client, hotel, kamar):
    res = _buat(client, hotel, kamar, jumlah_kamar=2, jumlah_tamu=4)
    assert res.status_code == 201
    assert res.json()["total_harga"] == 2 * 750000 * 2


def test_checkout_sebelum_checkin_422(client, hotel, kamar):
    res = _buat(
        client,
        hotel,
        kamar,
        tanggal_checkin=(date.today() + timedelta(days=9)).isoformat(),
        tanggal_checkout=(date.today() + timedelta(days=7)).isoformat(),
    )
    assert res.status_code == 422
    assert res.json()["code"] == "VALIDATION_ERROR"


def test_checkin_di_masa_lalu_422(client, hotel, kamar):
    res = _buat(client, hotel, kamar, tanggal_checkin=(date.today() - timedelta(days=1)).isoformat())
    assert res.status_code == 422


def test_email_tidak_valid_422(client, hotel, kamar):
    assert _buat(client, hotel, kamar, email="bukan-email").status_code == 422


def test_hotel_tidak_ada_404(client, kamar):
    res = client.post(f"{PREFIX}/hotel-bookings", json=booking_hotel_payload(999, kamar["id"]))
    assert res.status_code == 404


def test_kamar_milik_hotel_lain_404(client, staf, hotel, kamar):
    from tests.conftest import hotel_payload

    hotel2 = client.post(
        f"{PREFIX}/hotels", json=hotel_payload(nama="Hotel Lain", kota="Gowa"), headers=staf
    ).json()
    res = client.post(
        f"{PREFIX}/hotel-bookings", json=booking_hotel_payload(hotel2["id"], kamar["id"])
    )
    assert res.status_code == 404


def test_jumlah_tamu_melebihi_kapasitas_400(client, hotel, kamar):
    res = _buat(client, hotel, kamar, jumlah_tamu=5)
    assert res.status_code == 400
    assert res.json()["code"] == "BUSINESS_RULE_VIOLATION"


def test_hotel_nonaktif_400(client, staf, hotel, kamar):
    client.patch(f"{PREFIX}/hotels/{hotel['id']}", json={"aktif": False}, headers=staf)
    assert _buat(client, hotel, kamar).status_code == 400


def test_overbooking_409_dan_bebas_lagi_setelah_dibatalkan(client, staf, hotel, kamar):
    pertama = _buat(client, hotel, kamar, jumlah_kamar=2, jumlah_tamu=4)
    assert pertama.status_code == 201
    kedua = _buat(client, hotel, kamar)
    assert kedua.status_code == 409
    assert kedua.json()["code"] == "CONFLICT"

    batal = client.patch(
        f"{PREFIX}/hotel-bookings/{pertama.json()['id']}", json={"status": "dibatalkan"}, headers=staf
    )
    assert batal.status_code == 200
    assert _buat(client, hotel, kamar).status_code == 201


def test_tanggal_tidak_beririsan_tetap_tersedia(client, hotel, kamar):
    assert _buat(client, hotel, kamar, jumlah_kamar=2, jumlah_tamu=4).status_code == 201
    # check-in tepat pada hari check-out booking sebelumnya -> tidak beririsan
    res = _buat(
        client,
        hotel,
        kamar,
        tanggal_checkin=(date.today() + timedelta(days=9)).isoformat(),
        tanggal_checkout=(date.today() + timedelta(days=10)).isoformat(),
    )
    assert res.status_code == 201


def test_daftar_booking_tanpa_key_401(client):
    assert client.get(f"{PREFIX}/hotel-bookings").status_code == 401


def test_daftar_dan_filter_status(client, staf, hotel, kamar):
    b = _buat(client, hotel, kamar).json()
    client.patch(f"{PREFIX}/hotel-bookings/{b['id']}", json={"status": "selesai"}, headers=staf)
    _buat(client, hotel, kamar)
    semua = client.get(f"{PREFIX}/hotel-bookings", headers=staf).json()
    assert semua["total"] == 2
    selesai = client.get(f"{PREFIX}/hotel-bookings", params={"status": "selesai"}, headers=staf).json()
    assert selesai["total"] == 1


def test_detail_booking_dan_404(client, staf, hotel, kamar):
    b = _buat(client, hotel, kamar).json()
    assert client.get(f"{PREFIX}/hotel-bookings/{b['id']}", headers=staf).status_code == 200
    assert client.get(f"{PREFIX}/hotel-bookings/999", headers=staf).status_code == 404


def test_batalkan_dua_kali_409(client, staf, hotel, kamar):
    b = _buat(client, hotel, kamar).json()
    url = f"{PREFIX}/hotel-bookings/{b['id']}"
    assert client.patch(url, json={"status": "dibatalkan"}, headers=staf).status_code == 200
    assert client.patch(url, json={"status": "dibatalkan"}, headers=staf).status_code == 409


def test_status_tidak_dikenal_422(client, staf, hotel, kamar):
    b = _buat(client, hotel, kamar).json()
    res = client.patch(f"{PREFIX}/hotel-bookings/{b['id']}", json={"status": "ngambek"}, headers=staf)
    assert res.status_code == 422


def test_hapus_booking_rbac(client, staf, admin, hotel, kamar):
    b = _buat(client, hotel, kamar).json()
    url = f"{PREFIX}/hotel-bookings/{b['id']}"
    assert client.delete(url, headers=staf).status_code == 403
    assert client.delete(url, headers=admin).status_code == 204


def test_hapus_hotel_dengan_booking_aktif_409(client, admin, hotel, kamar):
    _buat(client, hotel, kamar)
    res = client.delete(f"{PREFIX}/hotels/{hotel['id']}", headers=admin)
    assert res.status_code == 409


def test_hapus_kamar_dengan_booking_aktif_409(client, admin, hotel, kamar):
    _buat(client, hotel, kamar)
    res = client.delete(f"{PREFIX}/hotels/{hotel['id']}/rooms/{kamar['id']}", headers=admin)
    assert res.status_code == 409
