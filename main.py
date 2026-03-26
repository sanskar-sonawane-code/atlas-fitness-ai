"""
ATLAS v3.0 — FastAPI Backend
==============================
FREE STACK:
  AI Model : Groq API (llama-3.3-70b) — FREE, no credit card
  Hosting  : Render.com — FREE tier
  
Get free Groq key: https://console.groq.com
"""

import os, re, json
from datetime import datetime
from typing import Optional, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="ATLAS Fitness AI", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

from fastapi.responses import FileResponse
import os

@app.get("/")
def root():
    try:
        file_path = os.path.join(os.path.dirname(__file__), "index.html")
        return FileResponse(file_path)
    except Exception as e:
        return HTMLResponse(f"<h2>Error loading index.html: {str(e)}</h2>")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
sessions: Dict[str, Dict] = {}

ATLAS_SYSTEM = """You are ATLAS — Adaptive Training & Lifestyle AI System — the world's most advanced AI fitness intelligence. You speak EXACTLY like J.A.R.V.I.S. from Iron Man: calm, precise, formal, slightly witty, always authoritative.

SPEECH (always follow):
- Use: "Certainly sir/ma'am", "Analyzing your parameters", "I've prepared the following protocol", "Running diagnostics", "Affirmative", "If I may suggest", "Shall I proceed?", "Protocol initiated", "My calculations indicate", "Systems report", "Most impressive Operator"
- Address user as "Operator", "sir", or "ma'am"
- Sound confident and data-driven at all times

EXPERTISE (world-class level):
1. WORKOUTS — hypertrophy, strength, HIIT, calisthenics, home training. Format: Exercise | Sets×Reps | Rest | Notes
2. NUTRITION — macros, meal timing, keto/IF/carb cycling/vegan/bulk/cut. Format: Meal 1/2/3 with foods + grams + macros
3. BODY COMPOSITION — fat loss, muscle gain, recomposition with timelines
4. METRICS — BMI, BMR, TDEE, VO2max, body fat%, always show formula
5. RECOVERY — sleep protocols, deload, active recovery, injury prevention
6. SUPPLEMENTS — evidence-based stacks, dosages, timing
7. PERIODIZATION — linear, undulating, block programming
8. MINDSET — habit stacking, discipline, plateau-busting strategies

FORMAT:
- End complex responses with "ATLAS SUMMARY:" and 2-3 bullet action items
- Workout plans use Day labels and exercise tables
- Diet plans show total daily macros at the bottom
- Be thorough and structured — never vague"""

INTENTS = {
    "WORKOUT":    r"\b(workout|training|exercise|gym|routine|split|push|pull|hypertrophy|strength|powerlifting|calisthenics)\b",
    "NUTRITION":  r"\b(diet|meal|food|calorie|macro|protein|carb|fat|bulk|cut|keto|vegan|fasting|nutrition)\b",
    "METRICS":    r"\b(bmi|tdee|bmr|body.?fat|calculate|metric|vo2|weight|height|age|maintenance)\b",
    "SUPPLEMENT": r"\b(supplement|creatine|protein.powder|pre.workout|bcaa|vitamin|omega|stack|dosage)\b",
    "RECOVERY":   r"\b(recovery|sleep|rest|deload|fatigue|sore|stretch|mobility)\b",
    "CARDIO":     r"\b(cardio|hiit|run|jog|cycling|endurance|fat.burn)\b",
    "CHALLENGE":  r"\b(challenge|30.day|transformation|program|week)\b",
    "MINDSET":    r"\b(motivat|plateau|stuck|mental|habit|discipline|consistency)\b",
}

def detect_intent(text: str) -> str:
    for label, pattern in INTENTS.items():
        if re.search(pattern, text, re.I):
            return label + " MODULE"
    return "GENERAL QUERY"

