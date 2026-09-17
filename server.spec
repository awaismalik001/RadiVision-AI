# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:/My Projects/RadiVision AI/server.py'],
    pathex=['D:/My Projects/RadiVision AI'],
    binaries=[],
    datas=[],
    hiddenimports=['uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.lifespan.off', 'fastapi', 'starlette', 'starlette.middleware', 'starlette.middleware.cors', 'starlette.staticfiles', 'starlette.responses', 'pydantic', 'reportlab', 'reportlab.platypus', 'reportlab.lib', 'reportlab.lib.colors', 'reportlab.lib.styles', 'reportlab.lib.pagesizes', 'reportlab.graphics.shapes', 'sqlite3', 'bcrypt', 'openpyxl', 'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont', 'torch', 'torchvision', 'torchvision.models', 'torchvision.transforms', 'ultralytics', 'ultralytics.models', 'ultralytics.models.yolo', 'dotenv', 'app', 'app.model_engine', 'app.hospital_referral', 'app.report_generator', 'app.database', 'app.auth', 'app.encryption', 'app.excel_export', 'app.vit_model', 'app.gemini_service', 'app.detection_overlay'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='server',
)
