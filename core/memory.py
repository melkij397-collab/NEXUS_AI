import json
import os
from datetime import datetime


class NexusMemory:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.file = "data/memory.json"

        if not os.path.exists(self.file):
            self.save([])

    def load(self):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return []

    def save(self, memory):
        os.makedirs("data", exist_ok=True)
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=4)

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