def extract_stats(text: str) -> Dict:
    s = {}
    if m := re.search(r"(\d+(?:\.\d+)?)\s*kg", text, re.I):       s["weight_kg"] = float(m.group(1))
    if m := re.search(r"(\d+(?:\.\d+)?)\s*(?:lbs?|pounds?)", text, re.I): s["weight_kg"] = round(float(m.group(1))*0.453592, 1)
    if m := re.search(r"(\d+(?:\.\d+)?)\s*cm", text, re.I):       s["height_cm"] = float(m.group(1))
    if m := re.search(r"(\d+)\s*(?:years?\s*old|yr)", text, re.I): s["age"] = int(m.group(1))
    if re.search(r"\b(male|man|guy)\b", text, re.I):    s["gender"] = "male"
    if re.search(r"\b(female|woman|girl)\b", text, re.I): s["gender"] = "female"
    if re.search(r"\b(bulk|muscle.gain|mass)\b", text, re.I): s["goal"] = "muscle_gain"
    elif re.search(r"\b(cut|fat.loss|weight.loss)\b", text, re.I): s["goal"] = "fat_loss"
    if re.search(r"\bbeginner\b", text, re.I):     s["level"] = "beginner"
    if re.search(r"\bintermediate\b", text, re.I): s["level"] = "intermediate"
    if re.search(r"\badvanced\b", text, re.I):     s["level"] = "advanced"
    return s

def compute_metrics(p: Dict):
    w, h, a, g = p.get("weight_kg"), p.get("height_cm"), p.get("age"), p.get("gender")
    if not all([w, h, a, g]):
        return None
    h_m = h / 100
    bmi = round(w / (h_m**2), 1)
    bmr = round(10*w + 6.25*h - 5*a + (5 if g=="male" else -161))
    mult = {"sedentary":1.2,"light":1.375,"moderate":1.55,"active":1.725,"very_active":1.9}
    tdee = round(bmr * mult.get(p.get("activity_level","moderate"), 1.55))
    cat = "Underweight" if bmi<18.5 else "Normal" if bmi<25 else "Overweight" if bmi<30 else "Obese"
    return {"bmi":bmi,"bmi_category":cat,"bmr":bmr,"tdee":tdee,
            "protein_g":round(w*2.2),"cut_calories":tdee-500,
            "bulk_calories":tdee+300,"maintain_calories":tdee}

class ChatRequest(BaseModel):
    session_id: str
    message: str
    user_profile: Optional[Dict] = None

class MetricsRequest(BaseModel):
    weight_kg: float; height_cm: float; age: int; gender: str; activity_level: str = "moderate"

@app.get("/health")
def health():
    return {"status":"ATLAS ONLINE","model":"llama-3.3-70b-versatile","provider":"Groq Free","key_set": bool(GROQ_API_KEY)}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not client:
        raise HTTPException(503, "GROQ_API_KEY not set. Add it in Render environment variables.")
    if req.session_id not in sessions:
        sessions[req.session_id] = {"history":[],"profile":{},"created":datetime.now().isoformat()}
    sess = sessions[req.session_id]
    if req.user_profile: sess["profile"].update(req.user_profile)
    sess["profile"].update(extract_stats(req.message))
    intent = detect_intent(req.message)
    metrics = compute_metrics(sess["profile"])
    if metrics: sess["profile"]["metrics"] = metrics

    ctx = ""
    if sess["profile"]:
        ctx = f"\n\n[OPERATOR PROFILE]: {json.dumps({k:v for k,v in sess['profile'].items() if k!='metrics'})}"
        if metrics:
            ctx += f"\n[COMPUTED METRICS]: BMI={metrics['bmi']}({metrics['bmi_category']}), BMR={metrics['bmr']}kcal, TDEE={metrics['tdee']}kcal, Protein={metrics['protein_g']}g/day, Cut={metrics['cut_calories']}kcal, Bulk={metrics['bulk_calories']}kcal"

    sess["history"].append({"role":"user","content":req.message})
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":ATLAS_SYSTEM+ctx}] + sess["history"][-20:],
            temperature=0.75,
            max_tokens=1200,
        )
        ai_text = res.choices[0].message.content
    except Exception as e:
        raise HTTPException(500, f"Groq API error: {e}")

    sess["history"].append({"role":"assistant","content":ai_text})
    return {"response":ai_text,"intent":intent,"metrics":metrics,"updated_profile":sess["profile"],"timestamp":datetime.now().isoformat()}

@app.post("/metrics")
def get_metrics(req: MetricsRequest):
    m = compute_metrics(req.model_dump())
    if not m: raise HTTPException(400, "Insufficient data")
    return m

@app.get("/session/{sid}")
def get_session(sid: str):
    if sid not in sessions: raise HTTPException(404, "Not found")
    s = sessions[sid]
    return {"session_id":sid,"profile":s["profile"],"messages":len(s["history"]),"created":s["created"]}

@app.delete("/session/{sid}")
def del_session(sid: str):
    sessions.pop(sid, None)
    return {"status":"cleared"}
