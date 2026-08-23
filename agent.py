"""
agent.py — Zugo.ai main brain.

Talks to a local Ollama model (free, private, runs on your PC), and gives it
tools: web search, document reading, and persistent memory.

Run: python3 agent.py
Requires Ollama running in the background (it auto-starts after install).
"""

import requests
import json
import storage
import web_search
import document_reader

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"   # change to "llama3.2:3b" if your PC is low-spec

SYSTEM_PROMPT = """You are Zugo, a private personal AI agent running entirely on the
user's own computer. You think step by step, are honest about uncertainty, and use
the tools available to you (web search, document reading, memory) when they would help.
Keep answers clear and useful. Never invent facts you weren't given or didn't search for."""


def ask_ollama(prompt, context=""):
    """Send a prompt to the local model and get its reply."""
    full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser: {prompt}\nZugo:"
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"].strip()


def build_context():
    """Pull recent chat history + saved facts so Zugo has memory across turns."""
    facts = storage.recall_facts()
    history = storage.get_recent_history(limit=6)

    context_parts = []
    if facts:
        context_parts.append("Known facts about the user/project:\n" +
                              "\n".join(f"- {k}: {v}" for k, v in facts.items()))
    if history:
        hist_lines = [f"{h['role']}: {h['content']}" for h in history]
        context_parts.append("Recent conversation:\n" + "\n".join(hist_lines))

    return "\n\n".join(context_parts)


def handle_input(user_input):
    """Route input to the right tool, or just chat."""

    if user_input.lower().startswith("search:"):
        query = user_input.split(":", 1)[1].strip()
        print(f"\n[Zugo is searching the web for: {query}]\n")
        results = web_search.search_web(query)
        results_text = web_search.format_results_for_model(results)
        reply = ask_ollama(
            f"Based on these search results, answer the user's original question: '{query}'\n\n{results_text}"
        )
        return reply

    elif user_input.lower().startswith("read:"):
        path = user_input.split(":", 1)[1].strip()
        print(f"\n[Zugo is reading: {path}]\n")
        content = document_reader.read_document(path)
        # Truncate very long docs so it fits in the model's context window
        content_snippet = content[:6000]
        reply = ask_ollama(
            f"Summarize and extract the key information from this document:\n\n{content_snippet}"
        )
        return reply

    elif user_input.lower().startswith("remember:"):
        # format: remember: key = value
        try:
            body = user_input.split(":", 1)[1]
            key, value = body.split("=", 1)
            storage.remember_fact(key.strip(), value.strip())
            return f"Got it, I'll remember that {key.strip()} = {value.strip()}."
        except ValueError:
            return "Use the format: remember: key = value"

    else:
        context = build_context()
        return ask_ollama(user_input, context)


def main():
    print("=" * 50)
    print(" Zugo.ai — your private local AI agent")
    print(" Type 'search: <query>' to research the web")
    print(" Type 'read: <filepath>' to extract a document")
    print(" Type 'remember: key = value' to save a fact")
    print(" Type 'exit' to quit")
    print("=" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Zugo: Goodbye. Everything we discussed is saved locally in memory/.")
            break

        storage.log_message("user", user_input)
        reply = handle_input(user_input)
        storage.log_message("zugo", reply)
        print(f"\nZugo: {reply}")


if __name__ == "__main__":
    main()
