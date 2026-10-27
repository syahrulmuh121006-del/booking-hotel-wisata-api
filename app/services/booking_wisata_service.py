"""Logika bisnis Booking Tiket Destinasi Wisata: kuota harian dan total harga."""
from datetime import datetime, timezone

from app.core.errors import BusinessRuleError, ConflictError, NotFoundError
from app.repositories.database import Database
from app.schemas.booking import BookingWisataCreate, StatusBooking
from app.schemas.common import paginate
from app.services.destinasi_service import DestinasiService
from app.services.status_rules import validasi_transisi


class BookingWisataService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def buat(self, payload: BookingWisataCreate) -> dict:
        destinasi = DestinasiService(self.db).ambil(payload.destinasi_id)
        if not destinasi["aktif"]:
            raise BusinessRuleError("Destinasi sedang tidak aktif dan tidak menerima booking.")

        terpakai = sum(
            b["jumlah_tiket"]
            for b in self.db.booking_wisata.list(
                lambda b: b["destinasi_id"] == payload.destinasi_id
                and b["status"] == StatusBooking.DIKONFIRMASI
                and b["tanggal_kunjungan"] == payload.tanggal_kunjungan
            )
        )
        if terpakai + payload.jumlah_tiket > destinasi["kuota_harian"]:
            sisa = max(destinasi["kuota_harian"] - terpakai, 0)
            raise ConflictError(f"Kuota harian tidak mencukupi. Sisa kuota pada tanggal tersebut: {sisa}.")

        item = self.db.booking_wisata.add(
            {
                **payload.model_dump(),
                "kode_booking": "",
                "total_harga": destinasi["harga_tiket"] * payload.jumlah_tiket,
                "status": StatusBooking.DIKONFIRMASI,
                "dibuat_pada": datetime.now(timezone.utc),
            }
        )
        return self.db.booking_wisata.update(item["id"], {"kode_booking": f"BKW-{item['id']:04d}"})

    def ambil(self, booking_id: int) -> dict:
        booking = self.db.booking_wisata.get(booking_id)
        if booking is None:
            raise NotFoundError(f"Booking wisata dengan id {booking_id} tidak ditemukan.")
        return booking

    def daftar(
        self,
        status: StatusBooking | None,
        destinasi_id: int | None,
        halaman: int,
        per_halaman: int,
    ) -> dict:
        def cocok(b: dict) -> bool:
            if status and b["status"] != status:
                return False
            if destinasi_id and b["destinasi_id"] != destinasi_id:
                return False
            return True

        return paginate(self.db.booking_wisata.list(cocok), halaman, per_halaman)

    def ubah_status(self, booking_id: int, tujuan: StatusBooking) -> dict:
        booking = self.ambil(booking_id)
        validasi_transisi(booking["status"], tujuan)
        return self.db.booking_wisata.update(booking_id, {"status": tujuan})

    def hapus(self, booking_id: int) -> None:
        self.ambil(booking_id)
        self.db.booking_wisata.delete(booking_id)
