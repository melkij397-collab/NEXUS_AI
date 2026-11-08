class NexusAnswer:
    def __init__(self):
        self.name = "NEXUS ANSWER"

    def create(self, question, search_data):
        if not question:
            return "Задай вопрос."

        results = search_data.get("results", [])

        if not results:
            return (
                "Я пока не нашёл подходящих источников. "
                "Попробуй уточнить вопрос."
            )

        parts = []

        for item in results[:5]:
            title = item.get("title", "")
            text = item.get("text", "")
            url = item.get("url", "")

            parts.append(
                f"Источник: {title}\n"
                f"Информация: {text}\n"
                f"Ссылка: {url}"
            )

        return (
            f"ТВОЙ ВОПРОС:\n{question}\n\n"
            f"НАЙДЕННАЯ ИНФОРМАЦИЯ:\n\n"
            + "\n\n".join(parts)
            + "\n\n"
            "Это предварительный обзор найденных материалов. "
            "Для полноценного анализа нужно подключить языковую модель."
        )
