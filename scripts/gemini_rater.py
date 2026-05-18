import os
import json
import google.generativeai as genai

# --- 1. SETUP GEMINI API ---
# Replace 'YOUR_API_KEY' with your actual key from Google AI Studio
genai.configure(api_key="AIzaSyBMySvhnOrWnPtu0NJ-GSdtbyjSOuO0-Zo")

# We use gemini-1.5-flash because it is incredibly fast and great at JSON parsing
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. LOAD YOUR CV DATA ---
print("Loading extracted CV data...")
try:
    with open("outputs/resume_data.json", "r", encoding="utf-8") as f:
        resume_data = json.load(f)
except FileNotFoundError:
    print("Error: Could not find outputs/resume_data.json. Run your OCR script first!")
    exit()

# --- 3. DEFINE THE JOB DESCRIPTION ---
job_description = """
Position: Junior AI/Computer Vision Engineer
Requirements:
- Experience with Python and Machine Learning frameworks (TensorFlow/PyTorch).
- Hands-on projects involving Computer Vision (OpenCV, YOLO, Object Detection).
- Understanding of full-stack integration (APIs, Databases, Web Frameworks).
- Certifications or academic focus in AI/ML is a strong plus.
"""

# --- 4. THE MASTER PROMPT ---
# We instruct Gemini to act as a strict recruiter and return structured JSON
prompt = f"""
You are an expert Technical Recruiter. I am providing you with a Job Description and a Candidate's Extracted Resume Data (in JSON format).

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME DATA:
{json.dumps(resume_data, indent=2)}

TASK:
Evaluate how well this candidate fits the job description. Base your evaluation STRICTLY on the Projects, Experience, and Certifications found in the resume data. Do not make up information.

Respond ONLY with a valid JSON object matching this exact structure:
{{
    "overall_score_out_of_100": int,
    "verdict": "string (e.g., Highly Recommend, Recommend, Do Not Recommend)",
    "strengths": ["string", "string"],
    "missing_requirements": ["string", "string"],
    "project_alignment_analysis": "string detailing how their projects map to the job",
    "experience_alignment_analysis": "string detailing how their experience maps to the job"
}}
"""

print("\n Sending data to Gemini for analysis...\n")

# --- 5. CALL GEMINI ---
response = model.generate_content(prompt)

# --- 6. DISPLAY THE RESULTS ---
# Strip the markdown formatting Gemini sometimes adds to JSON output
clean_json = response.text.replace("```json", "").replace("```", "").strip()

try:
    ai_evaluation = json.loads(clean_json)
    
    print("================ AI EVALUATION ================")
    print(f"Overall Score:  {ai_evaluation['overall_score_out_of_100']}/100")
    print(f"Verdict:        {ai_evaluation['verdict']}")
    print("-" * 45)
    print(" Strengths:")
    for s in ai_evaluation['strengths']: print(f"  - {s}")
    
    print("\n Missing Requirements:")
    for m in ai_evaluation['missing_requirements']: print(f"  - {m}")
    
    print("-" * 45)
    print("  Project Alignment:")
    print(ai_evaluation['project_alignment_analysis'])
    
    print("\n Experience Alignment:")
    print(ai_evaluation['experience_alignment_analysis'])
    print("===============================================")
    
except Exception as e:
    print("Failed to parse Gemini's response. Raw output:")
    print(response.text)