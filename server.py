"""
server.py — turns Zugo into a website you access in your browser.
This is a Flask web server (pure Python) that connects your chat page to
your existing agent.py logic (Ollama + search + documents + memory).

Run: py -3.12 server.py
Then open your browser to: http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template
import storage
import web_search
import document_reader
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"

SYSTEM_PROMPT = """You are Zugo, a private personal AI agent running entirely on the
user's own computer. You think step by step, are honest about uncertainty, and use
the tools available to you (web search, document reading, memory) when they would help.
Keep answers clear and useful. Never invent facts you weren't given or didn't search for."""


def ask_ollama(prompt, context=""):
    full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser: {prompt}\nZugo:"
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"].strip()


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
        reply = ask_ollama(f"Based on these search results, answer: '{query}'\n\n{results_text}")
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
        reply = ask_ollama(user_input, context)

    storage.log_message("zugo", reply)
    return jsonify({"reply": reply})


@app.route("/api/upload", methods=["POST"])
def upload():
    """Handles document uploads from the browser, with an optional custom instruction."""
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

    reply = ask_ollama(prompt)

    storage.log_message("user", f"[uploaded document: {file.filename}] {instruction}".strip())
    storage.log_message("zugo", reply)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    print("Zugo.ai web server starting...")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, port=5000)
