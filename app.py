from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("RUBIKA_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")


@app.route("/")
def home():
    return "Server is running!"


@app.route("/submit", methods=["POST"])
def submit():
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        return jsonify({"error": "Server configuration missing"}), 500

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    username = str(data.get("username", "")).strip()
    invite_code = str(data.get("invite_code", "")).strip()

    if not name or not username or not invite_code:
        return jsonify({"error": "Please fill in all fields"}), 400

    message = (
        "ثبت‌نام جدید\n\n"
        f"نام: {name}\n"
        f"نام کاربری: {username}\n"
        f"کد دعوت: {invite_code}"
    )

    try:
        response = requests.post(
            f"https://botapi.rubika.ir/v3/{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_CHAT_ID,
                "text": message
            },
            timeout=15
        )
        result = response.json()

        if result.get("status") != "OK":
            return jsonify({"error": "Rubika message failed"}), 502

        return jsonify({"success": True})

    except Exception:
        return jsonify({"error": "Could not contact Rubika"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
