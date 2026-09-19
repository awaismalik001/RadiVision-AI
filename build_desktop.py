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
    log("Step 3/4: Packaging into Native Desktop Executable via Electron-Builder...")
    # Build unpacked directory first for verification and speed
    run_cmd("npm run package:dir", cwd=FRONTEND_DIR)

    output_dir = os.path.join(FRONTEND_DIR, "dist-electron", "win-unpacked")
    app_exe = os.path.join(output_dir, "RadiVision AI.exe")
    if not os.path.exists(app_exe):
        log(f"ERROR: Application executable was not created at: {app_exe}")
        sys.exit(1)

    # 4. Create Standalone Workstation Distribution Archive (.zip)
    log("Step 4/4: Creating Compressed Workstation Archive (RadiVision-AI-Workstation.zip)...")
    zip_dest_electron = os.path.join(FRONTEND_DIR, "dist-electron", "RadiVision-AI-Workstation.zip")
    zip_dest_root = os.path.join(ROOT_DIR, "RadiVision-AI-Workstation.zip")

    # Remove previous archives if exist
    for p in [zip_dest_electron, zip_dest_root]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception as e:
                log(f"Notice: Could not delete old archive {p}: {e}")

    import zipfile
    print(f">> Compressing {output_dir} -> {zip_dest_electron}...")
    with zipfile.ZipFile(zip_dest_electron, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, output_dir)
                zf.write(file_path, arcname=rel_path)

    # Copy to project root for convenience
    try:
        shutil.copy2(zip_dest_electron, zip_dest_root)
        print(f">> Copied archive to root: {zip_dest_root}")
    except Exception as e:
        log(f"Notice: Could not copy archive to root: {e}")

    # Also copy unpacked directory to RadiVision-AI-Workstation in root
    workstation_folder_root = os.path.join(ROOT_DIR, "RadiVision-AI-Workstation")
    if os.path.exists(workstation_folder_root):
        shutil.rmtree(workstation_folder_root, ignore_errors=True)
    try:
        shutil.copytree(output_dir, workstation_folder_root)
        print(f">> Copied unpacked workstation folder to: {workstation_folder_root}")
    except Exception as e:
        log(f"Notice: Could not copy workstation folder: {e}")

    # 5. Build Single Windows Setup Installer (.exe)
    log("Step 5/5: Building Single Windows Setup Installer (RadiVision_AI_Setup.exe)...")
    run_cmd("npx electron-builder --win nsis", cwd=FRONTEND_DIR)
    installer_src = os.path.join(FRONTEND_DIR, "dist-electron", "RadiVision_AI_Setup.exe")
    installer_dest_root = os.path.join(ROOT_DIR, "RadiVision_AI_Setup.exe")
    if os.path.exists(installer_src):
        try:
            shutil.copy2(installer_src, installer_dest_root)
            print(f">> Copied Setup Installer to root: {installer_dest_root}")
        except Exception as e:
            log(f"Notice: Could not copy installer to root: {e}")

    elapsed = time.time() - start_time
    zip_size_mb = os.path.getsize(zip_dest_electron) / (1024 * 1024) if os.path.exists(zip_dest_electron) else 0
    installer_size_mb = os.path.getsize(installer_dest_root) / (1024 * 1024) if os.path.exists(installer_dest_root) else 0

    log("=" * 60)
    log(f"[SUCCESS] Desktop Packaging & Installer Pipeline Complete in {elapsed:.1f}s!")
    log(f"1. Single Setup Installer:  {installer_dest_root} ({installer_size_mb:.1f} MB)")
    log(f"2. Portable Zip Archive:    {zip_dest_root} ({zip_size_mb:.1f} MB)")
    log(f"3. Unpacked Executable:     {app_exe}")
    log("Single Setup.exe is ready to share and install on any Windows PC.")
    log("=" * 60)

if __name__ == "__main__":
    main()
