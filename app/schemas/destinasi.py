"""Kontrak data Destinasi Wisata."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class KategoriWisata(str, Enum):
    PANTAI = "pantai"
    GUNUNG = "gunung"
    BUDAYA = "budaya"
    SEJARAH = "sejarah"
    KULINER = "kuliner"
    BAHARI = "bahari"


class DestinasiBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nama: str = Field(..., min_length=3, max_length=100)
    kategori: KategoriWisata
    kota: str = Field(..., min_length=2, max_length=60)
    deskripsi: str = Field(..., min_length=10, max_length=500)
    harga_tiket: int = Field(..., ge=0, le=10_000_000, description="Rupiah per orang (0 = gratis)")
    kuota_harian: int = Field(..., ge=1, le=10_000, description="Maksimal pengunjung per hari")


class DestinasiCreate(DestinasiBase):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "nama": "Rammang-Rammang",
                "kategori": "bahari",
                "kota": "Maros",
                "deskripsi": "Kawasan karst dengan susur sungai dan pemandangan batu kapur.",
                "harga_tiket": 25000,
                "kuota_harian": 200,
            }
        },
    )


class DestinasiUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nama: str | None = Field(default=None, min_length=3, max_length=100)
    kategori: KategoriWisata | None = None
    kota: str | None = Field(default=None, min_length=2, max_length=60)
    deskripsi: str | None = Field(default=None, min_length=10, max_length=500)
    harga_tiket: int | None = Field(default=None, ge=0, le=10_000_000)
    kuota_harian: int | None = Field(default=None, ge=1, le=10_000)
    aktif: bool | None = None


class DestinasiResponse(DestinasiBase):
    id: int
    kode: str
    aktif: bool
    dibuat_pada: datetime
