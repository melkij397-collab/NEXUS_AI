import os
import logging

from flask import Flask, request, jsonify, send_from_directory
from core.brain import NexusBrain

app = Flask(__name__, static_folder=".")
logging.basicConfig(level=logging.INFO)

nexus = NexusBrain()


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "Напиши сообщение"}), 400

    user_message = None

    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            user_message = message.get("content")
            break

    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({"error": "Пустое сообщение"}), 400

    try:
        result = nexus.process(user_message)

        return jsonify({
            "reply": result["reply"],
            "name": result["name"],
            "version": result["version"],
            "category": result["category"]
        })

    except Exception:
        app.logger.exception("Ошибка NEXUS AI")
        return jsonify({
            "error": "Внутренняя ошибка NEXUS AI"
        }), 500


@app.route("/api/status")
def status():
    return jsonify({
        "name": "NEXUS AI",
        "status": "online",
        "engine": "NEXUS Brain",
        "version": "1.0.0"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
