from flask import Flask, request, jsonify, send_from_directory
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("RUBIKA_TOKEN")
CHAT_ID = os.environ.get("RUBIKA_CHAT_ID")

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    username = data.get("username", "").strip()
    invite_code = data.get("invite_code", "").strip()
    consent = data.get("consent")

    if not all([name, username, invite_code]) or consent is not True:
        return jsonify({"error": "اطلاعات ناقص است"}), 400

    if not TOKEN or not CHAT_ID:
        return jsonify({"error": "تنظیمات سرور کامل نیست"}), 500

    message = (
        "ثبت‌نام جدید\n\n"
        f"نام: {name}\n"
        f"نام کاربری: {username}\n"
        f"کد دعوت: {invite_code}"
    )

    try:
        response = requests.post(
            f"https://botapi.rubika.ir/v3/{TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=15
        )

        result = response.json()

        if response.status_code != 200 or result.get("status") != "OK":
            return jsonify({"error": "ارسال پیام ناموفق بود"}), 502

        return jsonify({"success": True})

    except Exception:
        return jsonify({"error": "خطا در ارتباط با روبیکا"}), 502
