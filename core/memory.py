import json
import os
import re
from datetime import datetime

MEMORY_DIR = "data/users"


class NexusMemory:
    def __init__(self, session_id="default"):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "", str(session_id))[:80]
        self.memory_file = os.path.join(
            MEMORY_DIR, (safe_id or "default") + ".json"
        )

        if not os.path.exists(self.memory_file):
            self.save([])

    def load(self):
        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, memory):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        temp_file = self.memory_file + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(memory, file, ensure_ascii=False, indent=2)

        os.replace(temp_file, self.memory_file)

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
