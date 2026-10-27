from tests.conftest import PREFIX


def test_root_service(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "running"


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_openapi_memuat_semua_resource(client):
    res = client.get("/openapi.json")
    assert res.status_code == 200
    paths = res.json()["paths"]
    for p in ("hotels", "destinations", "hotel-bookings", "destination-bookings"):
        assert f"{PREFIX}/{p}" in paths
    assert f"{PREFIX}/hotels/{{hotel_id}}/rooms" in paths


def test_route_tidak_ada_memakai_format_error_seragam(client):
    res = client.get("/tidak-ada")
    assert res.status_code == 404
    body = res.json()
    assert body["status"] == "error"
    assert body["code"] == "NOT_FOUND"
    assert body["path"] == "/tidak-ada"
