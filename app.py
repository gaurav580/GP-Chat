from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 Railway ENV variable
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set")

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
        data = request.get_json()
        user_msg = data.get("message", "").strip()

        if not user_msg:
            return jsonify({"reply": "Message empty hai."})

        msg_lower = user_msg.lower()

        creator_triggers = [
            "who made you", "who created you",
            "creator kaun", "kisne banaya",
            "tumhara creator"
        ]

        if any(t in msg_lower for t in creator_triggers):
            return jsonify({"reply": "I was created by Gaurav Pathak."})

        conversation.append({"role": "user", "content": user_msg})

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

        result = response.json()

        reply = result["choices"][0]["message"]["content"]
        conversation.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "Server error"})

# 🚀 Railway entrypoint
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
