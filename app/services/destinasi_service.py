"""Logika bisnis Destinasi Wisata."""
from datetime import datetime, timezone

from app.core.errors import ConflictError, NotFoundError
from app.repositories.database import Database
from app.schemas.booking import StatusBooking
from app.schemas.common import paginate
from app.schemas.destinasi import DestinasiCreate, DestinasiUpdate, KategoriWisata


class DestinasiService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def _cek_duplikat(self, nama: str, kota: str, kecuali_id: int | None = None) -> None:
        for d in self.db.destinasi.list():
            if d["id"] != kecuali_id and d["nama"].lower() == nama.lower() and d["kota"].lower() == kota.lower():
                raise ConflictError(f"Destinasi '{nama}' di {kota} sudah terdaftar.")

    def buat(self, payload: DestinasiCreate) -> dict:
        self._cek_duplikat(payload.nama, payload.kota)
        item = self.db.destinasi.add(
            {
                **payload.model_dump(),
                "kode": "",
                "aktif": True,
                "dibuat_pada": datetime.now(timezone.utc),
            }
        )
        return self.db.destinasi.update(item["id"], {"kode": f"WST-{item['id']:03d}"})

    def ambil(self, destinasi_id: int) -> dict:
        destinasi = self.db.destinasi.get(destinasi_id)
        if destinasi is None:
            raise NotFoundError(f"Destinasi dengan id {destinasi_id} tidak ditemukan.")
        return destinasi

    def daftar(
        self,
        kategori: KategoriWisata | None,
        kota: str | None,
        harga_maks: int | None,
        q: str | None,
        halaman: int,
        per_halaman: int,
    ) -> dict:
        def cocok(d: dict) -> bool:
            if kategori and d["kategori"] != kategori:
                return False
            if kota and d["kota"].lower() != kota.lower():
                return False
            if harga_maks is not None and d["harga_tiket"] > harga_maks:
                return False
            if q and q.lower() not in d["nama"].lower() and q.lower() not in d["deskripsi"].lower():
                return False
            return True

        return paginate(self.db.destinasi.list(cocok), halaman, per_halaman)

    def ubah(self, destinasi_id: int, payload: DestinasiUpdate) -> dict:
        destinasi = self.ambil(destinasi_id)
        perubahan = payload.model_dump(exclude_unset=True, exclude_none=True)
        self._cek_duplikat(
            perubahan.get("nama", destinasi["nama"]),
            perubahan.get("kota", destinasi["kota"]),
            kecuali_id=destinasi_id,
        )
        return self.db.destinasi.update(destinasi_id, perubahan)

    def hapus(self, destinasi_id: int) -> None:
        self.ambil(destinasi_id)
        aktif = self.db.booking_wisata.list(
            lambda b: b["destinasi_id"] == destinasi_id and b["status"] == StatusBooking.DIKONFIRMASI
        )
        if aktif:
            raise ConflictError("Destinasi masih memiliki booking aktif dan tidak dapat dihapus.")
        self.db.destinasi.delete(destinasi_id)
