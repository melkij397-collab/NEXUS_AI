from core.memory import NexusMemory
from core.router import NexusRouter
from modules.llm import NexusLLM
from modules.web import NexusWeb


class NexusBrain:
    def __init__(self):
        self.name = "NEXUS AI"
        self.version = "5.0.0"

        self.memory = NexusMemory()
        self.router = NexusRouter()
        self.llm = NexusLLM()
        self.web = NexusWeb()

    def process(self, message):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Пустое сообщение")

        message = message.strip()

        # Загружаем предыдущую историю
        history = self.memory.get_history(limit=12)

        # Определяем категорию запроса
        category = self.router.route(message)

        # Получаем дополнительную информацию
        search_data = self.web.search(message)
        search_context = ""

        if isinstance(search_data, dict):
            if search_data.get("status") == "success":
                search_context = "\n".join(
                    f"{item['title']}: {item['text']}"
                    for item in search_data.get("results", [])
                )

        # Передаём модели историю отдельными сообщениями
        context = history

        if search_context:
            context = history + [{
                "role": "system",
                "content": "Результаты веб-поиска:\n" + search_context
            }]

        # Генерируем ответ
        response = self.llm.generate(
            message,
            context=context
        )

        # Сохраняем диалог
        self.memory.add("user", message)
        self.memory.add("assistant", response)

        return {
            "name": self.name,
            "version": self.version,
            "category": category,
            "reply": response
        }
