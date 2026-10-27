"""Aturan transisi status booking (dipakai booking hotel & booking wisata)."""
from app.core.errors import ConflictError
from app.schemas.booking import StatusBooking

TRANSISI: dict[StatusBooking, set[StatusBooking]] = {
    StatusBooking.DIKONFIRMASI: {StatusBooking.DIBATALKAN, StatusBooking.SELESAI},
    StatusBooking.DIBATALKAN: set(),
    StatusBooking.SELESAI: set(),
}


def validasi_transisi(sekarang: StatusBooking, tujuan: StatusBooking) -> None:
    if tujuan not in TRANSISI[StatusBooking(sekarang)]:
        raise ConflictError(
            f"Status booking tidak dapat diubah dari '{StatusBooking(sekarang).value}' ke '{tujuan.value}'."
        )
