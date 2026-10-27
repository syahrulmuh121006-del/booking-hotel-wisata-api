"""Logika bisnis Kamar (sub-resource Hotel)."""
from app.core.errors import ConflictError, NotFoundError
from app.repositories.database import Database
from app.schemas.booking import StatusBooking
from app.schemas.kamar import KamarCreate, KamarUpdate
from app.services.hotel_service import HotelService


class KamarService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def tambah(self, hotel_id: int, payload: KamarCreate) -> dict:
        HotelService(self.db).ambil(hotel_id)
        return self.db.kamar.add({"hotel_id": hotel_id, **payload.model_dump()})

    def daftar(self, hotel_id: int) -> list[dict]:
        HotelService(self.db).ambil(hotel_id)
        return self.db.kamar.list(lambda k: k["hotel_id"] == hotel_id)

    def ambil(self, hotel_id: int, kamar_id: int) -> dict:
        HotelService(self.db).ambil(hotel_id)
        kamar = self.db.kamar.get(kamar_id)
        if kamar is None or kamar["hotel_id"] != hotel_id:
            raise NotFoundError(f"Kamar {kamar_id} tidak ditemukan pada hotel {hotel_id}.")
        return kamar

    def ubah(self, hotel_id: int, kamar_id: int, payload: KamarUpdate) -> dict:
        self.ambil(hotel_id, kamar_id)
        perubahan = payload.model_dump(exclude_unset=True, exclude_none=True)
        return self.db.kamar.update(kamar_id, perubahan)

    def hapus(self, hotel_id: int, kamar_id: int) -> None:
        self.ambil(hotel_id, kamar_id)
        aktif = self.db.booking_hotel.list(
            lambda b: b["kamar_id"] == kamar_id and b["status"] == StatusBooking.DIKONFIRMASI
        )
        if aktif:
            raise ConflictError("Kamar masih memiliki booking aktif dan tidak dapat dihapus.")
        self.db.kamar.delete(kamar_id)
