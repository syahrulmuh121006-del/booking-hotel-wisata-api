"""Data contoh (dipakai saat menjalankan server, tidak dipakai di test)."""
from app.repositories.database import Database
from app.schemas.destinasi import DestinasiCreate
from app.schemas.hotel import HotelCreate
from app.schemas.kamar import KamarCreate
from app.services.destinasi_service import DestinasiService
from app.services.hotel_service import HotelService
from app.services.kamar_service import KamarService


def seed_database(db: Database) -> None:
    hotel = HotelService(db).buat(
        HotelCreate(
            nama="Hotel Pantai Losari",
            kota="Makassar",
            bintang=4,
            alamat="Jl. Penghibur No. 10, Makassar",
            fasilitas=["wifi", "kolam renang", "sarapan"],
        )
    )
    kamar = KamarService(db)
    kamar.tambah(hotel["id"], KamarCreate(tipe="standar", harga_per_malam=450000, kapasitas=2, jumlah_unit=10))
    kamar.tambah(hotel["id"], KamarCreate(tipe="deluxe", harga_per_malam=750000, kapasitas=3, jumlah_unit=5))

    destinasi = DestinasiService(db)
    destinasi.buat(
        DestinasiCreate(
            nama="Rammang-Rammang",
            kategori="bahari",
            kota="Maros",
            deskripsi="Kawasan karst dengan susur sungai dan pemandangan batu kapur.",
            harga_tiket=25000,
            kuota_harian=200,
        )
    )
    destinasi.buat(
        DestinasiCreate(
            nama="Benteng Rotterdam",
            kategori="sejarah",
            kota="Makassar",
            deskripsi="Benteng peninggalan Kerajaan Gowa-Tallo di tepi Pantai Losari.",
            harga_tiket=10000,
            kuota_harian=500,
        )
    )
