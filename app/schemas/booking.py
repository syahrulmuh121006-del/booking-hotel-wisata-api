"""Kontrak data Booking Hotel dan Booking Tiket Destinasi Wisata."""
from datetime import date, datetime
from enum import Enum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

POLA_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
MAKS_MALAM = 30


class StatusBooking(str, Enum):
    DIKONFIRMASI = "dikonfirmasi"
    DIBATALKAN = "dibatalkan"
    SELESAI = "selesai"


class StatusUpdate(BaseModel):
    status: StatusBooking


def _tidak_di_masa_lalu(nilai: date) -> date:
    if nilai < date.today():
        raise ValueError("Tanggal tidak boleh di masa lalu")
    return nilai


# ---------------------------- Booking Hotel ----------------------------
class BookingHotelCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "hotel_id": 1,
                "kamar_id": 1,
                "nama_tamu": "Andi Baso",
                "email": "andi@example.com",
                "tanggal_checkin": "2030-01-10",
                "tanggal_checkout": "2030-01-12",
                "jumlah_tamu": 2,
                "jumlah_kamar": 1,
            }
        },
    )

    hotel_id: int = Field(..., ge=1)
    kamar_id: int = Field(..., ge=1)
    nama_tamu: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., pattern=POLA_EMAIL, max_length=120)
    tanggal_checkin: date
    tanggal_checkout: date
    jumlah_tamu: int = Field(..., ge=1, le=40)
    jumlah_kamar: int = Field(default=1, ge=1, le=10)

    @field_validator("tanggal_checkin")
    @classmethod
    def checkin_valid(cls, v: date) -> date:
        return _tidak_di_masa_lalu(v)

    @model_validator(mode="after")
    def validasi_rentang_tanggal(self) -> Self:
        if self.tanggal_checkout <= self.tanggal_checkin:
            raise ValueError("tanggal_checkout harus setelah tanggal_checkin")
        if (self.tanggal_checkout - self.tanggal_checkin).days > MAKS_MALAM:
            raise ValueError(f"Lama menginap maksimal {MAKS_MALAM} malam")
        return self


class BookingHotelResponse(BaseModel):
    id: int
    kode_booking: str
    hotel_id: int
    kamar_id: int
    nama_tamu: str
    email: str
    tanggal_checkin: date
    tanggal_checkout: date
    jumlah_tamu: int
    jumlah_kamar: int
    jumlah_malam: int
    total_harga: int
    status: StatusBooking
    dibuat_pada: datetime


# ------------------------- Booking Destinasi Wisata -------------------------
class BookingWisataCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "destinasi_id": 1,
                "nama_pemesan": "Siti Aisyah",
                "email": "siti@example.com",
                "tanggal_kunjungan": "2030-01-11",
                "jumlah_tiket": 3,
            }
        },
    )

    destinasi_id: int = Field(..., ge=1)
    nama_pemesan: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., pattern=POLA_EMAIL, max_length=120)
    tanggal_kunjungan: date
    jumlah_tiket: int = Field(..., ge=1, le=50)

    @field_validator("tanggal_kunjungan")
    @classmethod
    def kunjungan_valid(cls, v: date) -> date:
        return _tidak_di_masa_lalu(v)


class BookingWisataResponse(BaseModel):
    id: int
    kode_booking: str
    destinasi_id: int
    nama_pemesan: str
    email: str
    tanggal_kunjungan: date
    jumlah_tiket: int
    total_harga: int
    status: StatusBooking
    dibuat_pada: datetime
