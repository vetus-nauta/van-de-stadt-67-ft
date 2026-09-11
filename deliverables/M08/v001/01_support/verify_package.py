"""Verify the frozen document copies against their recorded Git basis."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import csv
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BUNDLE = ROOT / 'Машина - версия 1.0'
checks = []

def check(name, passed):
    checks.append({'check': name, 'status': 'PASS' if passed else 'FAIL'})

def sha(data):
    return hashlib.sha256(data).hexdigest()

rows = list(csv.DictReader((BUNDLE / 'Реестры/Документы.csv').open(), delimiter=';'))
for row in rows:
    path = BUNDLE / row['packet_path']
    data = path.read_bytes()
    basis = subprocess.check_output(['git', 'show', row['basis_commit'] + ':' + row['source_path']], cwd=ROOT)
    check('source-copy:' + row['source_path'], not path.is_symlink() and len(data) == int(row['bytes']) and sha(data) == row['sha256'] and data == basis)

catalogues = json.loads((BUNDLE / 'Реестры/Каталоги.json').read_text())
for row in catalogues:
    path = BUNDLE / row['packet_path']
    data = path.read_bytes()
    info = subprocess.run(['pdfinfo', str(path)], capture_output=True)
    ignored = subprocess.run(['git', 'check-ignore', '-q', str(path)], cwd=ROOT).returncode == 0
    check('local-pdf:' + row['packet_path'], len(data) == row['bytes'] and sha(data) == row['sha256'] and data == (ROOT / row['source_path']).read_bytes() and info.returncode == 0 and ignored)

class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value:
                url = urlsplit(value)
                if not url.scheme and url.path:
                    check('index-link:' + unquote(url.path), (BUNDLE / unquote(url.path)).exists())

Links().feed((BUNDLE / '00_Оглавление.html').read_text())
actual = {str(p.relative_to(BUNDLE)) for p in (BUNDLE / 'Документы').rglob('*') if p.is_file()}
check('document-inventory-exact', actual == {r['packet_path'] for r in rows})
check('no-symlinks', not any(p.is_symlink() for p in BUNDLE.rglob('*')))
check('no-lockfiles-or-private-workspaces', not any(p.name.startswith('.~lock.') or p.name in ('.git', '.env', '.local') for p in BUNDLE.rglob('*')))
result = {'status': 'PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL', 'date': '2026-09-11', 'document_copies': len(rows), 'local_pdf_occurrences': len(catalogues), 'checks_total': len(checks), 'checks': checks, 'limits': 'Integrity and document navigation only; no new engineering, tax or budget approval.'}
(ROOT / 'deliverables/M08/v001/01_support/verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k != 'checks'}, ensure_ascii=False, indent=2))
assert result['status'] == 'PASS'
