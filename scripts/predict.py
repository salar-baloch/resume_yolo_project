from ultralytics import YOLO
import cv2

# 1. Load your custom-trained model
model = YOLO("models/resume_yolo.pt")

# 2. Run detection on a test image
# conf=0.5 means it will only show boxes it is 50%+ confident about
results = model.predict(
    source="test_images/sample_resume.png", 
    conf=0.5, 
    save=True,        # Saves the image with boxes drawn
    save_txt=True     # Saves the exact coordinates (critical for cropping later)
)

print("✅ Prediction complete! Check the 'runs/detect/predict' folder.")