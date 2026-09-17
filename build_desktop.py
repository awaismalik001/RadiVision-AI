"""
build_desktop.py
----------------
Complete End-to-End Build Pipeline for RadiVision AI Desktop Workstation.
1. Compiles React + Vite frontend into optimized static production bundle.
2. Compiles FastAPI AI backend and PyTorch/YOLO/ViT models into standalone binary (PyInstaller).
3. Packages complete application into native Windows desktop executable (Electron-Builder).
"""

import os
import sys
import subprocess
import shutil
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

def log(msg: str):
    print(f"\n[RadiVision Builder] {msg}")

def run_cmd(cmd, cwd):
    print(f">> Running: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        log(f"Command failed with exit code: {result.returncode}")
        sys.exit(result.returncode)

def main():
    start_time = time.time()
    log("=" * 60)
    log(" Starting RadiVision AI Native Desktop Packaging Pipeline")
    log("=" * 60)

    # 1. Compile React Frontend
    log("Step 1/3: Compiling React + Tailwind + Vite Frontend...")
    run_cmd("npm run build", cwd=FRONTEND_DIR)

    # 2. Compile FastAPI AI Backend with PyInstaller
    log("Step 2/3: Compiling FastAPI Engine & PyTorch/YOLO Models via PyInstaller...")
    from build_backend import build_backend
    build_backend()

    # Verify backend executable
    backend_exe = os.path.join(ROOT_DIR, "dist-server", "server", "server.exe")
    if not os.path.exists(backend_exe):
        log(f"ERROR: Backend executable was not created at: {backend_exe}")
        sys.exit(1)

    # 3. Package with Electron-Builder
    log("Step 3/3: Packaging into Native Desktop Executable via Electron-Builder...")
    # Build unpacked directory first for verification and speed
    run_cmd("npm run package:dir", cwd=FRONTEND_DIR)

    elapsed = time.time() - start_time
    output_dir = os.path.join(FRONTEND_DIR, "dist-electron", "win-unpacked")
    app_exe = os.path.join(output_dir, "RadiVision AI.exe")

    log("=" * 60)
    log(f"[SUCCESS] Desktop Workstation Build Complete in {elapsed:.1f}s!")
    log(f"Executable: {app_exe}")
    log(f"Unpacked Distribution Directory: {output_dir}")
    log("Launch 'RadiVision AI.exe' directly like WhatsApp Desktop without any terminals or IDEs.")
    log("=" * 60)

if __name__ == "__main__":
    main()
