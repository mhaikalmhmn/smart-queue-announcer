from pathlib import Path

from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT

project_dir = Path.cwd()


a = Analysis(
    ["app/main.py"],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        ("assets", "assets"),
        ("sounds", "sounds"),
        ("voice_cache", "voice_cache"),
        ("piper/voices", "piper/voices"),
    ],
    hiddenimports=[
        "piper",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(
    a.pure,
)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Smart Queue Announcer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(project_dir / "assets" / "smart_queue_announcer.ico"),
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="Smart Queue Announcer",
)