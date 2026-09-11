#!/usr/bin/env bash
# Run from repository root; task-local dependency, native DWG stays unchanged.
set -eu
BASE="$PWD"
OUT="${1:-$BASE/.local/G02/cad/recheck-$(date +%Y%m%dT%H%M%S)}"
case "$OUT" in "$BASE/.local/"*) ;; *) echo 'Output must be inside repository .local/' >&2; exit 2;; esac
[ ! -e "$OUT" ] || { echo 'Output already exists; choose a new directory' >&2; exit 2; }
PKG="$BASE/.local/cad-tools/oda/ODAFileConverter_QT6_lnxX64_8.3dll_27.1.deb"
ODA="$BASE/.local/cad-tools/oda/root/usr/bin/ODAFileConverter_27.1.0.0/ODAFileConverter"
mkdir -p "$(dirname "$PKG")" "$OUT/input" "$OUT/noaudit" "$OUT/audit"
if [ ! -f "$PKG" ]; then curl -L --fail 'https://www.opendesign.com/guestfiles/get?filename=ODAFileConverter_QT6_lnxX64_8.3dll_27.1.deb' -o "$PKG"; fi
python3 - "$PKG" <<'PY'
import hashlib,sys
assert hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()=='c71363cd54758177af47a365154f180dc50a1e2b52a131994fda541c13a36766'
PY
[ -x "$ODA" ] || dpkg-deb -x "$PKG" "$BASE/.local/cad-tools/oda/root"
cp "$BASE/documentation/01-hull-and-geometry/lines/Linie teoretyczne VDS 67.DWG" "$OUT/input/"
# Qt xcb uses existing DISPLAY; no application offscreen plugin supplied in this package.
# timeout protects headless environments; no GUI licence acceptance or subscriptions performed.
set +e
timeout 60 "$ODA" "$OUT/input" "$OUT/noaudit" ACAD2004 DXF 0 0 '*.DWG' > "$OUT/noaudit.stdout.log" 2> "$OUT/noaudit.stderr.log"
RC0=$?
timeout 60 "$ODA" "$OUT/input" "$OUT/audit" ACAD2004 DXF 0 1 '*.DWG' > "$OUT/audit.stdout.log" 2> "$OUT/audit.stderr.log"
RC1=$?
set -e
python3 - "$OUT" "$RC0" "$RC1" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]);(p/'exit-status.json').write_text(json.dumps({'noaudit':int(sys.argv[2]),'audit':int(sys.argv[3])},indent=2)+'\n')
PY
[ "$RC0" = 0 ] && [ "$RC1" = 0 ]
"$BASE/.local/cad-tools/dwg/venv/bin/python" "$BASE/deliverables/G02/v001/01_support/cad/compare_cad.py" --oda "$OUT/noaudit/Linie teoretyczne VDS 67.dxf" --g01 "$BASE/deliverables/G01/v001/01_support/dwg/lines-derived.dxf" --log "$BASE/deliverables/G01/v001/01_support/dwg/dwg2dxf.stderr.log" --out "$OUT/comparison" > "$OUT/comparison.stdout.log" 2> "$OUT/comparison.stderr.log"
