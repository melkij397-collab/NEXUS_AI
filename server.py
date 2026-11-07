
import os
import logging
import requests

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".")

logging.basicConfig(level=logging.INFO)

API_URL = "https://router.huggingface.co/v1/chat/completions"

# Модель и провайдер
MODEL = "Qwen/Qwen2.5-7B-Instruct:featherless-ai"


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    token = os.getenv("HF_TOKEN")

    if not token:
        return jsonify({
            "error": "Не настроен токен HF_TOKEN"
        }), 500

    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not isinstance(messages, list) or not messages:
        return jsonify({
            "error": "Сообщения не найдены"
        }), 400

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            app.logger.error(
                "Hugging Face error: %s %s",
                response.status_code,
                response.text[:1000]
            )

            return jsonify({
                "error": "Ошибка Hugging Face",
                "details": response.text[:1000]
            }), response.status_code

        result = response.json()

        choices = result.get("choices", [])

        if not choices:
            return jsonify({
                "error": "Модель вернула пустой ответ"
            }), 502

        answer = choices[0].get("message", {}).get("content", "")

        if not answer:
            return jsonify({
                "error": "Пустой ответ модели"
            }), 502

        return jsonify({
            "reply": answer
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Превышено время ожидания ответа"
        }), 504

    except requests.exceptions.RequestException:
        app.logger.exception("Ошибка соединения")
        return jsonify({
            "error": "Не удалось подключиться к Hugging Face"
        }), 502

    except Exception:
        app.logger.exception("Внутренняя ошибка")
        return jsonify({
            "error": "Внутренняя ошибка сервера"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

