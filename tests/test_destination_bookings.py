from datetime import date, timedelta

from tests.conftest import PREFIX, booking_wisata_payload


def _pesan(client, destinasi, **override):
    return client.post(
        f"{PREFIX}/destination-bookings", json=booking_wisata_payload(destinasi["id"], **override)
    )


def test_booking_wisata_berhasil_dan_total_harga(client, destinasi):
    res = _pesan(client, destinasi)
    assert res.status_code == 201
    data = res.json()
    assert data["kode_booking"] == "BKW-0001"
    assert data["total_harga"] == 3 * 25000
    assert data["status"] == "dikonfirmasi"


def test_destinasi_tidak_ada_404(client):
    res = client.post(f"{PREFIX}/destination-bookings", json=booking_wisata_payload(77))
    assert res.status_code == 404


def test_tanggal_kunjungan_masa_lalu_422(client, destinasi):
    res = _pesan(client, destinasi, tanggal_kunjungan=(date.today() - timedelta(days=1)).isoformat())
    assert res.status_code == 422


def test_jumlah_tiket_nol_422(client, destinasi):
    assert _pesan(client, destinasi, jumlah_tiket=0).status_code == 422


def test_kuota_harian_terlampaui_409(client, destinasi):
    assert _pesan(client, destinasi, jumlah_tiket=3).status_code == 201
    res = _pesan(client, destinasi, jumlah_tiket=3)  # kuota 5, sudah terpakai 3
    assert res.status_code == 409
    assert "Sisa kuota" in res.json()["message"]


def test_kuota_dihitung_per_tanggal(client, destinasi):
    assert _pesan(client, destinasi, jumlah_tiket=5).status_code == 201
    besok = (date.today() + timedelta(days=6)).isoformat()
    assert _pesan(client, destinasi, jumlah_tiket=5, tanggal_kunjungan=besok).status_code == 201


def test_pembatalan_mengembalikan_kuota(client, staf, destinasi):
    b = _pesan(client, destinasi, jumlah_tiket=5).json()
    assert _pesan(client, destinasi, jumlah_tiket=1).status_code == 409
    client.patch(f"{PREFIX}/destination-bookings/{b['id']}", json={"status": "dibatalkan"}, headers=staf)
    assert _pesan(client, destinasi, jumlah_tiket=1).status_code == 201


def test_destinasi_nonaktif_400(client, staf, destinasi):
    client.patch(f"{PREFIX}/destinations/{destinasi['id']}", json={"aktif": False}, headers=staf)
    assert _pesan(client, destinasi).status_code == 400


def test_daftar_booking_wisata_butuh_key(client, staf, destinasi):
    _pesan(client, destinasi)
    assert client.get(f"{PREFIX}/destination-bookings").status_code == 401
    res = client.get(f"{PREFIX}/destination-bookings", headers=staf)
    assert res.status_code == 200
    assert res.json()["total"] == 1


def test_ubah_status_dan_transisi_tidak_valid(client, staf, destinasi):
    b = _pesan(client, destinasi).json()
    url = f"{PREFIX}/destination-bookings/{b['id']}"
    assert client.patch(url, json={"status": "selesai"}, headers=staf).json()["status"] == "selesai"
    assert client.patch(url, json={"status": "dibatalkan"}, headers=staf).status_code == 409


def test_hapus_destinasi_dengan_booking_aktif_409(client, admin, destinasi):
    _pesan(client, destinasi)
    assert client.delete(f"{PREFIX}/destinations/{destinasi['id']}", headers=admin).status_code == 409


def test_hapus_booking_wisata_rbac(client, staf, admin, destinasi):
    b = _pesan(client, destinasi).json()
    url = f"{PREFIX}/destination-bookings/{b['id']}"
    assert client.delete(url, headers=staf).status_code == 403
    assert client.delete(url, headers=admin).status_code == 204
    assert client.get(url, headers=admin).status_code == 404
