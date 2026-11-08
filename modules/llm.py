import os
import requests
from dotenv import load_dotenv

load_dotenv()


class NexusLLM:
    def __init__(self):
        self.token = os.getenv("OPENROUTER_API_KEY")
        self.model = "nvidia/nemotron-3-ultra-550b-a55b:free"
        self.url = "https://openrouter.ai/api/v1/chat/completions"

        self.system_prompt = """
Ты — NEXUS AI, интеллектуальный универсальный помощник.

Твои задачи:
1. Понимать смысл вопросов и намерения пользователя.
2. Давать точные, полезные и понятные ответы.
3. Объяснять сложные темы простыми словами.
4. Учитывать предыдущие сообщения диалога.
5. Помогать с программированием, анализом и обучением.
6. Если не знаешь ответа, честно сообщать об этом.
7. Не выдумывать факты и источники.
8. Отвечать на языке пользователя, по умолчанию на русском.
9. Использовать структуру и примеры, когда это помогает.
10. Не повторять вопрос без необходимости.

Ты должен быть вежливым, логичным и последовательным.
"""

    def generate(self, question, context=None):
        if not self.token:
            return "Ошибка: OPENROUTER_API_KEY не найден."

        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        if isinstance(context, list):
            for item in context[-12:]:
                if not isinstance(item, dict):
                    continue

                role = item.get("role")
                content = item.get("content")

                if role in ("user", "assistant") and isinstance(content, str):
                    messages.append({
                        "role": role,
                        "content": content[:4000]
                    })

        elif isinstance(context, str) and context.strip():
            messages.append({
                "role": "system",
                "content": "Дополнительный контекст:\n" + context[:8000]
            })

        messages.append({
            "role": "user",
            "content": question
        })

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
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500
                },
                timeout=120
            )

            if response.status_code != 200:
                return (
                    f"Ошибка OpenRouter HTTP {response.status_code}. "
                    "Попробуй повторить запрос позже."
                )

            data = response.json()
            answer = data["choices"][0]["message"]["content"]

            if not isinstance(answer, str) or not answer.strip():
                return "Модель вернула пустой ответ. Попробуй ещё раз."

            return answer.strip()

        except requests.Timeout:
            return "Превышено время ожидания ответа. Попробуй ещё раз."

        except requests.RequestException:
            return "Ошибка соединения с OpenRouter."

        except (KeyError, ValueError, IndexError, TypeError):
            return "Не удалось обработать ответ языковой модели."
