from core.memory import NexusMemory
from core.memory_engine import NexusMemoryEngine
from core.router import NexusRouter
from modules.llm import NexusLLM
from modules.web import NexusWeb


class NexusBrain:
    def __init__(self, session_id="default"):
        self.name = "Flint"
        self.version = "6.0.0"

        self.memory = NexusMemory(session_id)
        self.long_term_memory = NexusMemoryEngine(session_id)
        self.router = NexusRouter()
        self.llm = NexusLLM()
        self.web = NexusWeb()

    def process(self, message):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Пустое сообщение")

        message = message.strip()
        history = self.memory.get_history(limit=12)
        category = self.router.route(message)

        search_data = self.web.search(message)
        search_context = ""

        if isinstance(search_data, dict):
            if search_data.get("status") == "success":
                search_context = "\n".join(
                    f"{item.get('title', '')}: {item.get('text', '')}"
                    for item in search_data.get("results", [])
                )

        memory_facts = self.long_term_memory.list_facts(limit=30)
        memory_lines = []

        for fact in memory_facts:
            memory_lines.append(
                f"[{fact['category']}] {fact['content']}"
            )

        context_parts = []

        if memory_lines:
            context_parts.append(
                "Сохранённые факты о пользователе:\n"
                + "\n".join(memory_lines)
            )

        if search_context:
            context_parts.append(
                "Результаты веб-поиска:\n" + search_context
            )

        memory_context = "\n\n".join(context_parts)

        response = self.llm.generate(
            message,
            context=history,
            memory_context=memory_context
        )

        self.memory.add("user", message)
        self.memory.add("assistant", response)

        return {
            "name": self.name,
            "version": self.version,
            "category": category,
            "reply": response
        }
