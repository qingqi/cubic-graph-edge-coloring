import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["core", "backend"],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "oegarn",
    version = "0.1",
    description = "Oegarn Graph Inspector",
    options = {"build_exe": build_exe_options},
    executables = [Executable("app.py", base=base)]
)