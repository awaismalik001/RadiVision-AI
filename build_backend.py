"""
build_backend.py
----------------
Automated PyInstaller build script for RadiVision AI.
Packages the FastAPI AI inference engine and all dependencies
(PyTorch, Vision Transformer, YOLOv8, ReportLab, SQLite, Uvicorn)
into a standalone, native executable distribution directory (dist-server/server).
"""

import os
import sys
import subprocess
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def build_backend():
    print("=" * 60)
    print(" RadiVision AI — Standalone Backend Packaging Pipeline")
    print("=" * 60)

    # 1. Clean previous builds
    dist_dir = os.path.join(ROOT_DIR, "dist-server")
    work_dir = os.path.join(ROOT_DIR, "build-server")
    if os.path.exists(dist_dir):
        print(f"[*] Cleaning previous dist directory: {dist_dir}")
        shutil.rmtree(dist_dir, ignore_errors=True)
    if os.path.exists(work_dir):
        print(f"[*] Cleaning previous build directory: {work_dir}")
        shutil.rmtree(work_dir, ignore_errors=True)

    # 2. Hidden imports for Uvicorn, FastAPI, ReportLab, Torch, and SQLite
    hidden_imports = [
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "fastapi",
        "starlette",
        "starlette.middleware",
        "starlette.middleware.cors",
        "starlette.staticfiles",
        "starlette.responses",
        "pydantic",
        "reportlab",
        "reportlab.platypus",
        "reportlab.lib",
        "reportlab.lib.colors",
        "reportlab.lib.styles",
        "reportlab.lib.pagesizes",
        "reportlab.graphics.shapes",
        "sqlite3",
        "bcrypt",
        "openpyxl",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
        "PIL.ImageFont",
        "torch",
        "torchvision",
        "torchvision.models",
        "torchvision.transforms",
        "ultralytics",
        "ultralytics.models",
        "ultralytics.models.yolo",
        "dotenv",
        "app",
        "app.model_engine",
        "app.hospital_referral",
        "app.report_generator",
        "app.database",
        "app.auth",
        "app.encryption",
        "app.excel_export",
        "app.vit_model",
        "app.preprocessing",
        "app.domain_shift_augmentation",
        "app.gemini_service",
        "app.detection_overlay",
        "cv2"
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=server",
        "--onedir",
        "--noconfirm",
        "--clean",
        f"--distpath={dist_dir}",
        f"--workpath={work_dir}",
        f"--paths={ROOT_DIR}",
    ]

    for h in hidden_imports:
        cmd.extend(["--hidden-import", h])

    cmd.append(os.path.join(ROOT_DIR, "server.py"))

    print(f"[*] Executing PyInstaller build command...")
    print(f"    Command: {' '.join(cmd[:6])} ... [+{len(hidden_imports)} hidden imports]")
    
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    if result.returncode != 0:
        print(f"[!] PyInstaller build failed with exit code: {result.returncode}")
        sys.exit(result.returncode)

    exe_path = os.path.join(dist_dir, "server", "server.exe")
    if os.path.exists(exe_path):
        # Patch torchvision native C++ extensions and DLLs (_C_stable.pyd, image_stable.pyd, dlls)
        try:
            import torchvision
            tv_dir = os.path.dirname(torchvision.__file__)
            target_tv_dir = os.path.join(dist_dir, "server", "_internal", "torchvision")
            if os.path.exists(target_tv_dir):
                print(f"[*] Copying torchvision binary extensions from {tv_dir} to {target_tv_dir}...")
                for f in os.listdir(tv_dir):
                    if f.endswith(".pyd") or f.endswith(".dll"):
                        src = os.path.join(tv_dir, f)
                        dst = os.path.join(target_tv_dir, f)
                        shutil.copy2(src, dst)
                        print(f"    + {f}")
        except Exception as e:
            print(f"[!] Warning: Could not patch torchvision binaries: {e}")

        print("=" * 60)
        print(f"[SUCCESS] Backend standalone executable compiled successfully!")
        print(f"    Binary Path: {exe_path}")
        print(f"    Size: {os.path.getsize(exe_path) / (1024 * 1024):.2f} MB")
        print("=" * 60)
    else:
        print(f"[!] Warning: Expected output binary not found at: {exe_path}")

if __name__ == "__main__":
    build_backend()
