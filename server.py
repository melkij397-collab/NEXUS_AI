import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".")

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "Qwen/Qwen2.5-7B-Instruct"

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    token = os.getenv("HF_TOKEN")

    if not token:
        return jsonify({"error": "Не настроен HF_TOKEN"}), 500

    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "Сообщения не найдены"}), 400

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
            return jsonify({
                "error": "Ошибка Hugging Face",
                "details": response.text[:1000]
            }), response.status_code

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        return jsonify({"reply": answer})

    except requests.exceptions.Timeout:
        return jsonify({"error": "Превышено время ожидания"}), 504

    except Exception as error:
        app.logger.exception("Ошибка сервера")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
