# Zugo — a private personal AI agent, built from scratch

Created by **Madhav Dua**.

Zugo is a personal AI agent with two ways to run it: fully offline on your own
computer, or live on the internet for free. It can chat, research the web,
read documents, see photos (via text extraction), listen to your voice, and
speak its replies back — all built on a zero-budget stack.

---

## What Zugo can do

- **Chat naturally** — no special commands needed. Just talk to it like you
  would talk to Claude or ChatGPT.
- **Search the web on its own** — when a question needs current information,
  Zugo decides to search automatically, using real-time function calling.
- **Remember things** — tell it something worth remembering, and it saves that
  fact permanently, recalling it in future conversations.
- **Read documents** — PDF, Word (.docx), PowerPoint (.pptx), and plain text
  files. Drop them in or upload from the chat.
- **Read text out of photos** — camera capture or image upload, with OCR
  extracting any text inside the image.
- **Voice input** — tap the mic and speak; your words are transcribed straight
  into the chat box.
- **Voice output** — Zugo can read its replies aloud.
- **Mobile-friendly** — the web interface adapts to phone screens, with
  drag-and-drop and camera capture built in.
- **Private local memory** — when run locally, everything is stored as plain
  files on your own machine. Nothing leaves your computer except web searches.

---

## Two ways to run Zugo

### 1. Local (fully offline, completely free, totally private)

Uses [Ollama](https://ollama.com) running a local open-source model
(Llama 3.1) directly on your computer. No internet needed except for web
search. Nothing is sent to any company's servers.

**Setup:**
```
py -3.12 -m pip install -r requirements.txt
```
Install Ollama, then pull a model:
```
ollama pull llama3.1
```
Run the chat website:
```
py -3.12 server.py
```
Open your browser to `http://localhost:5000`

Or launch the terminal-only version instead of the website:
```
py -3.12 agent.py
```

### 2. Cloud (live on the internet, free tier, always accessible)

Uses [Groq](https://console.groq.com)'s free API instead of a local model, so
the site works from any device, anywhere, without your computer needing to be
on. Deployed for free on [Render](https://render.com).

See `DEPLOY_GUIDE.md` for the full step-by-step deployment walkthrough.

**Setup:**
```
py -3.12 -m pip install -r requirements-cloud.txt
```
Set your free Groq API key as an environment variable, then run:
```
py -3.12 cloud_server.py
```

---

## Project structure

```
zugo_ai/
  agent.py              # terminal-only local agent (Ollama)
  server.py              # local website backend (Ollama)
  cloud_server.py        # live/cloud website backend (Groq)
  storage.py              # local file-based memory system
  web_search.py            # free web search (DuckDuckGo, no API key)
  document_reader.py        # reads PDF / Word / PowerPoint / images (OCR)
  templates/
    index.html               # the chat website (dark UI, mobile-friendly)
  requirements.txt              # dependencies for the local version
  requirements-cloud.txt         # dependencies for the cloud version
  Procfile                        # tells Render how to start the app
  start_zugo.bat                   # one-click launcher (Windows, local version)
  DEPLOY_GUIDE.md                   # step-by-step guide to going live for free
  PORTABILITY_GUIDE.md               # running Zugo from a pendrive, offline use
  memory/                             # Zugo's saved facts and chat history (local only)
  documents/                           # uploaded files land here (local only)
```

---

## Tech stack (100% free)

| Piece | Tool |
|---|---|
| Local AI brain | Ollama + Llama 3.1 |
| Cloud AI brain | Groq free API (Llama 3.3 70B) |
| Web framework | Flask |
| Web research | duckduckgo-search |
| Document reading | pdfplumber, python-docx, python-pptx |
| Image OCR | pytesseract + Pillow |
| Voice input/output | Browser Web Speech API |
| Cloud hosting | Render (free tier) |
| Version control | GitHub |

---

## Notes

- The cloud version's free hosting tier sleeps after periods of inactivity;
  the first visitor after a quiet spell waits ~20-30 seconds for it to wake up.
- Local memory (facts, chat history) only persists on whichever machine is
  running the local version — the cloud version's memory resets on redeploy.
- Voice features work best in Chrome or Edge.

---

Built from scratch, zero budget, by Madhav Dua.
