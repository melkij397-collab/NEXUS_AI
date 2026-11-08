from core.memory import NexusMemory
from core.router import NexusRouter


class NexusBrain:
    def __init__(self):
        self.memory = NexusMemory()
        self.router = NexusRouter()
        self.name = "NEXUS AI"
        self.version = "1.0.0"

    def process(self, message):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Пустое сообщение")

        message = message.strip()
        category = self.router.route(message)

        self.memory.add("user", message)
        response = self.generate_response(message, category)
        self.memory.add("assistant", response)

        return {
            "name": self.name,
            "version": self.version,
            "category": category,
            "reply": response
        }

    def generate_response(self, message, category):
        responses = {
            "chat": "Привет! Я NEXUS AI. Я готов общаться и помогать тебе.",
            "think": "Я получил задачу для анализа. Модуль рассуждений NEXUS готовится.",
            "code": "Запрос направлен в NEXUS CODE. Модуль программирования готовится.",
            "vision": "Запрос направлен в NEXUS VISION. Модуль обработки изображений готовится.",
            "documents": "Запрос направлен в NEXUS DOCS. Модуль документов готовится."
        }

        return responses.get(category, "NEXUS AI получил твоё сообщение.")
