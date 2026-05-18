import os
import cv2
from ultralytics import YOLO

# --- CONFIGURATION ---
MODEL_PATH = "models/resume_yolo.pt"
IMAGE_PATH = "test_images/sample_resume.png"
OUTPUT_DIR = "outputs/crops"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 1. LOAD MODEL & IMAGE ---
print("Loading model and reading image...")
model = YOLO(MODEL_PATH)
img = cv2.imread(IMAGE_PATH)

if img is None:
    raise FileNotFoundError(f"Could not find image at {IMAGE_PATH}. Please check the path.")

# Get image dimensions (height, width) for safety checks
img_height, img_width = img.shape[:2]

# --- 2. RUN DETECTION ---
print("Detecting resume sections...")
# conf=0.5 ensures we only process confident predictions
results = model.predict(source=IMAGE_PATH, conf=0.5) 

# --- 3. CROP AND SAVE ---
print("\n--- Cropping Results ---")
# Loop through every bounding box detected by YOLO
for i, box in enumerate(results[0].boxes):
    
    # Get the coordinates
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    
    # Get the predicted class name (e.g., "Education", "Experience")
    class_id = int(box.cls[0])
    class_name = model.names[class_id]
    
    # SAFETY CHECK: Ensure YOLO didn't guess coordinates outside the image
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(img_width, x2), min(img_height, y2)
    
    # Actually crop the image using NumPy slicing [y_start:y_end, x_start:x_end]
    cropped_section = img[y1:y2, x1:x2]
    
    # Create a clean filename (e.g., "0_Experience.jpg", "1_Education.jpg")
    filename = f"{i}_{class_name}.jpg"
    save_path = os.path.join(OUTPUT_DIR, filename)
    
    # Save it to the outputs folder
    cv2.imwrite(save_path, cropped_section)
    print(f"✅ Saved: {filename}")

print(f"\n🎉 Cropping complete! Check your '{OUTPUT_DIR}' folder.")