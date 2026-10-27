"""Kontrak data umum: pagination dan format error."""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Halaman(BaseModel, Generic[T]):
    data: list[T]
    total: int
    halaman: int
    per_halaman: int


class DetailError(BaseModel):
    field: str
    msg: str


class ErrorResponse(BaseModel):
    status: str = "error"
    code: str
    path: str
    message: str | None = None
    details: list[DetailError] | None = None


def paginate(items: list, halaman: int, per_halaman: int) -> dict:
    mulai = (halaman - 1) * per_halaman
    return {
        "data": items[mulai : mulai + per_halaman],
        "total": len(items),
        "halaman": halaman,
        "per_halaman": per_halaman,
    }
