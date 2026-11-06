
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"

SYSTEM_PROMPT = """
You are GP Chat, a smart AI assistant created by Gaurav Pathak.

Detect the user's language automatically.
English -> English
Hindi -> Hindi
Hinglish -> Hinglish

Be polite, helpful, friendly and clear.

If asked about your creator, reply exactly:
I was created by Gaurav Pathak.
"""

conversation = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            print("ERROR: API key missing")
            return jsonify({"reply": "API key not configured."}), 503

        data = request.get_json(silent=True) or {}
        user_msg = data.get("message", "").strip()

        if not user_msg:
            return jsonify({"reply": "Message empty hai."})

        msg_lower = user_msg.lower()

        creator_triggers = [
            "who made you",
            "who created you",
            "creator kaun",
            "kisne banaya",
            "tumhara creator"
        ]

        if any(t in msg_lower for t in creator_triggers):
            return jsonify({
                "reply": "I was created by Gaurav Pathak."
            })

        conversation.append({
            "role": "user",
            "content": user_msg
        })

        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://openrouter.ai",
                "X-Title": "GP Chat"
            },
            json={
                "model": MODEL,
                "messages": conversation,
                "temperature": 0.6
            },
            timeout=60
        )

        print("OpenRouter Status:", response.status_code)

        if response.status_code != 200:
            print("OpenRouter Error:", response.text[:1000])
            conversation.pop()

            return jsonify({
                "reply": f"AI API error (HTTP {response.status_code}). Check server logs."
            }), 502

        result = response.json()

        if "choices" not in result or not result["choices"]:
            print("Invalid API response:", str(result)[:1000])
            conversation.pop()

            return jsonify({
                "reply": "AI returned an invalid response."
            }), 502

        reply = result["choices"][0]["message"]["content"]

        if not reply:
            conversation.pop()
            return jsonify({"reply": "AI returned an empty response."}), 502

        conversation.append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({"reply": reply})

    except requests.exceptions.Timeout:
        print("ERROR: OpenRouter request timed out")
        if len(conversation) > 1 and conversation[-1]["role"] == "user":
            conversation.pop()

        return jsonify({"reply": "AI response timeout. Please try again."}), 504

    except requests.exceptions.RequestException as e:
        print("NETWORK ERROR:", str(e))
        if len(conversation) > 1 and conversation[-1]["role"] == "user":
            conversation.pop()

        return jsonify({"reply": "AI connection failed."}), 502

    except Exception as e:
        print("SERVER ERROR:", repr(e))
        if len(conversation) > 1 and conversation[-1]["role"] == "user":
            conversation.pop()

        return jsonify({"reply": "Server error. Check server logs."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

