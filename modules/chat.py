class NexusChat:
    def __init__(self):
        self.name = "NEXUS AI"
        self.version = "3.0.0"

    def respond(self, message):
        if not isinstance(message, str) or not message.strip():
            return "Напиши, что тебя интересует."

        text = message.lower().strip()

        if any(x in text for x in ["привет", "здравствуй", "салют"]):
            return "Привет! Я NEXUS AI. Рад помочь. Что будем решать?"

        if "как дела" in text:
            return "Всё работает! Готов помочь тебе."

        if "кто ты" in text:
            return "Я NEXUS AI — твой интеллектуальный помощник."

        if "что умеешь" in text:
            return "Я создан для общения, анализа вопросов, помощи с программированием и решения задач."

        return "Я понял твой вопрос. Расскажи немного подробнее, чтобы я мог помочь."
