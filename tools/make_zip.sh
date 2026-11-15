#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python - "$ROOT" <<'PY'
import sys, zipfile
from pathlib import Path
root=Path(sys.argv[1])
out=root/'output'/'ZAY_KEYS_Installer_Project.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
    for p in sorted(root.rglob('*')):
        if p.is_file() and 'output' not in p.relative_to(root).parts:
            z.write(p, Path('ZAY_KEYS_Installer')/p.relative_to(root))
print(out)
PY
