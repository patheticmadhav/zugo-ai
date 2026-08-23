# Deploying Zugo.ai Live — Free, Always-On, From Anywhere

This makes your website live on the real internet with its own permanent link,
without needing your laptop to stay on. Total time: ~20 minutes.

---

## STEP 1 — Get a free Groq API key (your cloud AI brain)

1. Go to console.groq.com, sign up free
2. Click "API Keys" → "Create API Key"
3. Copy the key (starts with `gsk_...`) — save it somewhere safe

---

## STEP 2 — Put your code on GitHub (free, required by Render)

1. Go to github.com, sign up free if you don't have an account
2. Click the "+" icon top right → "New repository"
3. Name it `zugo-ai`, keep it Public, click "Create repository"
4. On the new repo page, click "uploading an existing file"
5. Drag in your ENTIRE `zugo_ai` folder contents (all the .py files, the
   `templates` folder, `requirements-cloud.txt`, `Procfile`) — not the memory/
   or documents/ folders, since those are personal and will regenerate fresh
6. Click "Commit changes"

---

## STEP 3 — Deploy on Render (free hosting)

1. Go to render.com, sign up free (you can sign up with your GitHub account —
   easiest option, one click)
2. Click "New +" → "Web Service"
3. Connect your `zugo-ai` GitHub repo
4. Fill in:
   - **Name**: zugo-ai (or anything you like — this becomes part of your URL)
   - **Region**: pick the one closest to you
   - **Build Command**: `pip install -r requirements-cloud.txt`
   - **Start Command**: `gunicorn cloud_server:app`
   - **Instance Type**: Free
5. Scroll to "Environment Variables" → click "Add Environment Variable":
   - Key: `GROQ_API_KEY`
   - Value: paste your Groq key from Step 1
6. Click "Create Web Service"

Render will now build and deploy your site — takes a few minutes the first time.
Watch the logs; when it says "Live," your site is public.

---

## STEP 4 — Your website is live

Render gives you a permanent URL like:
```
https://zugo-ai.onrender.com
```

Anyone, anywhere, on any device can open that link and use Zugo — no cmd, no
Ollama, no server.py running on your laptop needed ever again.

**One honest limitation of the free tier**: if nobody visits for 15 minutes,
Render puts your site to sleep to save resources. The next visitor waits about
20-30 seconds while it wakes up, then it's fast for everyone after that. This
is normal for free hosting and doesn't cost you anything — no card required.

---

## What's different in the cloud version vs your local version

- Brain: Groq's cloud AI instead of Ollama (works even when your PC is off)
- Chat, memory, document reading, search — all still work the same way
- Storage: memory/facts are stored on Render's server disk, which resets
  whenever the app redeploys or restarts after sleeping. Good enough to try
  this live and share it with people now — if you want memory that survives
  forever, the next step is connecting a small free cloud database (I can
  build that when you're ready)

---

## Updating your site later

Whenever you want to change something (new features, design tweaks):
1. Edit the files on your PC
2. Go back to your GitHub repo → upload the changed files again → commit
3. Render automatically redeploys within a minute or two
