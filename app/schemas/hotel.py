"""Kontrak data Hotel (DTO: Create / Update / Response)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _bersihkan_fasilitas(nilai: list[str] | None) -> list[str] | None:
    if nilai is None:
        return None
    hasil: list[str] = []
    for f in nilai:
        f = f.strip().lower()
        if not f:
            raise ValueError("Nama fasilitas tidak boleh kosong")
        if f not in hasil:
            hasil.append(f)
    return hasil


class HotelBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nama: str = Field(..., min_length=3, max_length=100, description="Nama hotel")
    kota: str = Field(..., min_length=2, max_length=60)
    bintang: int = Field(..., ge=1, le=5, description="Kelas bintang 1-5")
    alamat: str = Field(..., min_length=5, max_length=200)
    fasilitas: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("fasilitas")
    @classmethod
    def validasi_fasilitas(cls, v: list[str]) -> list[str]:
        return _bersihkan_fasilitas(v) or []


class HotelCreate(HotelBase):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "nama": "Hotel Pantai Losari",
                "kota": "Makassar",
                "bintang": 4,
                "alamat": "Jl. Penghibur No. 10, Makassar",
                "fasilitas": ["wifi", "kolam renang"],
            }
        },
    )


class HotelUpdate(BaseModel):
    """PATCH: semua field opsional."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nama: str | None = Field(default=None, min_length=3, max_length=100)
    kota: str | None = Field(default=None, min_length=2, max_length=60)
    bintang: int | None = Field(default=None, ge=1, le=5)
    alamat: str | None = Field(default=None, min_length=5, max_length=200)
    fasilitas: list[str] | None = Field(default=None, max_length=20)
    aktif: bool | None = None

    @field_validator("fasilitas")
    @classmethod
    def validasi_fasilitas(cls, v: list[str] | None) -> list[str] | None:
        return _bersihkan_fasilitas(v)


class HotelResponse(HotelBase):
    id: int
    kode: str
    aktif: bool
    dibuat_pada: datetime
