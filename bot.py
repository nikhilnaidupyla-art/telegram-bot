import os
import requests
import google.generativeai as genai
from flask import Flask, request
import threading

# ✏️ Fill these in
TELEGRAM_TOKEN = "8711220932:AAG7YkP69uz9oMqTebvWaXWbsDc8jVhOFXU"
GEMINI_API_KEY = GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
YOUR_NAME = "Nik"
BOT_NAME = "rabbit"

# Set up Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

SYSTEM_PROMPT = f"""You are {BOT_NAME}, {YOUR_NAME}'s personal AI assistant on Telegram.
You are helpful, friendly, and concise.
If anyone asks for {YOUR_NAME}'s contact, tell them to reach out via Telegram.
Never pretend to be a human. Always add a 🤖 emoji at the end of replies."""

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def process_and_reply(chat_id, user_text):
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_text}\n{BOT_NAME}:"
        response = model.generate_content(full_prompt)
        reply = response.text
        send_message(chat_id, reply)
    except Exception as e:
        send_message(chat_id, "Sorry, I'm having trouble right now. Try again in a moment! 🤖")
        print(f"Error: {e}")

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_text = message["text"]

        # ✅ Reply to Telegram instantly so it doesn't timeout
        thread = threading.Thread(target=process_and_reply, args=(chat_id, user_text))
        thread.start()

    except Exception as e:
        print(f"Error: {e}")

    # ✅ This returns immediately — no more timeout!
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)