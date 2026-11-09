import os
import logging
import secrets
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, send_from_directory, session, Response, stream_with_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from core.brain import NexusBrain
from core.load_guard import load_guard
from core.emergency_shield import emergency_shield

load_guard.on_saturation = emergency_shield.activate

app = Flask(__name__, static_folder=".")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri="memory://",
    strategy="fixed-window"
)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30
)

logging.basicConfig(level=logging.INFO)


@app.errorhandler(429)
def rate_limit_error(error):
    return jsonify({"error": "Слишком много запросов. Попробуйте позже."}), 429


@app.before_request
def emergency_shield_check():
    if request.endpoint == "chat" and emergency_shield.is_active():
        response = jsonify({
            "error": "LIGHT BYTE временно перегружен. Попробуйте позже."
        })
        response.status_code = 503
        response.headers["Retry-After"] = "10"
        return response


@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/nexus.css")
def nexus_css():
    return send_from_directory(".", "nexus.css", mimetype="text/css")


@app.route("/api/chat", methods=["POST"])
@limiter.limit("10 per minute")
@load_guard.protect
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
        app.logger.exception("Ошибка LIGHT BYTE")
        return jsonify({
            "error": "Внутренняя ошибка LIGHT BYTE"
        }), 500



@app.route("/api/chat/stream", methods=["POST"])
@limiter.limit("10 per minute")
@load_guard.protect
def chat_stream():
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
    nexus = NexusBrain(session["user_id"])

    def generate():
        import json

        try:
            for chunk in nexus.process_stream(user_message):
                yield "data: " + json.dumps(
                    {"token": chunk}, ensure_ascii=False
                ) + "\n\n"

            yield "data: " + json.dumps(
                {"done": True}, ensure_ascii=False
            ) + "\n\n"

        except Exception:
            app.logger.exception("Ошибка потоковой генерации LIGHT BYTE")
            yield "data: " + json.dumps(
                {"error": "Внутренняя ошибка LIGHT BYTE"},
                ensure_ascii=False
            ) + "\n\n"

    response = Response(
        stream_with_context(generate()),
        mimetype="text/event-stream"
    )
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


@app.route("/api/status")
@limiter.limit("30 per minute")
def status():
    return jsonify({
        "name": "LIGHT BYTE",
        "status": "online",
        "engine": "NEXUS Brain",
        "version": "6.0.0"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
