"""Titik masuk aplikasi. Jalankan dengan: uvicorn app.main:app --reload"""
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.repositories.database import Database
from app.routers import destination_bookings, destinations, hotel_bookings, hotels, rooms
from app.seed import seed_database


def create_app(seed: bool = False) -> FastAPI:
    pengaturan = get_settings()
    app = FastAPI(
        title=pengaturan.nama_aplikasi,
        version=pengaturan.versi,
        description=(
            "REST API untuk pemesanan hotel dan tiket destinasi wisata.\n\n"
            "**Autentikasi:** kirim header `X-API-Key`. Endpoint GET katalog bersifat publik, "
            "operasi tulis memerlukan staf, penghapusan memerlukan admin."
        ),
    )
    app.state.db = Database()
    if seed:
        seed_database(app.state.db)

    register_exception_handlers(app)

    @app.get("/", tags=["Root"], summary="Info layanan")
    def root():
        return {"service": pengaturan.nama_aplikasi, "version": pengaturan.versi, "status": "running"}

    @app.get("/health", tags=["Root"], summary="Health check")
    def health():
        return {"status": "ok"}

    for modul in (hotels, rooms, destinations, hotel_bookings, destination_bookings):
        app.include_router(modul.router, prefix=pengaturan.api_prefix)
    return app


app = create_app(seed=True)
