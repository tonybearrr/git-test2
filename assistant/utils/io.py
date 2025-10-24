from __future__ import annotations
import json
import os
import tempfile
from typing import Any, Dict


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def atomic_write_json(file_path: str, data: Any) -> None:
    directory = os.path.dirname(file_path)
    ensure_directory(directory)
    fd, temp_path = tempfile.mkstemp(prefix=".tmp_", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, file_path)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
