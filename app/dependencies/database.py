from fastapi import Request

from app.repositories.database import Database


def get_db(request: Request) -> Database:
    """Mengambil 'database' milik instance app (memudahkan isolasi saat testing)."""
    return request.app.state.db
