"""Endpoint /hotels."""
from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies.auth import Pengguna, verifikasi_api_key, wajib_admin
from app.dependencies.database import get_db
from app.repositories.database import Database
from app.routers._responses import E401, E403, E404, E409
from app.schemas.common import Halaman
from app.schemas.hotel import HotelCreate, HotelResponse, HotelUpdate
from app.services.hotel_service import HotelService

router = APIRouter(prefix="/hotels", tags=["Hotels"])


def get_service(db: Database = Depends(get_db)) -> HotelService:
    return HotelService(db)


@router.get("", response_model=Halaman[HotelResponse], summary="Daftar hotel (publik)")
def daftar_hotel(
    kota: str | None = Query(default=None, description="Filter kota (persis, tidak peka huruf besar)"),
    bintang_min: int | None = Query(default=None, ge=1, le=5),
    q: str | None = Query(default=None, min_length=2, description="Cari pada nama/alamat"),
    halaman: int = Query(default=1, ge=1),
    per_halaman: int = Query(default=10, ge=1, le=100),
    service: HotelService = Depends(get_service),
):
    return service.daftar(kota, bintang_min, q, halaman, per_halaman)


@router.post(
    "",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah hotel (staf/admin)",
    responses={**E401, **E409},
)
def tambah_hotel(
    payload: HotelCreate,
    _: Pengguna = Depends(verifikasi_api_key),
    service: HotelService = Depends(get_service),
):
    return service.buat(payload)


@router.get("/{hotel_id}", response_model=HotelResponse, summary="Detail hotel (publik)", responses=E404)
def detail_hotel(hotel_id: int, service: HotelService = Depends(get_service)):
    return service.ambil(hotel_id)


@router.patch(
    "/{hotel_id}",
    response_model=HotelResponse,
    summary="Ubah sebagian data hotel (staf/admin)",
    responses={**E401, **E404, **E409},
)
def ubah_hotel(
    hotel_id: int,
    payload: HotelUpdate,
    _: Pengguna = Depends(verifikasi_api_key),
    service: HotelService = Depends(get_service),
):
    return service.ubah(hotel_id, payload)


@router.delete(
    "/{hotel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus hotel (admin)",
    responses={**E401, **E403, **E404, **E409},
)
def hapus_hotel(
    hotel_id: int,
    _: Pengguna = Depends(wajib_admin),
    service: HotelService = Depends(get_service),
):
    service.hapus(hotel_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
