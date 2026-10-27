"""Logika bisnis Hotel."""
from datetime import datetime, timezone

from app.core.errors import ConflictError, NotFoundError
from app.repositories.database import Database
from app.schemas.booking import StatusBooking
from app.schemas.common import paginate
from app.schemas.hotel import HotelCreate, HotelUpdate


class HotelService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def _cek_duplikat(self, nama: str, kota: str, kecuali_id: int | None = None) -> None:
        for h in self.db.hotels.list():
            if h["id"] != kecuali_id and h["nama"].lower() == nama.lower() and h["kota"].lower() == kota.lower():
                raise ConflictError(f"Hotel '{nama}' di {kota} sudah terdaftar.")

    def buat(self, payload: HotelCreate) -> dict:
        self._cek_duplikat(payload.nama, payload.kota)
        item = self.db.hotels.add(
            {
                **payload.model_dump(),
                "kode": "",
                "aktif": True,
                "dibuat_pada": datetime.now(timezone.utc),
            }
        )
        return self.db.hotels.update(item["id"], {"kode": f"HTL-{item['id']:03d}"})

    def ambil(self, hotel_id: int) -> dict:
        hotel = self.db.hotels.get(hotel_id)
        if hotel is None:
            raise NotFoundError(f"Hotel dengan id {hotel_id} tidak ditemukan.")
        return hotel

    def daftar(
        self,
        kota: str | None,
        bintang_min: int | None,
        q: str | None,
        halaman: int,
        per_halaman: int,
    ) -> dict:
        def cocok(h: dict) -> bool:
            if kota and h["kota"].lower() != kota.lower():
                return False
            if bintang_min and h["bintang"] < bintang_min:
                return False
            if q and q.lower() not in h["nama"].lower() and q.lower() not in h["alamat"].lower():
                return False
            return True

        return paginate(self.db.hotels.list(cocok), halaman, per_halaman)

    def ubah(self, hotel_id: int, payload: HotelUpdate) -> dict:
        hotel = self.ambil(hotel_id)
        perubahan = payload.model_dump(exclude_unset=True, exclude_none=True)
        self._cek_duplikat(
            perubahan.get("nama", hotel["nama"]),
            perubahan.get("kota", hotel["kota"]),
            kecuali_id=hotel_id,
        )
        return self.db.hotels.update(hotel_id, perubahan)

    def hapus(self, hotel_id: int) -> None:
        self.ambil(hotel_id)
        aktif = self.db.booking_hotel.list(
            lambda b: b["hotel_id"] == hotel_id and b["status"] == StatusBooking.DIKONFIRMASI
        )
        if aktif:
            raise ConflictError("Hotel masih memiliki booking aktif dan tidak dapat dihapus.")
        for kamar in self.db.kamar.list(lambda k: k["hotel_id"] == hotel_id):
            self.db.kamar.delete(kamar["id"])
        self.db.hotels.delete(hotel_id)
