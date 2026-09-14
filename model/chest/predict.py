"""
predict.py
-----------
Stand-alone inference verification script for chest pneumonia classification.
Evaluates an arbitrary-sized X-ray image and outputs the diagnosis and confidence.
"""

import sys
import os
import numpy as np

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing import image
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    HAS_TF = True
except ImportError:
    HAS_TF = False

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "chest_xray_model.h5")
IMG_SIZE = (224, 224)
CLASS_LABELS = {0: "NORMAL", 1: "PNEUMONIA (Abnormal)"}

def predict_xray(image_path: str):
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    if not HAS_TF:
        print("TensorFlow is not installed. Please install requirements.txt.")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"Model file '{MODEL_PATH}' not found. Please run train_model.py first.")
        return

    model = load_model(MODEL_PATH)

    # In-memory preprocessing: auto-resizes arbitrary resolution
    img = image.load_img(image_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    raw_pred = model.predict(img_array, verbose=0)[0][0]
    predicted_class = int(raw_pred >= 0.5)
    confidence = raw_pred if predicted_class == 1 else (1.0 - raw_pred)
    label = CLASS_LABELS[predicted_class]

    print("=" * 45)
    print(f"Target Radiograph : {image_path}")
    print(f"Diagnostic Result : {label}")
    print(f"Confidence Rating : {confidence * 100:.2f}%")
    print("=" * 45)

    return label, float(confidence)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_xray_image.jpg>")
        sys.exit(1)
    predict_xray(sys.argv[1])
