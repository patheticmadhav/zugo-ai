"""
storage.py — Zugo's local memory system.
No server, no database software needed. Just plain files on your drive.
Everything is stored under memory/ as JSON, so it's human-readable and private.
"""

import json
import os
from datetime import datetime

MEMORY_DIR = "memory"
CONVO_FILE = os.path.join(MEMORY_DIR, "conversations.json")
FACTS_FILE = os.path.join(MEMORY_DIR, "facts.json")


def _ensure_files():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    for f in (CONVO_FILE, FACTS_FILE):
        if not os.path.exists(f):
            with open(f, "w") as fp:
                json.dump([], fp)


def _load(path):
    _ensure_files()
    with open(path, "r") as fp:
        return json.load(fp)


def _save(path, data):
    with open(path, "w") as fp:
        json.dump(data, fp, indent=2)


def log_message(role, content):
    """Save every chat turn so Zugo has a permanent record on disk."""
    convos = _load(CONVO_FILE)
    convos.append({
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content": content
    })
    _save(CONVO_FILE, convos)


def remember_fact(key, value):
    """Store a specific fact Zugo should recall later, e.g. remember_fact('user_goal', 'build a trading bot')."""
    facts = _load(FACTS_FILE)
    facts = [f for f in facts if f["key"] != key]  # overwrite if exists
    facts.append({"key": key, "value": value, "saved_at": datetime.now().isoformat()})
    _save(FACTS_FILE, facts)


def recall_facts():
    """Return all stored facts as a dict for injecting into the LLM's context."""
    facts = _load(FACTS_FILE)
    return {f["key"]: f["value"] for f in facts}


def get_recent_history(limit=10):
    """Get the last N chat turns to give the model short-term memory."""
    convos = _load(CONVO_FILE)
    return convos[-limit:]
