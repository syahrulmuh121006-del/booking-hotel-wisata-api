"""Konfigurasi aplikasi. Nilai sensitif dapat dioverride lewat environment variable."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    nama_aplikasi: str
    versi: str
    api_prefix: str
    kunci_staf: str
    kunci_admin: str


def get_settings() -> Settings:
    return Settings(
        nama_aplikasi="API Booking Hotel & Destinasi Wisata Sulawesi Selatan",
        versi="1.0.0",
        api_prefix="/api/v1",
        kunci_staf=os.getenv("STAF_API_KEY", "staf-key-2026"),
        kunci_admin=os.getenv("ADMIN_API_KEY", "admin-key-2026"),
    )
