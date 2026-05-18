import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import os
import json
import subprocess
from google import genai

# --- 1. UI SETUP ---
st.set_page_config(page_title="AI CV Analyzer",  layout="wide")

st.title(" AI Resume Matchmaker")
st.markdown("Upload a Candidate CV and provide a Job Description to run the full Vision + NLP pipeline.")

# Hardcode your API Key
MY_API_KEY = "AIzaSyBMySvhnOrWnPtu0NJ-GSdtbyjSOuO0-Zo" 

# --- 2. DUAL UPLOADERS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Job Description")
    # Let the user choose their preferred input method!
    jd_input_method = st.radio("How do you want to provide the Job Description?", ("Paste Text", "Upload PDF"))
    
    if jd_input_method == "Paste Text":
        pasted_jd = st.text_area("Paste the Job Description here:", height=150)
        uploaded_jd = None
    else:
        uploaded_jd = st.file_uploader("Upload Job Description (PDF)", type=["pdf"], key="jd")
        pasted_jd = ""

with col2:
    st.subheader("📄 Candidate CV")
    uploaded_cv = st.file_uploader("Upload CV (PDF)", type=["pdf"], key="cv")

# --- 3. RUN THE PIPELINE ---
if st.button("🚀 Run Full AI Pipeline", use_container_width=True):
    
    # Validation check: Did they give us a JD (either text or PDF) AND a CV?
    jd_is_ready = (jd_input_method == "Paste Text" and bool(pasted_jd.strip())) or (jd_input_method == "Upload PDF" and uploaded_jd is not None)
    
    if not jd_is_ready or not uploaded_cv:
        st.error("⚠️ Please provide BOTH a Job Description and a Candidate CV to begin.")
    else:
        progress_text = st.empty()
        bar = st.progress(0)

        try:
            # STEP A: Process the Job Description (Handle both Text and PDF)
            progress_text.text("Processing Job Description...")
            jd_text = ""
            if jd_input_method == "Paste Text":
                jd_text = pasted_jd
            else:
                jd_document = fitz.open(stream=uploaded_jd.read(), filetype="pdf")
                for page in jd_document:
                    jd_text += page.get_text()
            bar.progress(20)

            # STEP B: Process the CV (Convert to Images for YOLO)
            progress_text.text("Converting CV to images for Vision Model...")
            os.makedirs("test_images", exist_ok=True)
            cv_document = fitz.open(stream=uploaded_cv.read(), filetype="pdf")
            
            for page_number in range(cv_document.page_count):
                page = cv_document.load_page(page_number)
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                image = Image.open(io.BytesIO(pixmap.tobytes("png")))
                image.save(f"test_images/cv_page_{page_number}.png")
            bar.progress(40)

            # STEP C: Trigger Local OCR Scripts
            progress_text.text("Running YOLOv8 and Tesseract OCR... (This may take a minute)")
            subprocess.run(["python", "scripts/run_ocr.py"], check=True)
            subprocess.run(["python", "scripts/build_ats_json.py"], check=True)
            bar.progress(70)

            # STEP D: AI Analysis with Gemini
            progress_text.text("Gemini is analyzing the data...")
            client = genai.Client(api_key=MY_API_KEY)
            
            with open("outputs/resume_data.json", "r", encoding="utf-8") as f:
                resume_data = json.load(f)

            prompt = f"""
            You are an expert Technical Recruiter. Evaluate this candidate based strictly on their resume data against the provided Job Description.
            
            JOB DESCRIPTION:
            {jd_text}
            
            CANDIDATE RESUME DATA:
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
            
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            ai_evaluation = json.loads(clean_json)
            bar.progress(100)
            progress_text.text("Pipeline Complete!")

            # --- 4. DISPLAY RESULTS ---
            st.success("✅ Candidate Analysis Generated Successfully!")
            
            m1, m2 = st.columns(2)
            m1.metric("Match Score", f"{ai_evaluation['score']}/100")
            m2.metric("Recruiter Verdict", ai_evaluation['verdict'])
            
            st.divider()
            
            s1, s2 = st.columns(2)
            with s1:
                st.subheader("💪 Strengths")
                for s in ai_evaluation['strengths']: st.write(f"- {s}")
            with s2:
                st.subheader("⚠️ Missing/Weaknesses")
                for w in ai_evaluation['weaknesses']: st.write(f"- {w}")
                    
            st.divider()
            
            with st.expander("🛠️ Project Alignment Analysis", expanded=True):
                st.write(ai_evaluation['project_analysis'])
                
            with st.expander("💼 Experience Alignment Analysis", expanded=True):
                st.write(ai_evaluation['experience_analysis'])

        except subprocess.CalledProcessError:
            st.error("Failed to run the OCR/YOLO scripts. Check your terminal for backend errors.")
        except json.JSONDecodeError:
            st.error("Gemini returned invalid JSON. Please try running it again.")
        except Exception as e:
            st.error(f"An error occurred: {e}")