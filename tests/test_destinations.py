from tests.conftest import PREFIX, destinasi_payload


def test_tambah_destinasi_berhasil(client, staf):
    res = client.post(f"{PREFIX}/destinations", json=destinasi_payload(), headers=staf)
    assert res.status_code == 201
    data = res.json()
    assert data["kode"] == "WST-001"
    assert data["kategori"] == "bahari"
    assert data["aktif"] is True


def test_tambah_destinasi_tanpa_key_401(client):
    assert client.post(f"{PREFIX}/destinations", json=destinasi_payload()).status_code == 401


def test_harga_tiket_negatif_422(client, staf):
    res = client.post(f"{PREFIX}/destinations", json=destinasi_payload(harga_tiket=-1), headers=staf)
    assert res.status_code == 422
    assert res.json()["code"] == "VALIDATION_ERROR"


def test_kategori_tidak_dikenal_422(client, staf):
    res = client.post(f"{PREFIX}/destinations", json=destinasi_payload(kategori="luar-angkasa"), headers=staf)
    assert res.status_code == 422


def test_destinasi_duplikat_409(client, staf, destinasi):
    res = client.post(f"{PREFIX}/destinations", json=destinasi_payload(), headers=staf)
    assert res.status_code == 409


def test_filter_kategori_dan_harga_maks(client, staf, destinasi):
    client.post(
        f"{PREFIX}/destinations",
        json=destinasi_payload(nama="Benteng Rotterdam", kategori="sejarah", kota="Makassar", harga_tiket=10000),
        headers=staf,
    )
    assert client.get(f"{PREFIX}/destinations").json()["total"] == 2
    assert client.get(f"{PREFIX}/destinations", params={"kategori": "sejarah"}).json()["total"] == 1
    assert client.get(f"{PREFIX}/destinations", params={"harga_maks": 10000}).json()["total"] == 1


def test_kategori_query_tidak_valid_422(client):
    assert client.get(f"{PREFIX}/destinations", params={"kategori": "xyz"}).status_code == 422


def test_detail_destinasi_404(client):
    assert client.get(f"{PREFIX}/destinations/42").status_code == 404


def test_ubah_destinasi(client, staf, destinasi):
    res = client.patch(f"{PREFIX}/destinations/{destinasi['id']}", json={"harga_tiket": 30000}, headers=staf)
    assert res.status_code == 200
    assert res.json()["harga_tiket"] == 30000


def test_hapus_destinasi_rbac(client, staf, admin, destinasi):
    url = f"{PREFIX}/destinations/{destinasi['id']}"
    assert client.delete(url, headers=staf).status_code == 403
    assert client.delete(url, headers=admin).status_code == 204
    assert client.get(url).status_code == 404
