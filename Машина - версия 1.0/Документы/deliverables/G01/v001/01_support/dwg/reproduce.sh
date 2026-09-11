#!/usr/bin/env bash
# Run from repository root. All original files are read-only inputs.
set -eu
TOOLROOT="$PWD/.local/cad-tools/dwg"
SCRIPTROOT="$PWD/deliverables/G01/v001/01_support/dwg"
OUT="${1:-$PWD/.local/G01/dwg/recheck}"
INPUT="$PWD/documentation/01-hull-and-geometry/lines/Linie teoretyczne VDS 67.DWG"
mkdir -p "$TOOLROOT" "$OUT"
if [ ! -x "$TOOLROOT/libredwg-0.13.3/programs/dwgread" ]; then
  curl -L --fail https://ftp.gnu.org/gnu/libredwg/libredwg-0.13.3.tar.xz -o "$TOOLROOT/libredwg-0.13.3.tar.xz"
  python3 - "$TOOLROOT/libredwg-0.13.3.tar.xz" <<'PY'
import hashlib,sys
assert hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()=='83f1f6e78a744777a481ff4520e4cef3f8ac4b2c1c25671077ca12fe81e8816e'
PY
  tar -xf "$TOOLROOT/libredwg-0.13.3.tar.xz" -C "$TOOLROOT"
  (cd "$TOOLROOT/libredwg-0.13.3"; ./configure --disable-shared --disable-bindings > configure.log 2>&1; make -j2 CFLAGS='-O0 -g0' > build.log 2>&1)
fi
if [ ! -x "$TOOLROOT/venv/bin/python" ]; then
  python3 -m venv "$TOOLROOT/venv"
  "$TOOLROOT/venv/bin/pip" install -r "$SCRIPTROOT/requirements-lock.txt"
fi
# Keep warnings and record each actual return code, even on nonfatal conversion errors.
set +e
"$TOOLROOT/libredwg-0.13.3/programs/dwgread" -O JSON -o "$OUT/lines-decoded.json" "$INPUT" > "$OUT/dwgread.stdout.log" 2> "$OUT/dwgread.stderr.log"
JSON_RC=$?
"$TOOLROOT/libredwg-0.13.3/programs/dwg2dxf" -y -o "$OUT/lines-derived.dxf" "$INPUT" > "$OUT/dwg2dxf.stdout.log" 2> "$OUT/dwg2dxf.stderr.log"
DXF_RC=$?
set -e
python3 - "$OUT" "$JSON_RC" "$DXF_RC" <<'PY'
import json,pathlib,sys
(pathlib.Path(sys.argv[1])/'conversion-status.json').write_text(json.dumps({'dwgread_exit':int(sys.argv[2]),'dwg2dxf_exit':int(sys.argv[3]),'libredwg':'0.13.3'},indent=2)+'\n')
PY
"$TOOLROOT/venv/bin/python" "$SCRIPTROOT/inspect_dxf.py" --out-dir "$OUT" > "$OUT/inspection.stdout.log" 2> "$OUT/inspection.stderr.log"
