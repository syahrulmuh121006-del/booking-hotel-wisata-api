"""Endpoint sub-resource /hotels/{hotel_id}/rooms."""
from fastapi import APIRouter, Depends, Response, status

from app.dependencies.auth import Pengguna, verifikasi_api_key, wajib_admin
from app.dependencies.database import get_db
from app.repositories.database import Database
from app.routers._responses import E401, E403, E404, E409
from app.schemas.kamar import KamarCreate, KamarResponse, KamarUpdate
from app.services.kamar_service import KamarService

router = APIRouter(prefix="/hotels/{hotel_id}/rooms", tags=["Rooms"])


def get_service(db: Database = Depends(get_db)) -> KamarService:
    return KamarService(db)


@router.get("", response_model=list[KamarResponse], summary="Daftar kamar pada hotel (publik)", responses=E404)
def daftar_kamar(hotel_id: int, service: KamarService = Depends(get_service)):
    return service.daftar(hotel_id)


@router.post(
    "",
    response_model=KamarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah kamar (staf/admin)",
    responses={**E401, **E404},
)
def tambah_kamar(
    hotel_id: int,
    payload: KamarCreate,
    _: Pengguna = Depends(verifikasi_api_key),
    service: KamarService = Depends(get_service),
):
    return service.tambah(hotel_id, payload)


@router.get("/{kamar_id}", response_model=KamarResponse, summary="Detail kamar (publik)", responses=E404)
def detail_kamar(hotel_id: int, kamar_id: int, service: KamarService = Depends(get_service)):
    return service.ambil(hotel_id, kamar_id)


@router.patch(
    "/{kamar_id}",
    response_model=KamarResponse,
    summary="Ubah sebagian data kamar (staf/admin)",
    responses={**E401, **E404},
)
def ubah_kamar(
    hotel_id: int,
    kamar_id: int,
    payload: KamarUpdate,
    _: Pengguna = Depends(verifikasi_api_key),
    service: KamarService = Depends(get_service),
):
    return service.ubah(hotel_id, kamar_id, payload)


@router.delete(
    "/{kamar_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus kamar (admin)",
    responses={**E401, **E403, **E404, **E409},
)
def hapus_kamar(
    hotel_id: int,
    kamar_id: int,
    _: Pengguna = Depends(wajib_admin),
    service: KamarService = Depends(get_service),
):
    service.hapus(hotel_id, kamar_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
