from flask import Flask, jsonify
import os
import requests

app = Flask(__name__)

TOKEN = os.environ.get("RUBIKA_TOKEN")
BASE_URL = f"https://botapi.rubika.ir/v3/{TOKEN}"


@app.route("/")
def home():
    return "Rubika bot server is running!"


@app.route("/check")
def check():
    if not TOKEN:
        return jsonify({"error": "Token is missing"}), 500

    try:
        response = requests.post(
            f"{BASE_URL}/getMe",
            json={},
            timeout=15
        )
        return jsonify(response.json())

    except Exception:
        return jsonify({"error": "Connection failed"}), 502


@app.route("/updates")
def updates():
    if not TOKEN:
        return jsonify({"error": "Token is missing"}), 500

    try:
        response = requests.post(
            f"{BASE_URL}/getUpdates",
            json={"limit": 10},
            timeout=15
        )

        result = response.json()
        chats = []

        for update in result.get("data", {}).get("updates", []):
            chats.append({
                "chat_id": update.get("chat_id"),
                "type": update.get("type")
            })

        return jsonify({"chats": chats})

    except Exception:
        return jsonify({"error": "Connection failed"}), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
