import os
import json
import pytesseract
from PIL import Image

# --- 1. SETUP ---
# Hardcode Tesseract path (since we know this works perfectly on your machine)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

CROPS_DIR = "outputs/crops"
OUTPUT_JSON = "outputs/resume_data.json"

print("\n Starting ATS JSON Parsing...\n")

# The "Smart Pipeline" correction dictionary
# If YOLO gets confused, we use these keywords in the text to override it
section_keywords = {
    "skill": "Skills",
    "project": "Projects",
    "education": "Education",
    "experience": "Experience",
    "summary": "Summary",
    "profil": "Summary"
}

# The final structure of our resume data
resume_data = {
    "Name": [],
    "Summary": [],
    "Education": [],
    "Experience": [],
    "Projects": [],
    "Skills": [],
    "Uncategorized": []
}

# --- 2. PROCESS CROPS & EXTRACT TEXT ---
for image_file in os.listdir(CROPS_DIR):
    if image_file.endswith(".jpg") or image_file.endswith(".png"):
        image_path = os.path.join(CROPS_DIR, image_file)
        
        # Get YOLO's guess from the filename
        try:
            yolo_label = image_file.split('_')[1].replace('.jpg', '').replace('.png', '')
        except IndexError:
            yolo_label = "Uncategorized"
            
        # Extract Text using Tesseract
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img).strip()
        
        if not extracted_text:
            continue # Skip empty crops
            
        # Split text into a clean list of lines
        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        
        # --- 3. APPLY SMART OVERRIDE LOGIC ---
        first_line = lines[0].lower()
        final_label = yolo_label.capitalize() # Default to YOLO's guess
        
        for keyword, correct_label in section_keywords.items():
            if keyword in first_line:
                final_label = correct_label
                # Remove the header word from the data so we don't duplicate it in our JSON
                lines = lines[1:] 
                break
        
        # --- 4. STORE IN JSON STRUCTURE ---
        # If YOLO found a completely weird class, create a new key for it safely
        if final_label not in resume_data:
            resume_data[final_label] = []
            
        resume_data[final_label].extend(lines)
        
        print(f" Processed: {final_label.ljust(15)} (YOLO originally guessed: {yolo_label})")

# --- 5. SAVE THE JSON ---
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(resume_data, f, indent=4, ensure_ascii=False)

print(f"\n ATS Parsing Complete! Your structured data is saved at: {OUTPUT_JSON}")