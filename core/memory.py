import json
import os
from datetime import datetime

MEMORY_FILE = "data/memory.json"


class NexusMemory:
    def __init__(self):
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(MEMORY_FILE):
            self.save([])

    def load(self):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, memory):
        os.makedirs("data", exist_ok=True)

        with open(MEMORY_FILE, "w", encoding="utf-8") as file:
            json.dump(memory, file, ensure_ascii=False, indent=4)

    def add(self, role, content):
        memory = self.load()
        memory.append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat()
        })
        self.save(memory)

    def get_history(self, limit=20):
        return self.load()[-limit:]

    def clear(self):
        self.save([])
