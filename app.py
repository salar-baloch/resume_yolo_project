import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import os
import json
import subprocess
from google import genai
from groq import Groq
from dotenv import load_dotenv

# --- 1. INITIALIZATION ---
load_dotenv()

# --- 2. UI SETUP & UPGRADED CSS ---
st.set_page_config(page_title="TalentSync AI", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

    /* ── Reset ── */
    #MainMenu, footer, header { visibility: hidden; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* ── App Background ── */
    .stApp {
        background: #05080f;
        min-height: 100vh;
    }

    /* ── Ambient background orbs ── */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 70% 50% at 15% -5%,  rgba(56,189,248,.13)  0%, transparent 65%),
            radial-gradient(ellipse 55% 45% at 85% 105%, rgba(139,92,246,.12)  0%, transparent 65%),
            radial-gradient(ellipse 35% 25% at 55%  45%, rgba(16,185,129,.08)  0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
        animation: ambientShift 12s ease-in-out infinite alternate;
    }

    @keyframes ambientShift {
        0%   { opacity: 1; }
        50%  { opacity: 0.7; }
        100% { opacity: 1; }
    }

    /* ── Grid dot pattern overlay ── */
    .stApp::after {
        content: '';
        position: fixed;
        inset: 0;
        background-image: radial-gradient(circle, rgba(255,255,255,.04) 1px, transparent 1px);
        background-size: 32px 32px;
        pointer-events: none;
        z-index: 0;
    }

    /* ── Content above overlays ── */
    .block-container {
        position: relative;
        z-index: 1;
        padding-top: 2rem !important;
        max-width: 1240px !important;
    }

    /* ══════════════════════════════════════
       HERO HEADER
    ══════════════════════════════════════ */
    .hero-wrap {
        text-align: center;
        padding: 4rem 1rem 2.5rem;
        position: relative;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        background: rgba(56,189,248,.12);
        border: 1px solid rgba(56,189,248,.35);
        color: #38bdf8;
        font-family: 'DM Sans', sans-serif;
        font-size: .85rem;
        font-weight: 700;
        letter-spacing: .18em;
        text-transform: uppercase;
        padding: .45rem 1.4rem;
        border-radius: 100px;
        margin-bottom: 1.6rem;
        animation: fadeDown .6s ease both;
    }
    .hero-badge::before {
        content: '';
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #38bdf8;
        box-shadow: 0 0 10px #38bdf8;
        animation: pulseDot 2s ease-in-out infinite;
    }

    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: .5; transform: scale(1.5); }
    }

    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(3.2rem, 7.5vw, 6rem);
        font-weight: 800;
        line-height: 1.04;
        letter-spacing: -.04em;
        background: linear-gradient(135deg, #e0f2fe 0%, #38bdf8 30%, #818cf8 60%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 1.2rem;
        animation: fadeDown .75s ease .1s both;
        text-shadow: none;
    }

    .hero-sub {
        color: #94a3b8;
        font-size: 1.2rem;
        font-weight: 500;
        max-width: 540px;
        margin: 0 auto 1rem;
        line-height: 1.75;
        animation: fadeDown .9s ease .2s both;
    }

    /* ══════════════════════════════════════
       GLASS CARDS
    ══════════════════════════════════════ */
    .glass-card {
        background: linear-gradient(145deg, rgba(15,23,42,.85), rgba(10,16,32,.92));
        border: 1px solid rgba(255,255,255,.1);
        border-radius: 22px;
        padding: 2rem;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        box-shadow: 0 8px 48px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.09);
        transition: border-color .4s, box-shadow .4s, transform .3s;
        animation: fadeUp .7s ease .3s both;
    }
    .glass-card:hover {
        border-color: rgba(56,189,248,.28);
        box-shadow: 0 12px 56px rgba(0,0,0,.55), 0 0 0 1px rgba(56,189,248,.1), inset 0 1px 0 rgba(255,255,255,.09);
        transform: translateY(-2px);
    }

    /* ══════════════════════════════════════
       CARD HEADING — BIGGER & BOLDER
    ══════════════════════════════════════ */
    .card-heading {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.6rem;
        font-weight: 400;
        color: #e2e8f0;
        display: flex;
        align-items: center;
        gap: .6rem;
        margin-bottom: 1.1rem;
        letter-spacing: .01em;
        text-shadow: none;
    }
    .card-heading .dot {
        width: 9px; height: 9px;
        border-radius: 50%;
        background: #38bdf8;
        box-shadow: 0 0 14px #38bdf8;
        display: inline-block;
        animation: pulseDot 2.5s ease-in-out infinite;
    }
    .card-heading .dot-purple {
        background: #a855f7;
        box-shadow: 0 0 14px #a855f7;
    }

    .card-sub {
        color: #94a3b8;             /* brighter than before */
        font-size: 1rem;            /* was .88rem */
        font-weight: 500;           /* was 400 */
        line-height: 1.65;
        margin-bottom: .9rem;
    }

    /* ══════════════════════════════════════
       STREAMLIT WIDGET OVERRIDES
    ══════════════════════════════════════ */

    /* Radio toggle */
    .stRadio > div {
        display: flex;
        gap: .5rem;
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 12px;
        padding: .4rem;
        width: fit-content;
        margin-bottom: 1rem;
    }
    .stRadio label {
        color: #94a3b8 !important;
        font-size: 1rem !important;     /* was .88rem */
        font-weight: 600 !important;    /* was normal */
    }

    /* Text area */
    .stTextArea textarea {
        background: rgba(8,12,24,.9) !important;
        border: 1px solid rgba(99,141,255,.25) !important;
        border-radius: 14px !important;
        color: #e2e8f0 !important;      /* bright text */
        caret-color: #38bdf8 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.05rem !important;  /* was .92rem */
        font-weight: 500 !important;
        line-height: 1.75 !important;
        padding: .85rem 1rem !important;
        resize: vertical;
        transition: border-color .3s, box-shadow .3s, background .3s !important;
    }
    .stTextArea textarea:focus {
        background: rgba(12,18,36,.95) !important;
        border-color: rgba(56,189,248,.65) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,.12), 0 0 24px rgba(56,189,248,.06) !important;
        outline: none !important;
    }
    .stTextArea textarea::placeholder {
        color: rgba(100,116,139,.7) !important;
        font-size: .97rem !important;
    }

    /* Text area label */
    .stTextArea label p,
    .stTextArea > label {
        color: #7dd3fc !important;      /* bright cyan instead of dim grey */
        font-size: .95rem !important;   /* was .82rem */
        font-weight: 700 !important;    /* was 500 */
        letter-spacing: .07em !important;
        text-transform: uppercase !important;
        margin-bottom: .4rem !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(8,12,24,.75) !important;
        border: 1.5px dashed rgba(99,141,255,.3) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        transition: border-color .3s, background .3s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(56,189,248,.55) !important;
        background: rgba(56,189,248,.04) !important;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] span {
        color: #94a3b8 !important;
        font-size: 1rem !important;     /* was .9rem */
        font-weight: 600 !important;
    }
    [data-testid="stFileUploader"] small { color: #475569 !important; }
    [data-testid="stFileUploader"] button {
        background: rgba(56,189,248,.12) !important;
        border: 1px solid rgba(56,189,248,.35) !important;
        color: #38bdf8 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: .95rem !important;
    }

    /* Generic text colours — MUCH BRIGHTER */
    p, span, li, div { color: #b0bfd0; }

    /* ══════════════════════════════════════
       DIVIDER
    ══════════════════════════════════════ */
    hr {
        border: none !important;
        border-top: 1px solid rgba(255,255,255,.08) !important;
        margin: 2rem 0 !important;
    }

    /* ══════════════════════════════════════
       CTA BUTTON
    ══════════════════════════════════════ */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #a855f7 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1.1rem 2.5rem !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        font-size: 1.18rem !important;  /* was 1.08rem */
        letter-spacing: .06em !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: transform .3s, box-shadow .3s !important;
        box-shadow: 0 4px 32px rgba(99,102,241,.45), 0 0 0 0 rgba(99,102,241,0) !important;
        animation: ctaPulse 4s ease-in-out infinite;
        text-transform: uppercase !important;
    }
    .stButton > button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 14px 44px rgba(99,102,241,.7), 0 0 70px rgba(56,189,248,.18) !important;
    }
    .stButton > button:active { transform: translateY(-1px) !important; }

    @keyframes ctaPulse {
        0%, 100% { box-shadow: 0 4px 32px rgba(99,102,241,.45), 0 0 0 0 rgba(99,102,241,0); }
        50%       { box-shadow: 0 4px 32px rgba(99,102,241,.6), 0 0 0 10px rgba(99,102,241,.06); }
    }

    /* ══════════════════════════════════════
       PROGRESS BAR
    ══════════════════════════════════════ */
    [data-testid="stProgress"] {
        background: rgba(255,255,255,.06) !important;
        border-radius: 100px !important;
        overflow: hidden;
    }
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #0ea5e9, #6366f1, #a855f7) !important;
        background-size: 200% 100% !important;
        border-radius: 100px !important;
        animation: shimmer 2s linear infinite;
        transition: width .4s ease !important;
    }

    @keyframes shimmer {
        0%   { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* ══════════════════════════════════════
       STATUS ALERTS
    ══════════════════════════════════════ */
    .stSuccess {
        background: rgba(16,185,129,.09) !important;
        border: 1px solid rgba(16,185,129,.3) !important;
        border-radius: 14px !important;
        color: #6ee7b7 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    .stWarning {
        background: rgba(245,158,11,.08) !important;
        border: 1px solid rgba(245,158,11,.28) !important;
        border-radius: 14px !important;
        color: #fcd34d !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    .stError {
        background: rgba(239,68,68,.08) !important;
        border: 1px solid rgba(239,68,68,.28) !important;
        border-radius: 14px !important;
        color: #fca5a5 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* ══════════════════════════════════════
       RESULTS
    ══════════════════════════════════════ */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, rgba(15,23,42,.85), rgba(10,16,32,.92)) !important;
        border: 1px solid rgba(255,255,255,.09) !important;
        border-radius: 20px !important;
        padding: 1.8rem 1.5rem !important;
        text-align: center !important;
        backdrop-filter: blur(14px) !important;
        box-shadow: 0 4px 28px rgba(0,0,0,.4) !important;
        transition: transform .3s, box-shadow .3s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 36px rgba(99,102,241,.3) !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
        color: #7dd3fc !important;      /* bright cyan label */
        font-size: .88rem !important;
        font-weight: 700 !important;
        letter-spacing: .1em !important;
        text-transform: uppercase !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 2.4rem !important;   /* was 2.1rem */
        font-weight: 800 !important;
        background: linear-gradient(135deg, #38bdf8, #818cf8) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }

    /* ── Result items — BOLDER & BRIGHTER ── */
    .result-item {
        display: flex;
        align-items: flex-start;
        gap: .7rem;
        padding: .95rem 1.2rem;
        border-radius: 12px;
        background: rgba(255,255,255,.035);
        border: 1px solid rgba(255,255,255,.07);
        margin-bottom: .6rem;
        color: #cbd5e1;             /* was #94a3b8 */
        font-size: 1.02rem;         /* was .92rem */
        font-weight: 500;           /* was 400 */
        line-height: 1.6;
        transition: background .25s, border-color .25s, transform .25s;
    }
    .result-item:hover {
        background: rgba(56,189,248,.06);
        border-color: rgba(56,189,248,.22);
        transform: translateX(5px);
        color: #f0f6ff;
    }
    .result-item .icon { flex-shrink: 0; font-size: 1.1rem; margin-top: .1rem; }

    /* ── Section headings — COLORFUL & BOLD ── */
    .section-heading {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;            /* was .82rem */
        font-weight: 800;           /* was 700 */
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: .5rem;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(15,23,42,.75) !important;
        border: 1px solid rgba(255,255,255,.09) !important;
        border-radius: 14px !important;
        color: #94a3b8 !important;      /* was #64748b */
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;     /* was .9rem */
        padding: .95rem 1.3rem !important;
        backdrop-filter: blur(10px) !important;
        transition: border-color .3s, color .3s;
    }
    .streamlit-expanderHeader:hover {
        border-color: rgba(56,189,248,.28) !important;
        color: #e2e8f0 !important;
    }
    .streamlit-expanderContent {
        background: rgba(8,12,24,.65) !important;
        border: 1px solid rgba(255,255,255,.065) !important;
        border-top: none !important;
        border-radius: 0 0 14px 14px !important;
        padding: 1.3rem !important;
        color: #b0bfd0 !important;      /* brighter body text */
        font-size: 1.02rem !important;  /* was .93rem */
        font-weight: 500 !important;
        line-height: 1.75 !important;
    }

    .stInfo {
        background: rgba(56,189,248,.07) !important;
        border: 1px solid rgba(56,189,248,.22) !important;
        border-radius: 12px !important;
        color: #bae6fd !important;
        font-size: 1.02rem !important;  /* was .93rem */
        font-weight: 500 !important;
        line-height: 1.8 !important;
    }

    /* Progress label text */
    .progress-label {
        font-family: 'Syne', sans-serif;
        font-size: .95rem;          /* was .85rem */
        font-weight: 700;           /* was 600 */
        color: #7dd3fc;             /* bright cyan instead of grey */
        letter-spacing: .07em;
        text-transform: uppercase;
        margin-bottom: .5rem;
    }

    /* ══════════════════════════════════════
       ANIMATIONS
    ══════════════════════════════════════ */
    @keyframes fadeDown {
        from { opacity: 0; transform: translateY(-20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,.4); border-radius: 100px; }
</style>
""", unsafe_allow_html=True)

# ── HERO HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <span class="hero-badge">Vision + NLP Intelligence Pipeline</span>
    <h1 class="hero-title">TalentSync<br>AI Matchmaker</h1>
    <p class="hero-sub">Drop a candidate résumé, add a job description.<br>
    Our AI scores fit, surfaces gaps, and explains the reasoning — instantly.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── DUAL INPUT PANELS ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('''
        <div class="glass-card">
            <div class="card-heading"><span class="dot"></span>Job Description</div>
        </div>
    ''', unsafe_allow_html=True)

    jd_input_method = st.radio("Input method", ("Paste Text", "Upload PDF"), horizontal=True, label_visibility="collapsed")

    if jd_input_method == "Paste Text":
        pasted_jd = st.text_area(
            "PASTE ROLE DETAILS",
            height=180,
            placeholder="Drop the requirements, skills, responsibilities, and must-haves here…"
        )
        uploaded_jd = None
    else:
        uploaded_jd = st.file_uploader("Upload Job Description PDF", type=["pdf"], key="jd")
        pasted_jd = ""

with col2:
    st.markdown('''
        <div class="glass-card">
            <div class="card-heading"><span class="dot dot-purple"></span>Candidate Résumé</div>
            <p class="card-sub">Upload the applicant\'s CV — our AI vision layer reads layout, sections, and content.</p>
        </div>
    ''', unsafe_allow_html=True)

    uploaded_cv = st.file_uploader("Upload CV / Résumé (PDF)", type=["pdf"], key="cv")

st.write("")
st.write("")

# ── CTA BUTTON ────────────────────────────────────────────────────────────────
run = st.button("⚡  Run Candidate Intelligence Report", use_container_width=True)

# ── PIPELINE ─────────────────────────────────────────────────────────────────
if run:
    jd_is_ready = (jd_input_method == "Paste Text" and bool(pasted_jd.strip())) or \
                  (jd_input_method == "Upload PDF" and uploaded_jd is not None)

    if not jd_is_ready or not uploaded_cv:
        st.warning("⚠️  Both a Job Description and a Candidate CV are required to run the analysis.")
    else:
        progress_text = st.empty()
        bar = st.progress(0)

        try:
            # STEP A: Job Description
            progress_text.markdown('<p class="progress-label">⬡ Parsing job description…</p>', unsafe_allow_html=True)
            jd_text = ""
            if jd_input_method == "Paste Text":
                jd_text = pasted_jd
            else:
                jd_document = fitz.open(stream=uploaded_jd.read(), filetype="pdf")
                for page in jd_document:
                    jd_text += page.get_text()
            bar.progress(20)

            # STEP B: CV → Images
            progress_text.markdown('<p class="progress-label">⬡ Converting résumé pages to images…</p>', unsafe_allow_html=True)
            os.makedirs("test_images", exist_ok=True)
            cv_document = fitz.open(stream=uploaded_cv.read(), filetype="pdf")
            for page_number in range(cv_document.page_count):
                page = cv_document.load_page(page_number)
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                image = Image.open(io.BytesIO(pixmap.tobytes("png")))
                image.save(f"test_images/cv_page_{page_number}.png")
            bar.progress(40)

            # STEP C: OCR Scripts
            progress_text.markdown('<p class="progress-label">⬡ YOLOv8 + Tesseract OCR in progress…</p>', unsafe_allow_html=True)
            subprocess.run(["python", "scripts/run_ocr.py"], check=True)
            subprocess.run(["python", "scripts/build_ats_json.py"], check=True)
            bar.progress(70)

            # STEP D: AI Evaluation
            progress_text.markdown('<p class="progress-label">⬡ AI scoring candidate fit…</p>', unsafe_allow_html=True)

            GEMINI_KEY = os.getenv("GEMINI_API_KEY")
            GROQ_KEY   = os.getenv("GROQ_API_KEY")

            with open("outputs/resume_data.json", "r", encoding="utf-8") as f:
                resume_data = json.load(f)

            prompt = f"""
            You are a senior Technical Recruiter with 15 years of experience. Evaluate this candidate
            strictly on their résumé data against the provided Job Description.

            JOB DESCRIPTION:
            {jd_text}

            CANDIDATE RÉSUMÉ DATA:
            {json.dumps(resume_data, indent=2)}

            Respond ONLY with a valid JSON object matching this exact structure:
            {{
                "score": int (0-100),
                "verdict": "string",
                "strengths": ["string"],
                "weaknesses": ["string"],
                "project_analysis": "string",
                "experience_analysis": "string"
            }}
            """

            clean_json = ""

            try:
                if not GEMINI_KEY:
                    raise ValueError("No Gemini Key")
                client = genai.Client(api_key=GEMINI_KEY)
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                st.toast("Analysis powered by Google Gemini ✓", icon="🟢")
            except Exception:
                st.toast("Gemini unavailable — switching to Groq…", icon="🔄")
                if not GROQ_KEY:
                    st.error("No Groq API key found in .env — cannot complete analysis.")
                    st.stop()
                groq_client = Groq(api_key=GROQ_KEY)
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                clean_json = chat_completion.choices[0].message.content
                st.toast("Analysis powered by Groq (Llama 3) ✓", icon="🟡")

            ai_evaluation = json.loads(clean_json)
            bar.progress(100)
            progress_text.empty()

            # ── RESULTS ─────────────────────────────────────────────────────
            st.success("✨  Intelligence report ready.")
            st.markdown("<br>", unsafe_allow_html=True)

            m1, m2, m3 = st.columns([1, 2, 1])
            with m2:
                sc1, sc2 = st.columns(2)
                sc1.metric("Match Score", f"{ai_evaluation['score']}/100")
                sc2.metric("Verdict",     ai_evaluation['verdict'])

            st.markdown("<br>", unsafe_allow_html=True)

            s1, s2 = st.columns(2, gap="large")
            with s1:
                st.markdown('<p class="section-heading">✦ Candidate Strengths</p>', unsafe_allow_html=True)
                for s in ai_evaluation['strengths']:
                    st.markdown(f'<div class="result-item"><span class="icon">✅</span>{s}</div>', unsafe_allow_html=True)
            with s2:
                st.markdown('<p class="section-heading">✦ Gaps & Risks</p>', unsafe_allow_html=True)
                for w in ai_evaluation['weaknesses']:
                    st.markdown(f'<div class="result-item"><span class="icon">⚠️</span>{w}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("⬡  Project Alignment Breakdown", expanded=True):
                st.info(ai_evaluation['project_analysis'])

            with st.expander("⬡  Experience Alignment Breakdown", expanded=True):
                st.info(ai_evaluation['experience_analysis'])

        except subprocess.CalledProcessError:
            st.error("OCR / YOLO scripts failed — check terminal logs for backend errors.")
        except json.JSONDecodeError:
            st.error("AI returned malformed JSON — please retry the analysis.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")