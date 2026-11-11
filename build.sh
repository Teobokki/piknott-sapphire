#!/bin/bash
# Windows build via Wine: PyInstaller onedir + Inno Setup installer + onefile portable + zip
set -e
export WINEPREFIX=/workspace/exwifi/.wine WINEDEBUG=-all
cd "$(dirname "$0")"
V=$(grep -oP 'APP_VERSION = "\K[^"]+' piknott_sapphire.py)
PY='C:\Python311\python.exe'
wine "$PY" -m PyInstaller --noconfirm "PIKNOTT SAPPHIRE.spec" > build_dir.log 2>&1; echo DIR_DONE
wine "C:\\InnoSetup\\ISCC.exe" installer.iss > build_iss.log 2>&1; echo ISS_DONE
wine "$PY" -m PyInstaller --noconfirm --workpath build_onefile --distpath dist_onefile "PIKNOTT SAPPHIRE onefile.spec" > build_1f.log 2>&1
cp "dist_onefile/PIKNOTT SAPPHIRE.exe" dist/PIKNOTT.SAPPHIRE.Portable.exe; echo ONEFILE_DONE
cd dist && rm -f PIKNOTT.SAPPHIRE.$V.Windows.x64.zip && python3 -c "import shutil; shutil.make_archive('PIKNOTT.SAPPHIRE.'+'$V'+'.Windows.x64', 'zip', '.', 'PIKNOTT SAPPHIRE')" && echo ZIP_DONE
ls -la
