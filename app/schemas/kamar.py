"""Kontrak data Kamar hotel."""
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TipeKamar(str, Enum):
    STANDAR = "standar"
    DELUXE = "deluxe"
    SUITE = "suite"
    KELUARGA = "keluarga"


class KamarBase(BaseModel):
    tipe: TipeKamar
    harga_per_malam: int = Field(..., ge=100_000, le=50_000_000, description="Rupiah per malam")
    kapasitas: int = Field(..., ge=1, le=8, description="Jumlah tamu maksimal per kamar")
    jumlah_unit: int = Field(..., ge=1, le=200, description="Jumlah kamar tipe ini yang tersedia")


class KamarCreate(KamarBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"tipe": "deluxe", "harga_per_malam": 750000, "kapasitas": 2, "jumlah_unit": 5}
        }
    )


class KamarUpdate(BaseModel):
    tipe: TipeKamar | None = None
    harga_per_malam: int | None = Field(default=None, ge=100_000, le=50_000_000)
    kapasitas: int | None = Field(default=None, ge=1, le=8)
    jumlah_unit: int | None = Field(default=None, ge=1, le=200)


class KamarResponse(KamarBase):
    id: int
    hotel_id: int
