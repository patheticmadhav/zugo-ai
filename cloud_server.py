"""
cloud_server.py — the cloud-hosted version of Zugo.
Instead of talking to Ollama on your PC, this talks to Groq's free cloud API,
so the website works even when your laptop is off.

For LOCAL testing before deploying:
  1. Set your Groq key:  set GROQ_API_KEY=gsk_your_key_here   (Windows cmd)
  2. Run: py -3.12 cloud_server.py
  3. Open: http://localhost:5000

For DEPLOYING to Render (see DEPLOY_GUIDE.md), Render sets the environment
variable for you from its dashboard — you never put the key in this file.
"""

import os
from flask import Flask, request, jsonify, render_template
import storage
import web_search
import document_reader
import requests

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"   # free, fast, capable model on Groq

SYSTEM_PROMPT = """You are Zugo, a private personal AI agent created by Madhav Dua.
You think step by step, are honest about uncertainty, and use the tools available to
you (web search, document reading, memory) when they would help. Keep answers clear
and useful. Never invent facts you weren't given or didn't search for."""


def ask_ai(prompt, context=""):
    if not GROQ_API_KEY:
        return "Zugo isn't fully set up yet: the GROQ_API_KEY is missing. Set it as an environment variable and restart."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "system", "content": context})
    messages.append({"role": "user", "content": prompt})

    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={"model": MODEL_NAME, "messages": messages, "temperature": 0.7},
        timeout=60
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def build_context():
    facts = storage.recall_facts()
    history = storage.get_recent_history(limit=6)
    parts = []
    if facts:
        parts.append("Known facts:\n" + "\n".join(f"- {k}: {v}" for k, v in facts.items()))
    if history:
        parts.append("Recent conversation:\n" + "\n".join(f"{h['role']}: {h['content']}" for h in history))
    return "\n\n".join(parts)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Say something first!"})

    storage.log_message("user", user_input)

    if user_input.lower().startswith("search:"):
        query = user_input.split(":", 1)[1].strip()
        results = web_search.search_web(query)
        results_text = web_search.format_results_for_model(results)
        reply = ask_ai(f"Based on these search results, answer: '{query}'\n\n{results_text}")
    elif user_input.lower().startswith("remember:"):
        try:
            body = user_input.split(":", 1)[1]
            key, value = body.split("=", 1)
            storage.remember_fact(key.strip(), value.strip())
            reply = f"Got it, I'll remember that {key.strip()} = {value.strip()}."
        except ValueError:
            reply = "Use the format: remember: key = value"
    else:
        context = build_context()
        reply = ask_ai(user_input, context)

    storage.log_message("zugo", reply)
    return jsonify({"reply": reply})


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"reply": "No file received."})

    file = request.files["file"]
    instruction = request.form.get("instruction", "").strip()
    save_path = f"documents/{file.filename}"
    file.save(save_path)

    content = document_reader.read_document(save_path)
    content_snippet = content[:6000]

    if instruction:
        prompt = f"The user uploaded a document and asked: '{instruction}'\n\nDocument content:\n{content_snippet}"
    else:
        prompt = f"Summarize and extract the key information from this document:\n\n{content_snippet}"

    reply = ask_ai(prompt)

    storage.log_message("user", f"[uploaded document: {file.filename}] {instruction}".strip())
    storage.log_message("zugo", reply)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
