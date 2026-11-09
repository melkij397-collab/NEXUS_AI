from core.memory import NexusMemory
from core.memory_engine import NexusMemoryEngine
from core.router import NexusRouter
from modules.llm import NexusLLM
from modules.web import NexusWeb


class NexusBrain:
    def __init__(self, session_id="default"):
        self.name = "LIGHT BYTE"
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

        search_context = ""
        search_terms = (
            "найди", "поищи", "поиск", "википедия",
            "википедии", "в интернете"
        )

        if any(term in message.lower() for term in search_terms):
            search_data = self.web.search(message)

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

    def process_stream(self, message):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Пустое сообщение")

        message = message.strip()
        history = self.memory.get_history(limit=12)
        category = self.router.route(message)

        search_context = ""
        search_terms = (
            "найди", "поищи", "поиск", "википедия",
            "википедии", "в интернете"
        )

        if any(term in message.lower() for term in search_terms):
            search_data = self.web.search(message)
            if isinstance(search_data, dict):
                if search_data.get("status") == "success":
                    search_context = "\n".join(
                        f"{item.get('title', '')}: {item.get('text', '')}"
                        for item in search_data.get("results", [])
                    )

        memory_facts = self.long_term_memory.list_facts(limit=30)
        memory_lines = [
            f"[{fact['category']}] {fact['content']}"
            for fact in memory_facts
        ]

        context_parts = [f"Категория запроса: {category}"]

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
        answer_parts = []

        error_prefixes = (
            "Ошибка:",
            "Ошибка OpenRouter HTTP",
            "Превышено время ожидания",
            "Ошибка соединения",
            "Не удалось обработать",
            "Модель вернула пустой ответ"
        )

        for chunk in self.llm.generate_stream(
            message,
            context=history,
            memory_context=memory_context
        ):
            if not isinstance(chunk, str) or not chunk:
                continue

            if not answer_parts and chunk.strip().startswith(error_prefixes):
                raise RuntimeError(chunk.strip())

            answer_parts.append(chunk)
            yield chunk

        full_answer = "".join(answer_parts).strip()

        if not full_answer:
            raise RuntimeError("Модель не вернула ответ")

        self.memory.add("user", message)
        self.memory.add("assistant", full_answer)
