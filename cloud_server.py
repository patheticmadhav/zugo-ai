"""
cloud_server.py — the cloud-hosted version of Zugo.
Talks to Groq's free cloud API. Uses "function calling" so Zugo decides on its
own, from normal conversation, when to search the web or save a memory —
no more typing 'search:' or 'remember:' prefixes.
"""

import os
import json
from flask import Flask, request, jsonify, render_template
import storage
import web_search
import document_reader
import requests

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

ALLOWED_MODELS = {
    "llama-3.3-70b-versatile",
    "moonshotai/kimi-k2-instruct",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3-32b",
    "openai/gpt-oss-20b",
}

SYSTEM_PROMPT = """You are Zugo, a private personal AI agent created by Madhav Dua.
Think step by step, be honest about uncertainty, and use your tools (web search,
saving memories) whenever they'd genuinely help — decide this yourself from the
conversation, the user will never type special commands. Keep answers concise and
direct. Never invent facts you weren't given or didn't search for."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the live internet for current information, facts, prices, news, or anything you're unsure about or that may have changed recently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": "Save a specific fact about the user permanently, so it can be recalled in future conversations. Use this whenever the user tells you something worth remembering long-term (their name, preferences, ongoing projects, important dates, etc).",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Short label for the fact, e.g. 'user_name' or 'favorite_color'"},
                    "value": {"type": "string", "description": "The fact itself"}
                },
                "required": ["key", "value"]
            }
        }
    }
]


def call_groq(messages, tools=None, model=DEFAULT_MODEL):
    if model not in ALLOWED_MODELS:
        model = DEFAULT_MODEL
    payload = {"model": model, "messages": messages, "temperature": 0.6, "max_tokens": 700}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json=payload,
        timeout=90
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]


def run_tool(name, args):
    if name == "search_web":
        results = web_search.search_web(args.get("query", ""))
        return web_search.format_results_for_model(results)
    elif name == "remember_fact":
        storage.remember_fact(args.get("key", ""), args.get("value", ""))
        return f"Saved: {args.get('key')} = {args.get('value')}"
    return "Unknown tool."


def ask_ai(user_prompt, extra_context="", model=DEFAULT_MODEL):
    if not GROQ_API_KEY:
        return "Zugo isn't fully set up yet: GROQ_API_KEY is missing on the server."

    facts = storage.recall_facts()
    history = storage.get_recent_history(limit=6)

    context_lines = []
    if facts:
        context_lines.append("Known facts about the user:\n" + "\n".join(f"- {k}: {v}" for k, v in facts.items()))
    if extra_context:
        context_lines.append(extra_context)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context_lines:
        messages.append({"role": "system", "content": "\n\n".join(context_lines)})
    for h in history:
        role = "assistant" if h["role"] == "zugo" else "user"
        messages.append({"role": role, "content": h["content"]})
    messages.append({"role": "user", "content": user_prompt})

    msg = call_groq(messages, tools=TOOLS, model=model)

    # If the model wants to use a tool, run it and let the model finish its answer
    if msg.get("tool_calls"):
        messages.append(msg)
        for call in msg["tool_calls"]:
            args = json.loads(call["function"]["arguments"])
            result = run_tool(call["function"]["name"], args)
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result
            })
        final = call_groq(messages, model=model)  # no tools needed on the follow-up
        return final["content"].strip()

    return msg["content"].strip()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/models")
def list_models():
    labels = {
        "llama-3.3-70b-versatile": "Llama 3.3 70B — best overall",
        "moonshotai/kimi-k2-instruct": "Kimi K2 — latest, strong reasoning",
        "llama-3.1-8b-instant": "Llama 3.1 8B — fastest",
        "meta-llama/llama-4-scout-17b-16e-instruct": "Llama 4 Scout — latest Llama",
        "qwen/qwen3-32b": "Qwen3 32B",
        "openai/gpt-oss-20b": "GPT-OSS 20B",
    }
    models = [{"value": v, "label": l} for v, l in labels.items()]
    return jsonify({"models": models})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    model = data.get("model", DEFAULT_MODEL)
    if not user_input:
        return jsonify({"reply": "Say something first!"})

    storage.log_message("user", user_input)
    reply = ask_ai(user_input, model=model)
    storage.log_message("zugo", reply)
    return jsonify({"reply": reply})


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"reply": "No file received."})

    file = request.files["file"]
    instruction = request.form.get("instruction", "").strip()
    model = request.form.get("model", DEFAULT_MODEL)
    save_path = f"documents/{file.filename}"
    file.save(save_path)

    content = document_reader.read_document(save_path)
    content_snippet = content[:6000]

    prompt = instruction if instruction else "Summarize and extract the key information from this document."
    extra_context = f"Document content the user just uploaded ({file.filename}):\n{content_snippet}"

    reply = ask_ai(prompt, extra_context=extra_context, model=model)

    storage.log_message("user", f"[uploaded document: {file.filename}] {instruction}".strip())
    storage.log_message("zugo", reply)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

