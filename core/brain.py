from core.memory import NexusMemory
from core.router import NexusRouter
from modules.llm import NexusLLM
from modules.web import NexusWeb


class NexusBrain:
    def __init__(self):
        self.name = "NEXUS AI"
        self.version = "4.0.0"

        self.memory = NexusMemory()
        self.router = NexusRouter()
        self.llm = NexusLLM()
        self.web = NexusWeb()

    def process(self, message):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Пустое сообщение")

        message = message.strip()
        history = self.memory.get_history(limit=10)

        context = "\n".join(
            f"{item['role']}: {item['content']}"
            for item in history
        )

        category = self.router.route(message)
        search_data = self.web.search(message)

        search_context = ""

        if isinstance(search_data, dict) and search_data.get("status") == "success":
            search_context = "\n".join(
                f"{item['title']}: {item['text']}"
                for item in search_data.get("results", [])
            )

        full_context = (
            f"История диалога:\n{context}\n\n"
            f"Результаты поиска:\n{search_context}"
        )

        response = self.llm.generate(
            message,
            context=full_context
        )

        self.memory.add("user", message)
        self.memory.add("assistant", response)

        return {
            "name": self.name,
            "version": self.version,
            "category": category,
            "reply": response
        }
