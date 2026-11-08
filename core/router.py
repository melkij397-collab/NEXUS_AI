class NexusRouter:
    def __init__(self):
        self.categories = {
            "chat": [
                "привет", "здравствуй", "общение",
                "расскажи", "объясни", "поговорим"
            ],
            "think": [
                "реши", "задача", "вычисли",
                "почему", "рассуждай", "проанализируй"
            ],
            "code": [
                "код", "программа", "python",
                "ошибка", "сайт", "программирование"
            ],
            "vision": [
                "изображение", "фото", "картинка",
                "рисунок", "видео"
            ],
            "documents": [
                "документ", "pdf", "файл",
                "текст", "договор", "документация"
            ]
        }

    def route(self, message):
        text = message.lower()
        scores = {}

        for category, keywords in self.categories.items():
            scores[category] = sum(
                1 for word in keywords if word in text
            )

        best_category = max(scores, key=scores.get)

        if scores[best_category] == 0:
            return "chat"

        return best_category
