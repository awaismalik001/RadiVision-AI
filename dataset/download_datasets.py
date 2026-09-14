"""
download_datasets.py
--------------------
Automated dataset acquisition and structuring utility for RadiVision AI.

Downloads public clinical datasets from Kaggle / open repositories
and automatically prepares them in the directory format expected by
the training pipelines:
  - Chest (Pneumonia): dataset/chest_xray/{train,val,test}/{NORMAL,PNEUMONIA}
  - Bone (Fracture):   dataset/bone_xray/{images,labels}/{train,val,test}
  - Dental (Pathology): dataset/dental_xray/{images,labels}/{train,val,test}

Usage:
  python dataset/download_datasets.py --dataset chest
  python dataset/download_datasets.py --quick-test
"""

import os
import sys
import shutil
import argparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")

def get_dir_file_count(path: str) -> int:
    """Counts total regular files in directory recursively."""
    if not os.path.exists(path):
        return 0
    cnt = 0
    for root, _, files in os.walk(path):
        cnt += len(files)
    return cnt

def download_chest_dataset():
    """
    Downloads the Kermany et al. Chest X-Ray (Pneumonia) dataset (~1.15 GB, ~5,800 images)
    via kagglehub and structures it into dataset/chest_xray/
    """
    print("=" * 65)
    print("   DOWNLOADING CHEST X-RAY (PNEUMONIA) DATASET")
    print("   Source: paultimothymooney/chest-xray-pneumonia")
    print("=" * 65)

    try:
        import kagglehub
    except ImportError:
        print("[Error] kagglehub is required. Install it using: pip install kagglehub")
        return False

    target_dir = os.path.join(DATASET_DIR, "chest_xray")
    os.makedirs(target_dir, exist_ok=True)

    print("\n[*] Contacting Kaggle and downloading dataset...")
    print("    (This is ~1.15 GB. Download speed depends on your connection...)")
    try:
        raw_download_path = kagglehub.dataset_download("paultimothymooney/chest-xray-pneumonia")
        print(f"[+] Download complete at cache: {raw_download_path}")
    except Exception as e:
        print(f"\n[Error] Failed to download via kagglehub: {e}")
        return False

    # Look for the root containing train/val/test
    train_source = None
    for root, dirs, _ in os.walk(raw_download_path):
        if "train" in dirs and "test" in dirs:
            train_source = root
            break

    if not train_source:
        train_source = raw_download_path

    print("\n[*] Structuring images into dataset/chest_xray/ ...")
    for split in ["train", "val", "test"]:
        src_split = os.path.join(train_source, split)
        dst_split = os.path.join(target_dir, split)
        if os.path.exists(src_split):
            if os.path.exists(dst_split):
                print(f"    - {split}/ already present, updating...")
            else:
                print(f"    - Copying {split}/ split...")
            shutil.copytree(src_split, dst_split, dirs_exist_ok=True)

    # Verification summary
    print("\n" + "=" * 65)
    print("   DATASET READY FOR TRAINING!")
    print("=" * 65)
    for split in ["train", "val", "test"]:
        norm_cnt = get_dir_file_count(os.path.join(target_dir, split, "NORMAL"))
        pneu_cnt = get_dir_file_count(os.path.join(target_dir, split, "PNEUMONIA"))
        print(f"   [{split.upper():5s}]  NORMAL: {norm_cnt:4d} images | PNEUMONIA: {pneu_cnt:4d} images")

    print("\nYou can now start training the Chest model by running:")
    print("   python model/chest/train_model.py\n")
    return True

def create_quick_test_dataset():
    """
    Creates a tiny, lightweight test dataset (using synthetic/sample X-rays)
    so the user can test the training script in under 1 minute without waiting
    for large gigabyte downloads.
    """
    print("=" * 65)
    print("   CREATING QUICK-TEST DATASET FOR IMMEDIATE VERIFICATION")
    print("=" * 65)

    from PIL import Image, ImageDraw, ImageFilter

    def _synth_chest(path: str, is_pneumonia: bool):
        img = Image.new("RGB", (256, 256), color=(15, 15, 20))
        draw = ImageDraw.Draw(img)
        # Lung fields
        draw.ellipse([40, 50, 115, 210], fill=(40, 45, 55))
        draw.ellipse([141, 50, 216, 210], fill=(40, 45, 55))
        # Spine & heart
        draw.rectangle([117, 30, 138, 245], fill=(130, 135, 140))
        draw.ellipse([105, 130, 170, 210], fill=(160, 165, 175))
        # Ribs
        for y in range(60, 195, 20):
            draw.arc([35, y, 125, y + 20], start=180, end=360, fill=(90, 95, 105), width=2)
            draw.arc([131, y, 221, y + 20], start=180, end=360, fill=(90, 95, 105), width=2)
        if is_pneumonia:
            # Add opacity/infiltrate
            draw.ellipse([150, 145, 195, 190], fill=(135, 140, 150))
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
        img.save(path)

    target_dir = os.path.join(DATASET_DIR, "chest_xray")
    splits_config = {
        "train": {"NORMAL": 16, "PNEUMONIA": 16},
        "val":   {"NORMAL": 6,  "PNEUMONIA": 6},
        "test":  {"NORMAL": 6,  "PNEUMONIA": 6}
    }

    for split, categories in splits_config.items():
        for cat, count in categories.items():
            folder = os.path.join(target_dir, split, cat)
            os.makedirs(folder, exist_ok=True)
            has_abnormality = (cat == "PNEUMONIA")
            for i in range(count):
                img_path = os.path.join(folder, f"sample_{split}_{cat.lower()}_{i+1}.png")
                if not os.path.exists(img_path):
                    _synth_chest(img_path, is_pneumonia=has_abnormality)

    print("\n[+] Quick-test dataset created successfully at: dataset/chest_xray/")
    for split in ["train", "val", "test"]:
        norm_cnt = get_dir_file_count(os.path.join(target_dir, split, "NORMAL"))
        pneu_cnt = get_dir_file_count(os.path.join(target_dir, split, "PNEUMONIA"))
        print(f"   [{split.upper():5s}]  NORMAL: {norm_cnt:3d} images | PNEUMONIA: {pneu_cnt:3d} images")

    print("\nYou can run a quick dry-run training test right now:")
    print("   python model/chest/train_model.py\n")
    return True

def main():
    parser = argparse.ArgumentParser(description="RadiVision AI Dataset Acquisition Utility")
    parser.add_argument(
        "--dataset",
        choices=["chest", "bone", "dental", "all"],
        default="chest",
        help="Specify which dataset to download (default: chest)"
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Create a mini local dataset to test the training loop in 30 seconds before full download"
    )

    args = parser.parse_args()

    if args.quick_test:
        create_quick_test_dataset()
    elif args.dataset == "chest":
        download_chest_dataset()
    elif args.dataset == "bone":
        print("\n[*] To train Bone Fracture YOLOv8, download FracAtlas or Kaggle Fracture detection dataset:")
        print("    https://www.kaggle.com/datasets/bmadushanirodrigo/fracture-multi-region")
        print("    Place the extracted images and labels into: dataset/bone_xray/")
    elif args.dataset == "dental":
        print("\n[*] To train Dental Panoramic YOLOv8, download DENTEX Challenge dataset:")
        print("    https://dentex.grand-challenge.org/")
        print("    Place the extracted images and labels into: dataset/dental_xray/")
    elif args.dataset == "all":
        download_chest_dataset()

if __name__ == "__main__":
    main()
