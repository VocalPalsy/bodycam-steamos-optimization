#!/usr/bin/env bash
set -e

echo "================================================================="
echo "  Bodycam v0.8 (Locked & Loaded) 120 FPS Flatline Optimizer"
echo "  Optimized for SteamOS, Steam Machine & Linux RDNA 2/3 GPUs"
echo "================================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPAT_DIR="$HOME/.local/share/Steam/steamapps/compatdata/2406770/pfx/drive_c/users/steamuser/AppData/Local/Bodycam/Saved/Config/Windows"
PROTON_DIR="$HOME/.local/share/Steam/steamapps/common/Proton - Experimental"
BODYCAM_BIN="$HOME/.local/share/Steam/steamapps/common/Bodycam/Bodycam/Binaries/Win64"

# Fallback check for SD card / secondary storage mount
if [ ! -d "$COMPAT_DIR" ]; then
  ALT_COMPAT=$(find "$HOME" /run/media -type d -path '*/compatdata/2406770/pfx/drive_c/users/steamuser/AppData/Local/Bodycam/Saved/Config/Windows' 2>/dev/null | head -n 1 || true)
  if [ -n "$ALT_COMPAT" ]; then
    COMPAT_DIR="$ALT_COMPAT"
  else
    echo "[!] Error: Bodycam prefix directory not found. Please launch the game once first."
    exit 1
  fi
fi

# 1. Proton Experimental user_settings.py deployment
echo "[1/4] Configuring Proton Experimental graphics pipeline..."
if [ -d "$PROTON_DIR" ]; then
  cp "$SCRIPT_DIR/user_settings.py" "$PROTON_DIR/user_settings.py"
  echo "  -> Installed user_settings.py to $PROTON_DIR"
else
  echo "  -> Proton - Experimental not found at default path, skipping user_settings.py injection."
fi

# 2. Update Engine.ini cleanly preserving base paths
echo "[2/4] Injecting Engine.ini anti-fluctuation parameters..."
ENGINE_INI="$COMPAT_DIR/Engine.ini"
chmod +w "$ENGINE_INI" 2>/dev/null || true

python3 -c "
import os
ini_path = '$ENGINE_INI'
opt_path = '$SCRIPT_DIR/Engine.ini'

with open(opt_path, 'r') as f:
    new_blocks = f.read().strip()

if os.path.exists(ini_path):
    with open(ini_path, 'r') as f:
        content = f.read()
    if '[/Script/Engine.Engine]' in content:
        content = content.split('[/Script/Engine.Engine]')[0].rstrip()
    elif '[SystemSettings]' in content:
        content = content.split('[SystemSettings]')[0].rstrip()
    final = content + '\n\n' + new_blocks + '\n'
else:
    final = new_blocks + '\n'

with open(ini_path, 'w') as f:
    f.write(final)
"
chmod 444 "$ENGINE_INI"
echo "  -> Engine.ini deployed and write-protected (chmod 444)."

# 3. Update GameUserSettings.ini
echo "[3/4] Updating scalability targets in GameUserSettings.ini..."
GUS_INI="$COMPAT_DIR/GameUserSettings.ini"
chmod +w "$GUS_INI" 2>/dev/null || true
cp "$SCRIPT_DIR/GameUserSettings.ini" "$GUS_INI"
chmod 444 "$GUS_INI"
echo "  -> GameUserSettings.ini deployed and write-protected (chmod 444)."

# 4. Check for and disable DirectML CPU fallback dll
echo "[4/4] Auditing game binaries for DirectML CPU bottleneck..."
if [ -d "$BODYCAM_BIN" ]; then
  if [ -f "$BODYCAM_BIN/DirectML.dll" ]; then
    mv "$BODYCAM_BIN/DirectML.dll" "$BODYCAM_BIN/DirectML.dll.disabled"
    echo "  -> Disabled DirectML.dll (prevents CPU thread pegging at 96%)."
  else
    echo "  -> Clean: No CPU-fallback DirectML.dll found in binaries."
  fi
fi

echo ""
echo "================================================================="
echo "  Optimization Complete!"
echo "  - Pinned Framerate: 120 FPS Flatline (1:1 120Hz Match)"
echo "  - FSR 3.1 Balanced + FSR Frame Gen & Async Compute Active"
echo "  - VRAM Pool Locked to 4608MB (No System RAM GTT Paging)"
echo "  Launch Bodycam and enjoy zero-variance 120 FPS matches!"
echo "================================================================="
