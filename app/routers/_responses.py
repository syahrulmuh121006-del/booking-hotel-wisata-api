"""Dokumentasi respons error standar untuk Swagger."""
from app.schemas.common import ErrorResponse

E401 = {401: {"model": ErrorResponse, "description": "X-API-Key tidak ada / tidak valid"}}
E403 = {403: {"model": ErrorResponse, "description": "Peran tidak memiliki hak akses"}}
E404 = {404: {"model": ErrorResponse, "description": "Resource tidak ditemukan"}}
E409 = {409: {"model": ErrorResponse, "description": "Konflik data / aturan keadaan"}}
E400 = {400: {"model": ErrorResponse, "description": "Aturan bisnis dilanggar"}}
