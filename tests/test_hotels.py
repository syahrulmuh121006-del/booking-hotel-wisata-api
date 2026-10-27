from tests.conftest import PREFIX, hotel_payload


def test_tambah_hotel_berhasil(client, staf):
    res = client.post(f"{PREFIX}/hotels", json=hotel_payload(), headers=staf)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 1
    assert data["kode"] == "HTL-001"
    assert data["nama"] == "Hotel Pantai Losari"
    assert data["aktif"] is True
    assert data["fasilitas"] == ["wifi", "kolam renang"]


def test_tambah_hotel_tanpa_api_key_401(client):
    res = client.post(f"{PREFIX}/hotels", json=hotel_payload())
    assert res.status_code == 401
    assert res.json()["code"] == "UNAUTHORIZED"
    assert res.headers["www-authenticate"] == "ApiKey"


def test_tambah_hotel_api_key_salah_401(client):
    res = client.post(f"{PREFIX}/hotels", json=hotel_payload(), headers={"X-API-Key": "salah"})
    assert res.status_code == 401


def test_validasi_bintang_di_luar_rentang_422(client, staf):
    res = client.post(f"{PREFIX}/hotels", json=hotel_payload(bintang=9), headers=staf)
    assert res.status_code == 422
    body = res.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert any("bintang" in d["field"] for d in body["details"])


def test_fasilitas_dinormalisasi_dan_tanpa_duplikat(client, staf):
    res = client.post(
        f"{PREFIX}/hotels", json=hotel_payload(fasilitas=[" WiFi ", "wifi", "Gym"]), headers=staf
    )
    assert res.status_code == 201
    assert res.json()["fasilitas"] == ["wifi", "gym"]


def test_hotel_duplikat_409(client, staf, hotel):
    res = client.post(f"{PREFIX}/hotels", json=hotel_payload(nama="hotel pantai losari"), headers=staf)
    assert res.status_code == 409
    assert res.json()["code"] == "CONFLICT"


def test_daftar_hotel_publik_dengan_filter_kota(client, staf, hotel):
    client.post(
        f"{PREFIX}/hotels",
        json=hotel_payload(nama="Hotel Bukit Malino", kota="Gowa", bintang=3),
        headers=staf,
    )
    semua = client.get(f"{PREFIX}/hotels").json()
    assert semua["total"] == 2
    gowa = client.get(f"{PREFIX}/hotels", params={"kota": "gowa"}).json()
    assert gowa["total"] == 1
    assert gowa["data"][0]["nama"] == "Hotel Bukit Malino"


def test_filter_bintang_min_dan_pencarian(client, staf, hotel):
    client.post(
        f"{PREFIX}/hotels", json=hotel_payload(nama="Hotel Melati", bintang=2), headers=staf
    )
    assert client.get(f"{PREFIX}/hotels", params={"bintang_min": 4}).json()["total"] == 1
    assert client.get(f"{PREFIX}/hotels", params={"q": "melati"}).json()["total"] == 1


def test_pagination(client, staf):
    for i in range(3):
        client.post(f"{PREFIX}/hotels", json=hotel_payload(nama=f"Hotel Nomor {i}"), headers=staf)
    res = client.get(f"{PREFIX}/hotels", params={"halaman": 2, "per_halaman": 2}).json()
    assert res["total"] == 3
    assert len(res["data"]) == 1
    assert res["halaman"] == 2


def test_per_halaman_melebihi_batas_422(client):
    assert client.get(f"{PREFIX}/hotels", params={"per_halaman": 1000}).status_code == 422


def test_detail_hotel(client, hotel):
    res = client.get(f"{PREFIX}/hotels/{hotel['id']}")
    assert res.status_code == 200
    assert res.json()["kode"] == hotel["kode"]


def test_detail_hotel_tidak_ada_404(client):
    res = client.get(f"{PREFIX}/hotels/999")
    assert res.status_code == 404
    body = res.json()
    assert body["status"] == "error"
    assert body["code"] == "NOT_FOUND"
    assert body["path"] == f"{PREFIX}/hotels/999"


def test_ubah_sebagian_hotel(client, staf, hotel):
    res = client.patch(f"{PREFIX}/hotels/{hotel['id']}", json={"bintang": 5}, headers=staf)
    assert res.status_code == 200
    data = res.json()
    assert data["bintang"] == 5
    assert data["nama"] == hotel["nama"]


def test_ubah_hotel_tanpa_key_401(client, hotel):
    assert client.patch(f"{PREFIX}/hotels/{hotel['id']}", json={"bintang": 5}).status_code == 401


def test_hapus_hotel_oleh_staf_403(client, staf, hotel):
    res = client.delete(f"{PREFIX}/hotels/{hotel['id']}", headers=staf)
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"


def test_hapus_hotel_oleh_admin_204(client, admin, hotel):
    res = client.delete(f"{PREFIX}/hotels/{hotel['id']}", headers=admin)
    assert res.status_code == 204
    assert res.content == b""
    assert client.get(f"{PREFIX}/hotels/{hotel['id']}").status_code == 404
