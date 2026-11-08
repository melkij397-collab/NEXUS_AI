import os
import logging
import secrets

from flask import Flask, request, jsonify, send_from_directory, session
from core.brain import NexusBrain

app = Flask(__name__, static_folder=".")
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30
)

logging.basicConfig(level=logging.INFO)


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

    if len(user_message) > 10000:
        return jsonify({"error": "Сообщение слишком длинное"}), 413

    if "user_id" not in session:
        session["user_id"] = secrets.token_hex(24)

    session.permanent = True

    try:
        nexus = NexusBrain(session["user_id"])
        result = nexus.process(user_message)

        return jsonify({
            "reply": result["reply"],
            "name": result["name"],
            "version": result["version"],
            "category": result["category"]
        })

    except Exception:
        app.logger.exception("Ошибка Flint")
        return jsonify({
            "error": "Внутренняя ошибка Flint"
        }), 500


@app.route("/api/status")
def status():
    return jsonify({
        "name": "Flint",
        "status": "online",
        "engine": "NEXUS Brain",
        "version": "6.0.0"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
