from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# 🔹 Load .env file
load_dotenv()

app = Flask(__name__)

# 🔹 API Key (env se)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🔹 Safety check
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found. Check your .env file.")

# 🔹 Conversation memory
conversation = [
    {
        "role": "system",
        "content": (
            "You are GP Chat, a smart AI assistant.\n"
            "Detect user's language automatically.\n"
            "English → English\n"
            "Hindi → Hindi\n"
            "Hinglish → Hinglish\n"
            "Be polite, helpful, and clear.\n"
            "If asked about your creator, always reply exactly:\n"
            "'I was created by Gaurav Pathak.'"
        )
    }
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.json.get("message", "").strip()

        if not user_msg:
            return jsonify({"reply": "Message empty hai."})

        msg_lower = user_msg.lower()

        # 🔒 HARD CREATOR FIX (ALL LANGUAGES)
        creator_triggers = [
            # English
            "who made you",
            "who created you",
            "who is your creator",
            "your creator",
            "made you",
            "created you",
            "who built you",
            "who developed you",

            # Hindi / Hinglish
            "kisne banaya",
            "tumhe kisne banaya",
            "tumko kisne banaya",
            "banaya kisne",
            "creator kaun hai",
            "tumhara creator kaun",
            "tumhara malik kaun"
        ]

        if any(trigger in msg_lower for trigger in creator_triggers):
            return jsonify({
                "reply": "I was created by Gaurav Pathak."
            })

        # 🔹 Normal conversation
        conversation.append({
            "role": "user",
            "content": user_msg
        })

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": conversation,
                "temperature": 0.6
            },
            timeout=30
        )

        data = response.json()

        # 🔴 Error safety
        if "choices" not in data:
            return jsonify({"reply": "AI service error. Try again."})

        bot_reply = data["choices"][0]["message"]["content"]

        conversation.append({
            "role": "assistant",
            "content": bot_reply
        })

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "AI service error"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
