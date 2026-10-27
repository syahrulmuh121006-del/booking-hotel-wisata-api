"""Logika bisnis Booking Hotel: validasi kapasitas, ketersediaan, dan hitung total harga."""
from datetime import datetime, timezone

from app.core.errors import BusinessRuleError, ConflictError, NotFoundError
from app.repositories.database import Database
from app.schemas.booking import BookingHotelCreate, StatusBooking
from app.schemas.common import paginate
from app.services.hotel_service import HotelService
from app.services.kamar_service import KamarService
from app.services.status_rules import validasi_transisi


class BookingHotelService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def buat(self, payload: BookingHotelCreate) -> dict:
        hotel = HotelService(self.db).ambil(payload.hotel_id)
        if not hotel["aktif"]:
            raise BusinessRuleError("Hotel sedang tidak aktif dan tidak menerima booking.")
        kamar = KamarService(self.db).ambil(payload.hotel_id, payload.kamar_id)

        if payload.jumlah_tamu > kamar["kapasitas"] * payload.jumlah_kamar:
            raise BusinessRuleError(
                f"Jumlah tamu melebihi kapasitas ({kamar['kapasitas']} tamu per kamar x {payload.jumlah_kamar} kamar)."
            )

        # Konservatif: jumlahkan semua booking aktif yang tanggalnya beririsan.
        terpakai = sum(
            b["jumlah_kamar"]
            for b in self.db.booking_hotel.list(
                lambda b: b["kamar_id"] == payload.kamar_id
                and b["status"] == StatusBooking.DIKONFIRMASI
                and b["tanggal_checkin"] < payload.tanggal_checkout
                and payload.tanggal_checkin < b["tanggal_checkout"]
            )
        )
        if terpakai + payload.jumlah_kamar > kamar["jumlah_unit"]:
            raise ConflictError("Kamar tidak tersedia pada rentang tanggal tersebut.")

        malam = (payload.tanggal_checkout - payload.tanggal_checkin).days
        item = self.db.booking_hotel.add(
            {
                **payload.model_dump(),
                "kode_booking": "",
                "jumlah_malam": malam,
                "total_harga": malam * kamar["harga_per_malam"] * payload.jumlah_kamar,
                "status": StatusBooking.DIKONFIRMASI,
                "dibuat_pada": datetime.now(timezone.utc),
            }
        )
        return self.db.booking_hotel.update(item["id"], {"kode_booking": f"BKH-{item['id']:04d}"})

    def ambil(self, booking_id: int) -> dict:
        booking = self.db.booking_hotel.get(booking_id)
        if booking is None:
            raise NotFoundError(f"Booking hotel dengan id {booking_id} tidak ditemukan.")
        return booking

    def daftar(
        self,
        status: StatusBooking | None,
        hotel_id: int | None,
        halaman: int,
        per_halaman: int,
    ) -> dict:
        def cocok(b: dict) -> bool:
            if status and b["status"] != status:
                return False
            if hotel_id and b["hotel_id"] != hotel_id:
                return False
            return True

        return paginate(self.db.booking_hotel.list(cocok), halaman, per_halaman)

    def ubah_status(self, booking_id: int, tujuan: StatusBooking) -> dict:
        booking = self.ambil(booking_id)
        validasi_transisi(booking["status"], tujuan)
        return self.db.booking_hotel.update(booking_id, {"status": tujuan})

    def hapus(self, booking_id: int) -> None:
        self.ambil(booking_id)
        self.db.booking_hotel.delete(booking_id)
