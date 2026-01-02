from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

conversation = [
    {
        "role": "system",
        "content": """
You are GP Chat, a smart AI assistant.

IMPORTANT RULE:
- Detect the user's language automatically.
- If the user writes in:
  • English → reply in English
  • Hindi → reply in Hindi
  • Hinglish → reply in Hinglish
- NEVER change language unless the user does.
- Be helpful, polite, and clear.
"""
    }
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

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
        }
    )

    data = response.json()
    bot_reply = data["choices"][0]["message"]["content"]

    conversation.append({
        "role": "assistant",
        "content": bot_reply
    })

    return jsonify({"reply": bot_reply})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

