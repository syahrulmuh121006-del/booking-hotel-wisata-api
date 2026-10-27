from app.repositories.memory import InMemoryRepository


class Database:
    """Kumpulan repository untuk seluruh entitas."""

    def __init__(self) -> None:
        self.hotels = InMemoryRepository()
        self.kamar = InMemoryRepository()
        self.destinasi = InMemoryRepository()
        self.booking_hotel = InMemoryRepository()
        self.booking_wisata = InMemoryRepository()
