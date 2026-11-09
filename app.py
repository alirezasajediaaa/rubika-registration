from flask import Flask, request, jsonify, send_from_directory
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("RUBIKA_TOKEN")
CHAT_ID = os.environ.get("RUBIKA_CHAT_ID")

RUBIKA_URL = (
    f"https://botapi.rubika.ir/v3/{TOKEN}/sendMessage"
    if TOKEN else None
)


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/check")
def check():
    if not TOKEN:
        return jsonify({"error": "RUBIKA_TOKEN تنظیم نشده"}), 500

    try:
        response = requests.post(
            f"https://botapi.rubika.ir/v3/{TOKEN}/getMe",
            json={},
            timeout=15
        )

        return jsonify(response.json()), response.status_code

    except requests.RequestException as e:
        print("GETME ERROR:", repr(e), flush=True)
        return jsonify({"error": "اتصال به روبیکا برقرار نشد"}), 502


@app.route("/submit", methods=["POST"])
def submit():

    print("SUBMIT REQUEST RECEIVED", flush=True)

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    username = str(data.get("username", "")).strip()
    invite_code = str(data.get("invite_code", "")).strip()
    consent = data.get("consent")

    if not name or not username or not invite_code:
        return jsonify({
            "success": False,
            "error": "همه فیلدها را تکمیل کن"
        }), 400

    if len(name) > 60 or len(username) > 60 or len(invite_code) > 60:
        return jsonify({
            "success": False,
            "error": "طول اطلاعات بیش از حد مجاز است"
        }), 400

    if consent is not True:
        return jsonify({
            "success": False,
            "error": "رضایت ارسال اطلاعات لازم است"
        }), 400

    if not TOKEN or not CHAT_ID:
        print("ENVIRONMENT VARIABLE MISSING", flush=True)

        return jsonify({
            "success": False,
            "error": "تنظیمات سرور کامل نیست"
        }), 500

    message = (
        "ثبت‌نام جدید\n\n"
        f"نام: {name}\n"
        f"نام کاربری: {username}\n"
        f"کد دعوت: {invite_code}"
    )

    try:
        response = requests.post(
            RUBIKA_URL,
            json={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=20
        )

        try:
            result = response.json()
        except ValueError:
            result = {"raw_response": response.text[:500]}

        print("RUBIKA HTTP STATUS:", response.status_code, flush=True)
        print("RUBIKA RESPONSE:", result, flush=True)

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": "خطای HTTP از روبیکا",
                "details": result
            }), 502

        if result.get("status") != "OK":
            return jsonify({
                "success": False,
                "error": "روبیکا پیام را قبول نکرد",
                "details": result
            }), 502

        return jsonify({
            "success": True,
            "message": "اطلاعات با موفقیت ارسال شد"
        })

    except requests.RequestException as e:
        print("RUBIKA CONNECTION ERROR:", repr(e), flush=True)

        return jsonify({
            "success": False,
            "error": "ارتباط با روبیکا برقرار نشد"
        }), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
