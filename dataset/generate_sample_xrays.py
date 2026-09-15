"""
generate_sample_xrays.py
------------------------
Utility script to generate synthetic sample radiographs for demonstration
and verification testing of RadiVision AI across all supported modalities:
  1. sample_chest_xray.png (Chest view with simulated lung fields and ribs)
  2. sample_bone_xray.png (Bone view with distal radius fracture simulation)
"""

import os
from PIL import Image, ImageDraw, ImageFilter

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
os.makedirs(SAMPLES_DIR, exist_ok=True)

def generate_samples():
    print(f"Generating synthetic demonstration radiographs into: {SAMPLES_DIR}")

    # 1. Chest Radiograph (512 x 512)
    chest_img = Image.new("RGB", (512, 512), color=(15, 15, 20))
    draw = ImageDraw.Draw(chest_img)
    
    # Draw thoracic cavity & lungs (darker lung parenchyma)
    draw.ellipse([80, 100, 230, 420], fill=(40, 45, 55))  # Left lung field
    draw.ellipse([282, 100, 432, 420], fill=(40, 45, 55)) # Right lung field
    
    # Spine & mediastinum / cardiac silhouette (denser white opacity)
    draw.rectangle([235, 60, 277, 490], fill=(130, 135, 140)) # Spine
    draw.ellipse([210, 260, 340, 420], fill=(160, 165, 175))   # Cardiac shadow
    
    # Ribs simulation
    for y in range(120, 390, 35):
        draw.arc([70, y, 250, y + 40], start=180, end=360, fill=(90, 95, 105), width=4)
        draw.arc([262, y, 442, y + 40], start=180, end=360, fill=(90, 95, 105), width=4)

    # Simulated infiltrate / consolidation in right lower lobe
    draw.ellipse([300, 290, 380, 370], fill=(120, 125, 135))
    chest_img = chest_img.filter(ImageFilter.GaussianBlur(radius=3))
    chest_path = os.path.join(SAMPLES_DIR, "sample_chest_xray.png")
    chest_img.save(chest_path)
    print(f"  [+] Created: {chest_path}")

    # 2. Bone Fracture Radiograph (400 x 600 - typical tall extremity aspect)
    bone_img = Image.new("RGB", (400, 600), color=(20, 20, 25))
    b_draw = ImageDraw.Draw(bone_img)

    # Soft tissue contour
    b_draw.rectangle([110, 40, 290, 560], fill=(45, 45, 55))

    # Radius shaft (denser bone)
    b_draw.rounded_rectangle([140, 60, 200, 540], radius=10, fill=(180, 185, 195))
    # Ulna shaft
    b_draw.rounded_rectangle([220, 80, 265, 520], radius=8, fill=(175, 180, 190))

    # Fracture line across distal radius
    b_draw.line([(135, 340), (205, 355)], fill=(25, 25, 30), width=4)
    bone_img = bone_img.filter(ImageFilter.GaussianBlur(radius=2))
    bone_path = os.path.join(SAMPLES_DIR, "sample_bone_xray.png")
    bone_img.save(bone_path)
    print(f"  [+] Created: {bone_path}")

    print("\nDemonstration radiographs ready for testing.")

if __name__ == "__main__":
    generate_samples()
