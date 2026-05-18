import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. LOAD THE NLP MODEL ---
print("Loading SBERT AI Model... (Takes a moment on first run)")
# all-MiniLM-L6-v2 is a blazing fast, lightweight model perfect for our use case
model = SentenceTransformer('all-MiniLM-L6-v2')

# --- 2. DEFINE THE JOB REQUIREMENTS ---
# Imagine this is the job description for an AI/ML Internship
target_job_skills = [
    "Python", 
    "Machine Learning", 
    "Computer Vision", 
    "Deep Learning", 
    "TensorFlow or PyTorch"
]

# --- 3. LOAD YOUR EXTRACTED RESUME DATA ---
print("Loading Extracted Resume Data...")
with open("outputs/resume_data.json", "r", encoding="utf-8") as f:
    resume_data = json.load(f)

# Grab the skills section from your JSON (falling back to empty list if missing)
my_resume_skills = resume_data.get("Skills", [])

# Combine the resume skills into one big block of text for the AI to read
resume_text = " ".join(my_resume_skills)

print("\n🔍 Analyzing Skill Alignment...\n")

# --- 4. CALCULATE MATCH SCORES ---
total_score = 0

print(f"{'REQUIRED SKILL':<25} | {'MATCH CONFIDENCE'}")
print("-" * 45)

for required_skill in target_job_skills:
    # Convert words into mathematical vectors
    req_vector = model.encode([required_skill])
    res_vector = model.encode([resume_text])
    
    # Calculate how closely the vectors align (0.0 to 1.0)
    match_score = cosine_similarity(req_vector, res_vector)[0][0]
    
    # Convert to percentage
    match_percent = round(match_score * 100, 2)
    total_score += match_percent
    
    print(f"{required_skill:<25} | {match_percent}%")

# --- 5. FINAL VERDICT ---
average_match = round(total_score / len(target_job_skills), 2)
print("-" * 45)
print(f"OVERALL JOB MATCH SCORE:  | {average_match}%\n")

if average_match > 60:
    print(" Verdict: Highly Qualified! Proceed to Interview.")
else:
    print(" Verdict: Lacks key technical requirements.")