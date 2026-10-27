"""Endpoint /hotel-bookings.

Pelanggan boleh membuat booking tanpa key; melihat/mengubah status memerlukan staf; menghapus memerlukan admin.
"""
from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies.auth import Pengguna, verifikasi_api_key, wajib_admin
from app.dependencies.database import get_db
from app.repositories.database import Database
from app.routers._responses import E400, E401, E403, E404, E409
from app.schemas.booking import BookingHotelCreate, BookingHotelResponse, StatusBooking, StatusUpdate
from app.schemas.common import Halaman
from app.services.booking_hotel_service import BookingHotelService

router = APIRouter(prefix="/hotel-bookings", tags=["Hotel Bookings"])


def get_service(db: Database = Depends(get_db)) -> BookingHotelService:
    return BookingHotelService(db)


@router.post(
    "",
    response_model=BookingHotelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buat booking hotel (publik)",
    responses={**E400, **E404, **E409},
)
def buat_booking_hotel(payload: BookingHotelCreate, service: BookingHotelService = Depends(get_service)):
    return service.buat(payload)


@router.get(
    "",
    response_model=Halaman[BookingHotelResponse],
    summary="Daftar booking hotel (staf/admin)",
    responses=E401,
)
def daftar_booking_hotel(
    status_booking: StatusBooking | None = Query(default=None, alias="status"),
    hotel_id: int | None = Query(default=None, ge=1),
    halaman: int = Query(default=1, ge=1),
    per_halaman: int = Query(default=10, ge=1, le=100),
    _: Pengguna = Depends(verifikasi_api_key),
    service: BookingHotelService = Depends(get_service),
):
    return service.daftar(status_booking, hotel_id, halaman, per_halaman)


@router.get(
    "/{booking_id}",
    response_model=BookingHotelResponse,
    summary="Detail booking hotel (staf/admin)",
    responses={**E401, **E404},
)
def detail_booking_hotel(
    booking_id: int,
    _: Pengguna = Depends(verifikasi_api_key),
    service: BookingHotelService = Depends(get_service),
):
    return service.ambil(booking_id)


@router.patch(
    "/{booking_id}",
    response_model=BookingHotelResponse,
    summary="Ubah status booking: batalkan / selesai (staf/admin)",
    responses={**E401, **E404, **E409},
)
def ubah_status_booking_hotel(
    booking_id: int,
    payload: StatusUpdate,
    _: Pengguna = Depends(verifikasi_api_key),
    service: BookingHotelService = Depends(get_service),
):
    return service.ubah_status(booking_id, payload.status)


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus booking hotel (admin)",
    responses={**E401, **E403, **E404},
)
def hapus_booking_hotel(
    booking_id: int,
    _: Pengguna = Depends(wajib_admin),
    service: BookingHotelService = Depends(get_service),
):
    service.hapus(booking_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
