# Running Zugo.ai — Daily Use, Pendrive, and Offline Guide

## 1. ONE-CLICK LAUNCH (on your own PC)

I've added `start_zugo.bat` to your project folder. From now on:

- Just **double-click `start_zugo.bat`** inside the `zugo_ai` folder
- A black window opens and Zugo starts automatically — no typing commands
- To make it even easier: right-click `start_zugo.bat` → "Send to" → "Desktop (create shortcut)"
  Now you have a desktop icon — double-click it anytime to launch Zugo.

Important: **Ollama must be running** for this to work. It usually auto-starts in the background
after you install it (check the little icon near your clock/system tray). If chat doesn't respond,
open the Ollama app once from the Start menu to wake it up, then launch Zugo again.

---

## 2. PENDRIVE / PORTABILITY — the honest version

Here's what's realistically possible for free, explained clearly:

**What CAN move freely on a pendrive:**
- Your entire `zugo_ai` folder (code + all your saved memories in `memory/` + documents)
- This means all your conversations, saved facts, and files travel with you

**What CANNOT be "zero-install, one-click" on a totally new PC:**
- Ollama (the AI engine) needs to be installed on whatever computer you plug into — it runs as a
  background service, not a portable app. This isn't a Zugo limitation; it's how any local-AI setup works.
- Python also needs to be installed on that machine.

**The realistic workflow:**
1. Copy the whole `zugo_ai` folder onto your pendrive
2. On a new PC (once, ~10 minutes): install Ollama (`ollama.com/download`), run `ollama pull llama3.1`,
   install Python 3.12 (`winget install Python.Python.3.12`)
3. Plug in your pendrive, open the `zugo_ai` folder from it, double-click `start_zugo.bat`
4. From that point on, on THAT machine, it's truly one click each time

If you want, once Phase 1 is fully stable, I can also show you how to make the Python part itself
fully portable (a self-contained Python folder that needs no install) — that removes half the setup.
Ollama installation is unfortunately unavoidable on each new machine, since it's the AI engine itself.

---

## 3. OFFLINE USE

Already mostly true right now:
- Chatting with Zugo → fully offline (Ollama runs locally, no internet needed)
- Reading PDFs/Word/PPTX/images → fully offline
- Remembering facts / recalling memory → fully offline
- Only `search: <query>` needs internet, since it's live web research

So once Ollama and the model are downloaded, you can turn off wifi entirely and Zugo still chats,
reads your documents, and remembers things — just can't search the web until you're back online.
