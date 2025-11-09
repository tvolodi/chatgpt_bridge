# core/memory_manager.py
import json
import os

DEFAULT_MEMORY = {"last_sync": None, "lookup": {}, "projects": {}}


def load_memory(path: str):
    if not os.path.exists(path):
        # ensure parent exists
        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        return DEFAULT_MEMORY.copy()

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(path: str, data: dict):
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
