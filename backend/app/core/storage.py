import os
import aiofiles
from pathlib import Path
from typing import Protocol
from app.core.config import settings

class StorageBackend(Protocol):
    async def save_file(self, filename: str, content: bytes) -> str: ...
    async def get_file(self, file_path: str) -> bytes: ...
    async def delete_file(self, file_path: str) -> bool: ...

class LocalFileStorage:
    def __init__(self, base_dir: str = settings.STORAGE_PATH):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        target_path = self.base_dir / filename
        target_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(target_path, "wb") as f:
            await f.write(content)
        return str(target_path)

    async def get_file(self, file_path: str) -> bytes:
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    async def delete_file(self, file_path: str) -> bool:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False

def get_storage_backend() -> StorageBackend:
    return LocalFileStorage()
