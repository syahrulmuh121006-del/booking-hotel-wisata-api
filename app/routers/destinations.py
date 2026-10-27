"""Endpoint /destinations (destinasi wisata)."""
from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies.auth import Pengguna, verifikasi_api_key, wajib_admin
from app.dependencies.database import get_db
from app.repositories.database import Database
from app.routers._responses import E401, E403, E404, E409
from app.schemas.common import Halaman
from app.schemas.destinasi import DestinasiCreate, DestinasiResponse, DestinasiUpdate, KategoriWisata
from app.services.destinasi_service import DestinasiService

router = APIRouter(prefix="/destinations", tags=["Destinations"])


def get_service(db: Database = Depends(get_db)) -> DestinasiService:
    return DestinasiService(db)


@router.get("", response_model=Halaman[DestinasiResponse], summary="Daftar destinasi wisata (publik)")
def daftar_destinasi(
    kategori: KategoriWisata | None = Query(default=None),
    kota: str | None = Query(default=None),
    harga_maks: int | None = Query(default=None, ge=0, description="Harga tiket maksimal"),
    q: str | None = Query(default=None, min_length=2),
    halaman: int = Query(default=1, ge=1),
    per_halaman: int = Query(default=10, ge=1, le=100),
    service: DestinasiService = Depends(get_service),
):
    return service.daftar(kategori, kota, harga_maks, q, halaman, per_halaman)


@router.post(
    "",
    response_model=DestinasiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah destinasi (staf/admin)",
    responses={**E401, **E409},
)
def tambah_destinasi(
    payload: DestinasiCreate,
    _: Pengguna = Depends(verifikasi_api_key),
    service: DestinasiService = Depends(get_service),
):
    return service.buat(payload)


@router.get("/{destinasi_id}", response_model=DestinasiResponse, summary="Detail destinasi (publik)", responses=E404)
def detail_destinasi(destinasi_id: int, service: DestinasiService = Depends(get_service)):
    return service.ambil(destinasi_id)


@router.patch(
    "/{destinasi_id}",
    response_model=DestinasiResponse,
    summary="Ubah sebagian data destinasi (staf/admin)",
    responses={**E401, **E404, **E409},
)
def ubah_destinasi(
    destinasi_id: int,
    payload: DestinasiUpdate,
    _: Pengguna = Depends(verifikasi_api_key),
    service: DestinasiService = Depends(get_service),
):
    return service.ubah(destinasi_id, payload)


@router.delete(
    "/{destinasi_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus destinasi (admin)",
    responses={**E401, **E403, **E404, **E409},
)
def hapus_destinasi(
    destinasi_id: int,
    _: Pengguna = Depends(wajib_admin),
    service: DestinasiService = Depends(get_service),
):
    service.hapus(destinasi_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
