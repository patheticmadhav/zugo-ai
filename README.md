# Zugo.ai — Build Your Own Local AI Agent (Zero Budget)

This is Phase 1: a working CLI agent that can:
- Think/chat using a free local LLM (Ollama)
- Search the web
- Read PDFs, Word docs, PowerPoint files, and images (OCR)
- Remember things in local files (no server, no cloud)

Everything runs on YOUR computer. Nothing leaves your machine except web searches.

---

## STEP 1 — Install Ollama (the free local "brain")

Ollama lets you run real open-source AI models on your own PC for free, forever.

1. Go to https://ollama.com/download
2. Download and install for your OS (Windows/Mac/Linux)
3. Open a terminal and run:
   ```
   ollama pull llama3.1
   ```
   (This downloads an ~4.7GB model. If your PC is low-spec, use `ollama pull llama3.2:3b` instead — smaller and faster.)
4. Test it:
   ```
   ollama run llama3.1
   ```
   Type something, see if it replies. Type `/bye` to exit.

If step 4 works, your free local AI brain is ready.

---

## STEP 2 — Install Python + dependencies

You need Python 3.10+. Check with `python3 --version`.

In the `zugo_ai` folder, run:
```
pip install -r requirements.txt
```

On Linux, also install tesseract for OCR:
```
sudo apt install tesseract-ocr
```
On Mac: `brew install tesseract`
On Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki

---

## STEP 3 — Run Zugo

```
python3 agent.py
```

You'll get a chat prompt. Try:
- `search: latest news on AI regulation`
- `read: documents/somefile.pdf`
- Just chat normally — it remembers within the session and saves to memory/

---

## Folder structure

```
zugo_ai/
  agent.py          <- main brain loop
  web_search.py      <- free web search tool
  document_reader.py <- reads pdf/docx/pptx/images
  storage.py          <- local memory (JSON files, your "database")
  documents/           <- drop files here for Zugo to read
  memory/              <- Zugo's saved memories (auto-created)
  requirements.txt
```

---

## What's next (Phase 2, once this works)

- Give Zugo a proper long-term memory (SQLite + simple vector search so it can "recall" past facts semantically, not just keyword match)
- Add a simple web UI (Streamlit — also free) instead of terminal
- Add LinkedIn/market-data scraping (note: LinkedIn actively blocks scraping — I'll explain the free/legal options when we get there)
- Add autonomous multi-step planning (the agent breaks a goal into steps on its own)

Tell me when Phase 1 is running and we'll build Phase 2 file by file.
