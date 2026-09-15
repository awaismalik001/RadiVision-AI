"""
download_datasets.py
--------------------
Automated dataset acquisition and structuring utility for RadiVision AI.

Downloads public clinical datasets from Kaggle / open repositories
and automatically prepares them in the directory format expected by
the training pipelines:
  - Chest (Pneumonia): dataset/chest_xray/{train,val,test}/{NORMAL,PNEUMONIA}
  - Bone (Fracture):   dataset/bone_xray/{images,labels}/{train,val,test}

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

# Kaggle dataset slugs & web links
DATASET_SOURCES = {
    "chest": {
        "name": "Chest X-Ray (Pneumonia)",
        "slug": "paultimothymooney/chest-xray-pneumonia",
        "url": "https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia",
        "target_dir": os.path.join(DATASET_DIR, "chest_xray"),
        "train_cmd": "python model/chest/train_model.py"
    },
    "bone": {
        "name": "Bone Fracture & Musculoskeletal Regions",
        "slug": "bmadushanirodrigo/fracture-multi-region-x-ray-data",
        "alt_slug": "ahmedhamada0/fracatlas-dataset",
        "url": "https://www.kaggle.com/datasets/bmadushanirodrigo/fracture-multi-region-x-ray-data",
        "alt_url": "https://www.kaggle.com/datasets/ahmedhamada0/fracatlas",
        "target_dir": os.path.join(DATASET_DIR, "bone_xray"),
        "train_cmd": "python model/bone/train_bone_yolo.py"
    }
}

def get_dir_file_count(path: str) -> int:
    """Counts total regular files in directory recursively."""
    if not os.path.exists(path):
        return 0
    cnt = 0
    for _, _, files in os.walk(path):
        cnt += len(files)
    return cnt

def check_kaggle_auth() -> bool:
    """Checks if Kaggle API credentials are configured."""
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    if os.path.exists(kaggle_json):
        return True
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    return False

def show_auth_help(dataset_key: str = None):
    """Displays user-friendly guidance when Kaggle authentication is missing or blocked."""
    print("\n" + "=" * 68)
    print("   [!] KAGGLE AUTHENTICATION / ACCESS REQUIRED (403 FORBIDDEN)")
    print("=" * 68)
    print("Kaggle requires authentication to download datasets through its API.")
    print("Choose one of the two straightforward options below:\n")
    print("--- OPTION 1: Set Up Free Kaggle Credentials (Takes ~30 seconds) ---")
    print("1. Log in to https://www.kaggle.com (create a free account if needed).")
    print("2. Click your profile avatar (top-right) -> Settings.")
    print("3. In the 'API' section, click 'Create New Token'. This downloads kaggle.json.")
    print(f"4. Move kaggle.json to: {os.path.expanduser('~/.kaggle') + os.sep}kaggle.json")
    print("   Or run: python dataset/download_datasets.py --login")
    print("\n--- OPTION 2: Direct Browser Download (No API Key Required!) ---")
    print("You can download the dataset directly in your web browser:")
    if dataset_key and dataset_key in DATASET_SOURCES:
        info = DATASET_SOURCES[dataset_key]
        print(f"  * {info['name']}: {info['url']}")
        print(f"    -> Extract the downloaded zip directly into: dataset/{os.path.basename(info['target_dir'])}/")
    else:
        for k, info in DATASET_SOURCES.items():
            print(f"  * {info['name']}: {info['url']}")
            print(f"    -> Extract into: dataset/{os.path.basename(info['target_dir'])}/")
    print("=" * 68 + "\n")

def login_kaggle():
    """Interactive Kaggle login helper."""
    print("=" * 68)
    print("   KAGGLE AUTHENTICATION SETUP")
    print("=" * 68)
    try:
        import kagglehub
        kagglehub.login()
        print("\n[+] Authentication successful! You can now download datasets automatically.")
    except Exception as e:
        print(f"\n[Error] Failed to login: {e}")
        show_auth_help()

def show_dataset_status():
    """Prints current presence and image counts for all modalities."""
    print("=" * 68)
    print("   RADIVISION AI - DATASET REPOSITORY STATUS")
    print("=" * 68)
    for key, info in DATASET_SOURCES.items():
        td = info["target_dir"]
        count = get_dir_file_count(td)
        status_tag = f"[READY - {count} files]" if count > 50 else (f"[PARTIAL - {count} files]" if count > 0 else "[NOT DOWNLOADED]")
        print(f" * {info['name']:38s}: {status_tag}")
        print(f"   Directory : {td}")
        if count > 50:
            print(f"   Training  : {info['train_cmd']}")
        else:
            print(f"   Browser DL: {info['url']}")
        print()
    print("=" * 68)

def download_chest_dataset(force: bool = False):
    """Downloads Kermany et al. Chest X-Ray (Pneumonia) dataset."""
    info = DATASET_SOURCES["chest"]
    target_dir = info["target_dir"]
    file_count = get_dir_file_count(target_dir)

    print("=" * 68)
    print(f"   CHECKING / DOWNLOADING {info['name'].upper()}")
    print(f"   Target: {target_dir}")
    print("=" * 68)

    if file_count > 500 and not force:
        print(f"\n[+] Chest X-Ray dataset is ALREADY present! ({file_count} images found)")
        for split in ["train", "val", "test"]:
            norm_cnt = get_dir_file_count(os.path.join(target_dir, split, "NORMAL"))
            pneu_cnt = get_dir_file_count(os.path.join(target_dir, split, "PNEUMONIA"))
            print(f"    [{split.upper():5s}] NORMAL: {norm_cnt:4d} | PNEUMONIA: {pneu_cnt:4d}")
        print(f"\nYou can train the Chest model immediately by running:")
        print(f"   {info['train_cmd']}\n")
        return True

    try:
        import kagglehub
    except ImportError:
        print("[Error] kagglehub is required. Install it using: pip install kagglehub")
        return False

    os.makedirs(target_dir, exist_ok=True)
    print("\n[*] Contacting Kaggle to download chest-xray-pneumonia (~1.15 GB)...")
    try:
        raw_download_path = kagglehub.dataset_download(info["slug"])
        print(f"[+] Download complete at cache: {raw_download_path}")
    except Exception as e:
        print(f"\n[Error] Download failed: {e}")
        show_auth_help("chest")
        return False

    train_source = None
    for root, dirs, _ in os.walk(raw_download_path):
        if "train" in dirs and "test" in dirs:
            train_source = root
            break
    if not train_source:
        train_source = raw_download_path

    print("[*] Structuring images into dataset/chest_xray/ ...")
    for split in ["train", "val", "test"]:
        src_split = os.path.join(train_source, split)
        dst_split = os.path.join(target_dir, split)
        if os.path.exists(src_split):
            shutil.copytree(src_split, dst_split, dirs_exist_ok=True)

    print(f"\n[+] Chest dataset ready! Run: {info['train_cmd']}")
    return True

def download_bone_dataset(force: bool = False):
    """Downloads bone fracture dataset."""
    info = DATASET_SOURCES["bone"]
    target_dir = info["target_dir"]
    file_count = get_dir_file_count(target_dir)

    print("=" * 68)
    print(f"   CHECKING / DOWNLOADING {info['name'].upper()}")
    print(f"   Target: {target_dir}")
    print("=" * 68)

    if file_count > 50 and not force:
        print(f"\n[+] Bone dataset is ALREADY present! ({file_count} files found)")
        print(f"You can train the Bone model by running: {info['train_cmd']}")
        return True

    try:
        import kagglehub
    except ImportError:
        print("[Error] kagglehub is required. Install it using: pip install kagglehub")
        return False

    os.makedirs(target_dir, exist_ok=True)
    print(f"\n[*] Contacting Kaggle to download {info['slug']} ...")
    try:
        raw_path = kagglehub.dataset_download(info["slug"])
        print(f"[+] Download complete at cache: {raw_path}")
    except Exception as e:
        print(f"\n[Error] Download failed: {e}")
        show_auth_help("bone")
        return False

    print("[*] Copying files to dataset/bone_xray/ ...")
    shutil.copytree(raw_path, target_dir, dirs_exist_ok=True)
    print(f"\n[+] Bone dataset ready! Run: {info['train_cmd']}")
    return True

def create_quick_test_dataset(modality: str = "all"):
    """Creates tiny, lightweight test datasets for immediate training verification."""
    print("=" * 68)
    print("   CREATING QUICK-TEST DATASET FOR IMMEDIATE VERIFICATION")
    print("=" * 68)

    from PIL import Image, ImageDraw, ImageFilter

    # --- 1. CHEST ---
    if modality in ["all", "chest"]:
        print("[*] Creating mini Chest X-ray dataset (Normal vs Pneumonia)...")
        def _synth_chest(path: str, is_pneumonia: bool):
            img = Image.new("RGB", (256, 256), color=(15, 15, 20))
            draw = ImageDraw.Draw(img)
            draw.ellipse([40, 50, 115, 210], fill=(40, 45, 55))
            draw.ellipse([141, 50, 216, 210], fill=(40, 45, 55))
            draw.rectangle([117, 30, 138, 245], fill=(130, 135, 140))
            draw.ellipse([105, 130, 170, 210], fill=(160, 165, 175))
            for y in range(60, 195, 20):
                draw.arc([35, y, 125, y + 20], start=180, end=360, fill=(90, 95, 105), width=2)
                draw.arc([131, y, 221, y + 20], start=180, end=360, fill=(90, 95, 105), width=2)
            if is_pneumonia:
                draw.ellipse([150, 145, 195, 190], fill=(135, 140, 150))
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            img.save(path)

        chest_dir = os.path.join(DATASET_DIR, "chest_xray")
        splits_config = {
            "train": {"NORMAL": 16, "PNEUMONIA": 16},
            "val":   {"NORMAL": 6,  "PNEUMONIA": 6},
            "test":  {"NORMAL": 6,  "PNEUMONIA": 6}
        }
        for split, categories in splits_config.items():
            for cat, count in categories.items():
                folder = os.path.join(chest_dir, split, cat)
                os.makedirs(folder, exist_ok=True)
                has_abnormality = (cat == "PNEUMONIA")
                for i in range(count):
                    img_path = os.path.join(folder, f"sample_{split}_{cat.lower()}_{i+1}.png")
                    if not os.path.exists(img_path):
                        _synth_chest(img_path, is_pneumonia=has_abnormality)
        print("    [+] Chest quick-test ready. Run: python model/chest/train_model.py")

    # --- 2. BONE (YOLOv8 Detection) ---
    if modality in ["all", "bone"]:
        print("[*] Creating mini Bone YOLOv8 dataset (images + labels)...")
        bone_dir = os.path.join(DATASET_DIR, "bone_xray")
        for split, count in [("train", 12), ("val", 4), ("test", 4)]:
            img_dir = os.path.join(bone_dir, "images", split)
            lbl_dir = os.path.join(bone_dir, "labels", split)
            os.makedirs(img_dir, exist_ok=True)
            os.makedirs(lbl_dir, exist_ok=True)

            for i in range(count):
                img_path = os.path.join(img_dir, f"sample_bone_{split}_{i+1}.png")
                lbl_path = os.path.join(lbl_dir, f"sample_bone_{split}_{i+1}.txt")
                if not os.path.exists(img_path):
                    b_img = Image.new("RGB", (256, 384), color=(20, 20, 25))
                    draw = ImageDraw.Draw(b_img)
                    draw.rectangle([60, 20, 190, 360], fill=(45, 45, 55))
                    draw.rounded_rectangle([80, 40, 130, 340], radius=8, fill=(180, 185, 195))
                    draw.rounded_rectangle([140, 60, 175, 330], radius=6, fill=(175, 180, 190))
                    is_fracture = (i % 2 == 0)
                    if is_fracture:
                        draw.line([(75, 200), (135, 215)], fill=(25, 25, 30), width=3)
                    b_img.save(img_path)

                if not os.path.exists(lbl_path):
                    # Write YOLO format: <class_id> <x_center> <y_center> <w> <h>
                    with open(lbl_path, "w") as lf:
                        # Class 1: Wrist_Radius
                        lf.write("1 0.41 0.50 0.20 0.78\n")
                        # Class 2: Forearm_Ulna
                        lf.write("2 0.61 0.51 0.14 0.70\n")
                        if i % 2 == 0:
                            # Class 0: Fracture
                            lf.write("0 0.41 0.54 0.24 0.08\n")
        print("    [+] Bone YOLOv8 quick-test ready. Run: python model/bone/train_bone_yolo.py")

    print("\n[+] Quick-test generation complete!\n")

def main():
    parser = argparse.ArgumentParser(description="RadiVision AI Dataset Acquisition Utility")
    parser.add_argument(
        "--dataset",
        choices=["chest", "bone", "all"],
        default="status",
        help="Specify which dataset to download (chest, bone, all)"
    )
    parser.add_argument("--status", action="store_true", help="Display dataset availability status")
    parser.add_argument("--login", action="store_true", help="Authenticate with your Kaggle account")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files exist")
    parser.add_argument("--quick-test", action="store_true", help="Create synthetic mini test dataset")

    args = parser.parse_args()

    if args.status:
        show_dataset_status()
    elif args.login:
        login_kaggle()
    elif args.quick_test:
        create_quick_test_dataset()
    elif args.dataset == "chest":
        download_chest_dataset(force=args.force)
    elif args.dataset == "bone":
        download_bone_dataset(force=args.force)
    elif args.dataset == "all":
        download_chest_dataset(force=args.force)
        download_bone_dataset(force=args.force)
    else:
        show_dataset_status()

if __name__ == "__main__":
    main()

