import os
import requests
from dotenv import load_dotenv

load_dotenv()


class NexusLLM:
    def __init__(self):
        self.token = os.getenv("OPENROUTER_API_KEY")
        self.model = "openrouter/free"
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, question, context=""):
        if not self.token:
            return "Ошибка: OPENROUTER_API_KEY не найден."

        try:
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://nexus-ai-d4of.onrender.com",
                    "X-Title": "NEXUS AI"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты NEXUS AI — интеллектуальный помощник. Отвечай на русском языке, понятно и точно."
                        },
                        {
                            "role": "user",
                            "content": f"Вопрос: {question}\n\nКонтекст: {context}"
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1200
                },
                timeout=120
            )

            if response.status_code != 200:
                return f"Ошибка OpenRouter HTTP {response.status_code}: {response.text[:1000]}"

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.RequestException as error:
            return f"Ошибка соединения: {error}"
        except (KeyError, ValueError, IndexError) as error:
            return f"Ошибка ответа модели: {error}"
