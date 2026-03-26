# ATLAS v3.0 — Complete Setup & Deployment Guide
**Free AI Fitness Chatbot — Groq + Render.com**

---

## 🗂 Project Files

```
atlas/
├── main.py           ← FastAPI backend (AI brain, NLP, metrics)
├── index.html        ← Frontend (JARVIS UI, voice, chat)
├── requirements.txt  ← Python dependencies
├── render.yaml       ← Render.com deploy config
└── README.md         ← This file
```

---

## STEP 1 — Get Free Groq API Key (2 minutes)

1. Go to **https://console.groq.com**
2. Click **Sign Up** (use Google login — fastest)
3. Go to **API Keys** → click **Create API Key**
4. Copy the key — it looks like: `gsk_xxxxxxxxxxxxxxxxxxxx`
5. Save it somewhere safe

**Groq Free Tier limits:**
- 14,400 requests/day
- 6,000 tokens/minute  
- **No credit card required, ever**

---

## STEP 2 — Test Locally (Optional)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set your Groq API key
# Windows:
set GROQ_API_KEY=gsk_your_key_here

# Mac/Linux:
export GROQ_API_KEY=gsk_your_key_here

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Open in browser
# Go to: http://localhost:8000
```

---

## STEP 3 — Push to GitHub (Required for Render)

```bash
# Create a new folder and add your files
mkdir atlas-fitness-ai
cd atlas-fitness-ai

# Copy all 4 files here:
# main.py, index.html, requirements.txt, render.yaml

# Initialize git
git init
git add .
git commit -m "ATLAS v3.0 initial commit"

# Create a GitHub repo at github.com (click New Repository)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/atlas-fitness-ai.git
git branch -M main
git push -u origin main
```

---

## STEP 4 — Deploy to Render.com (Free Hosting)

1. Go to **https://render.com** → Sign up free (use GitHub login)

2. Click **New** → **Web Service**

3. Connect your GitHub repo → select **atlas-fitness-ai**

4. Render auto-detects settings from `render.yaml`. Confirm:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. Scroll to **Environment Variables** → click **Add Variable**:
   - Key: `GROQ_API_KEY`
   - Value: `gsk_your_actual_key_here`

6. Click **Create Web Service**

7. Wait ~3 minutes for first deploy

8. Your app is live at: **`https://atlas-fitness-ai.onrender.com`**

> **Share this link with anyone!** It works on mobile, tablet, desktop.

---

## 🔧 Architecture

```
User Browser
     │  HTTPS
     ▼
┌─────────────────────────────────────┐
│   Render.com (Free)                 │
│                                     │
│   FastAPI (main.py)                 │
│   ├── Serves index.html             │
│   ├── NLP Intent Detection          │
│   ├── Session Memory (per user)     │
│   ├── Health Metrics Calculator     │
│   └── /chat endpoint                │
│              │                      │
│              ▼                      │
│   Groq API (Free)                   │
│   └── LLaMA 3.3 70B model          │
└─────────────────────────────────────┘
```

---

## Features

| Feature | Details |
|---------|---------|
| 🤖 JARVIS Voice | Text-to-speech on every response (Web Speech API) |
| 🎙 Voice Input | Click mic → speak → auto-sends |
| 🧠 NLP Engine | 8 intent modules detected from natural language |
| 📊 Biometrics | BMI, BMR, TDEE, protein targets, cut/bulk calories |
| 👤 Profile Memory | Session remembers your stats across conversation |
| 💬 12 Quick Modules | Workout, Diet, Metrics, Supplements, Recovery, etc. |
| 🌐 Public URL | Anyone can access from any device |
| 💸 Cost | Completely FREE |

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Serves the chat UI |
| GET | `/health` | System status |
| POST | `/chat` | Main AI chat |
| POST | `/metrics` | Calculate metrics |
| GET | `/session/{id}` | View session data |
| DELETE | `/session/{id}` | Clear session |

---

## Extending the Project (Engineering Features to Add)

| Feature | How |
|---------|-----|
| **User Accounts** | Add SQLite + JWT auth |
| **Persistent History** | Replace dict sessions with SQLite |
| **Progress Tracking** | Add `/progress` endpoint + charts |
| **Food Photo Analysis** | Add Groq vision model for calorie detection |
| **Workout Logger** | Add POST /log endpoint + history view |
| **Push Notifications** | Add workout reminders via Web Push API |

---

## Troubleshooting

**"GROQ_API_KEY not set"** → Add the env variable in Render dashboard

**Voice not working** → Use Chrome or Edge (Firefox has limited Web Speech support)

**Render app sleeping** → Free tier sleeps after 15min idle. First request takes ~30s to wake up. Upgrade to paid ($7/mo) to keep always-on.

**"Service unavailable"** → Check Render logs. Usually means API key is wrong.
