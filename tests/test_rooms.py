from tests.conftest import PREFIX, kamar_payload


def test_tambah_kamar_berhasil(client, staf, hotel):
    res = client.post(f"{PREFIX}/hotels/{hotel['id']}/rooms", json=kamar_payload(), headers=staf)
    assert res.status_code == 201
    data = res.json()
    assert data["hotel_id"] == hotel["id"]
    assert data["tipe"] == "deluxe"


def test_tambah_kamar_hotel_tidak_ada_404(client, staf):
    res = client.post(f"{PREFIX}/hotels/999/rooms", json=kamar_payload(), headers=staf)
    assert res.status_code == 404


def test_harga_kamar_terlalu_murah_422(client, staf, hotel):
    res = client.post(
        f"{PREFIX}/hotels/{hotel['id']}/rooms", json=kamar_payload(harga_per_malam=1000), headers=staf
    )
    assert res.status_code == 422


def test_tipe_kamar_tidak_dikenal_422(client, staf, hotel):
    res = client.post(
        f"{PREFIX}/hotels/{hotel['id']}/rooms", json=kamar_payload(tipe="presidential"), headers=staf
    )
    assert res.status_code == 422


def test_daftar_dan_detail_kamar_publik(client, hotel, kamar):
    daftar = client.get(f"{PREFIX}/hotels/{hotel['id']}/rooms")
    assert daftar.status_code == 200
    assert len(daftar.json()) == 1
    detail = client.get(f"{PREFIX}/hotels/{hotel['id']}/rooms/{kamar['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == kamar["id"]


def test_ubah_kamar(client, staf, hotel, kamar):
    res = client.patch(
        f"{PREFIX}/hotels/{hotel['id']}/rooms/{kamar['id']}", json={"harga_per_malam": 900000}, headers=staf
    )
    assert res.status_code == 200
    assert res.json()["harga_per_malam"] == 900000


def test_hapus_kamar_hanya_admin(client, staf, admin, hotel, kamar):
    url = f"{PREFIX}/hotels/{hotel['id']}/rooms/{kamar['id']}"
    assert client.delete(url, headers=staf).status_code == 403
    assert client.delete(url, headers=admin).status_code == 204
    assert client.get(url).status_code == 404
