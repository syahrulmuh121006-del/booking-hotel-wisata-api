"""Autentikasi (X-API-Key) dan otorisasi bertingkat (staf vs admin) via Depends()."""
import secrets
from dataclasses import dataclass
from enum import Enum

from fastapi import Depends, Header, HTTPException, status

from app.core.config import get_settings


class Peran(str, Enum):
    STAF = "staf"
    ADMIN = "admin"


@dataclass(frozen=True)
class Pengguna:
    peran: Peran


def _sama(a: str, b: str) -> bool:
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def verifikasi_api_key(
    x_api_key: str | None = Header(default=None, description="API Key staf atau admin."),
) -> Pengguna:
    """401 jika header tidak ada / key salah."""
    tantangan = {"WWW-Authenticate": "ApiKey"}
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header X-API-Key wajib disertakan.",
            headers=tantangan,
        )
    pengaturan = get_settings()
    if _sama(x_api_key, pengaturan.kunci_admin):
        return Pengguna(peran=Peran.ADMIN)
    if _sama(x_api_key, pengaturan.kunci_staf):
        return Pengguna(peran=Peran.STAF)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API Key tidak valid.",
        headers=tantangan,
    )


def wajib_admin(pengguna: Pengguna = Depends(verifikasi_api_key)) -> Pengguna:
    """403 jika pengguna dikenal tetapi bukan admin."""
    if pengguna.peran != Peran.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak: operasi ini membutuhkan hak akses ADMIN.",
        )
    return pengguna
