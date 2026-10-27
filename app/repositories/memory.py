"""Repository generik in-memory (pengganti database untuk tugas ini)."""
from typing import Callable


class InMemoryRepository:
    def __init__(self) -> None:
        self._items: dict[int, dict] = {}
        self._counter = 0

    def add(self, data: dict) -> dict:
        self._counter += 1
        item = {"id": self._counter, **data}
        self._items[self._counter] = item
        return dict(item)

    def get(self, item_id: int) -> dict | None:
        item = self._items.get(item_id)
        return dict(item) if item else None

    def list(self, predicate: Callable[[dict], bool] | None = None) -> list[dict]:
        items = sorted(self._items.values(), key=lambda i: i["id"])
        return [dict(i) for i in items if predicate is None or predicate(i)]

    def update(self, item_id: int, changes: dict) -> dict | None:
        item = self._items.get(item_id)
        if item is None:
            return None
        item.update(changes)
        return dict(item)

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None
