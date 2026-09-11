"""Copy an immutable document snapshot, retain source bytes, create a portable index.
Third-party PDF originals remain in the ignored local catalogue directory.
"""
from pathlib import Path
import subprocess,hashlib,json,csv,shutil,re,posixpath,html
from urllib.parse import unquote,quote
R=Path(__file__).resolve().parents[4];B=R/'Машина - версия 1.0';D=B/'Документы';META=B/'Реестры'
assert not B.exists(),'Version exists: do not overwrite released package'
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
tracked=set(filter(None,subprocess.check_output(['git','ls-files','-z'],cwd=R).decode().split('\0')))
prefixes=[*(f'deliverables/M{i:02d}/' for i in range(1,8)),'deliverables/G01/','deliverables/G02/','deliverables/G03/','deliverables/U01/','experiments/EXP-003/','documentation/01-hull-and-geometry/','documentation/02-general-arrangement/','documentation/registers/','docs/','data/office/','office/','skills/','templates/']
chosen={p for p in tracked if any(p.startswith(a) for a in prefixes)}|{'documentation/CAD-status.md','documentation/previews/DOC-003-general-arrangement.png','HANDOFF.md'}
# Complete relative Markdown dependencies, preserving original document links.
scanned=set();unresolved=[]
while chosen-scanned:
 p=sorted(chosen-scanned)[0];scanned.add(p)
 if not p.endswith('.md'):continue
 for target in re.findall(r'\]\(([^)]+)\)',(R/p).read_text(errors='replace')):
  target=target.strip().strip('<>');target=unquote(target.split('#')[0])
  if not target or re.match(r'^[a-zA-Z]+:',target) or target.startswith('/'):continue
  rel=posixpath.normpath(posixpath.join(posixpath.dirname(p),target))
  if rel in tracked:chosen.add(rel)
  elif rel not in ['.','..'] and not rel.startswith(('../','.local')):
   kids={f for f in tracked if f.startswith(rel.rstrip('/')+'/')}
   if kids:chosen|=kids
   else:unresolved.append({'source':p,'target':target,'resolved':rel,'status':'PREEXISTING_OR_UNAVAILABLE_REFERENCE'})
# Add model generation dependencies that are expressed in code, not Markdown.
for prefix in ['experiments/EXP-001/','experiments/EXP-002/']:
 chosen|={p for p in tracked if p.startswith(prefix)}
# Sources/registries/tools for independently reading the included studies.
for prefix in ['sources/','knowledge/','tools/']:
 chosen|={p for p in tracked if p.startswith(prefix)}
for p in ['data/spec-matrix.csv','AGENTS.md']:
 if p in tracked:chosen.add(p)
META.mkdir(parents=True);D.mkdir()
files=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def category(p):
 if p.startswith('deliverables/M07'):return '01 Текущая смета'
 if p.startswith(('deliverables/M02','deliverables/M03')):return '02 КАЦ и рынок'
 if p.startswith(('deliverables/M04','deliverables/M05')):return '03 Yanmar: комплектность и подстановки'
 if p.startswith(('deliverables/M01','deliverables/M06')):return '04 Оборудование и RFQ'
 if p.startswith('deliverables/G03'):return '05 Компоновка МО'
 if p.startswith(('deliverables/G01','deliverables/G02','documentation/','experiments/')):return '06 Чертежи и геометрическая подоснова'
 if p.startswith('deliverables/U01'):return '07 Пустая основа УТВ'
 return '08 Требования, проверки и зависимости'
for p in sorted(chosen):
 src=R/p;dst=D/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 files.append({'source_path':p,'packet_path':str(dst.relative_to(B)),'category':category(p),'bytes':src.stat().st_size,'sha256':digest(src),'visibility':'PUBLIC','basis_commit':base})
# Gather metadata around known archive paths without copying browser profiles, QA or scripts.
source_meta={}
def walk(o):
 if isinstance(o,dict):
  paths=[v for v in o.values() if isinstance(v,str) and v.startswith('.local/') and v.lower().endswith('.pdf')]
  urls=[v for k,v in o.items() if isinstance(v,str) and v.startswith('http') and ('url' in k.lower() or k=='source')]
  for p in paths:source_meta.setdefault(p,[]).extend(urls)
  for v in o.values():walk(v)
 elif isinstance(o,list):
  for v in o:walk(v)
for p in sorted(chosen):
 if p.endswith('.json') and (R/p).stat().st_size<2_000_000:
  try:walk(json.loads((R/p).read_text()))
  except (ValueError,UnicodeError):pass
catdir=B/'Каталоги производителей';catdir.mkdir();catalog=[];byhash={}
for folder in ['.local/M02','.local/M03','.local/M04']:
 for src in sorted((R/folder).rglob('*.pdf')):
  if any(t in src.parts for t in ['qa','recalculated','output']):continue
  if not src.read_bytes().startswith(b'%PDF-'):continue
  h=digest(src);sp=str(src.relative_to(R))
  if h not in byhash:
   dst=catdir/(h[:10]+'_'+src.name);shutil.copy2(src,dst);byhash[h]=str(dst.relative_to(B))
  catalog.append({'source_path':sp,'packet_path':byhash[h],'bytes':src.stat().st_size,'sha256':h,'source_urls':sorted(set(source_meta.get(sp,[]))),'visibility':'LOCAL_ONLY_THIRD_PARTY_PDF','status':'ARCHIVED_NOT_SUPPLIER_QUOTATION'})
# Optional inaccessible/absent PDFs remain explicitly absent, not an invented complete collection.
(B/'.gitignore').write_text('Каталоги производителей/\n')
with (META/'Документы.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(files[0]),delimiter=';',lineterminator='\n');w.writeheader();w.writerows(files)
(META/'Каталоги.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
(META/'Ссылки-исходников.json').write_text(json.dumps(unresolved,ensure_ascii=False,indent=2)+'\n')
summary={'package':'Машина - версия 1.0','date':'2026-09-11','basis_commit':base,'public_copied_files':len(files),'public_bytes':sum(f['bytes'] for f in files),'local_pdf_occurrences':len(catalog),'unique_local_pdfs':len(byhash),'local_pdf_unique_bytes':sum((B/p).stat().st_size for p in byhash.values()),'preexisting_unresolved_markdown_references':len(unresolved),'status':'DOCUMENT_SNAPSHOT_NOT_NEW_ENGINEERING_OR_BUDGET_APPROVAL','originals_preserved':True,'local_catalogues_excluded_from_public_git':True}
(META/'Состав.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
# Offline user-facing navigation; all source copies are under their original relative paths.
E=html.escape
href=lambda p:quote(p,safe='/')
sections=[('Смета — текущий выпуск',[('Excel с налоговыми колонками','deliverables/M07/v001/00_engine-room-estimate.xlsx'),('Печатная смета, 3 листа','deliverables/M07/v001/01_support/01_estimate-print.pdf'),('Пояснения, ограничения и источники','deliverables/M07/v001/01_support/00_readme.md')]),('КАЦ и цены',[('Рабочая КАЦ M03','deliverables/M03/v001/00_working-KAC.xlsx'),('Рыночное сравнение M02','deliverables/M02/v001/00_market-analysis.xlsx'),('Yanmar: комплектующие M04','deliverables/M04/v001/00_yanmar-completeness.md'),('Подстановки цен M05','deliverables/M05/v001/00_price-substitutions.md')]),('Состав оборудования',[('Перечень M01','deliverables/M01/v001/00_equipment-list.md'),('Комплектность силовой установки M06','deliverables/M06/v001/00_powerplant-scope.xlsx'),('Проект запроса поставщикам — НЕ отправлен','deliverables/M06/v001/01_support/RFQ-draft-en.md')]),('Компоновка и сервис',[('G03/v002: блоки оборудования, 4 листа','deliverables/G03/v002/00_equipment-block-layout.pdf'),('G03/v001: предыдущая геометрическая проба','deliverables/G03/v001/00_central-engine-room.pdf'),('Сечения и привязка G02','deliverables/G02/v001/00_sprint-result.md'),('Состав и открытые пересечения','deliverables/G03/v002/01_support/00_readme.md')]),('Исходные чертежи',[('Общий план и продольный разрез','documentation/02-general-arrangement/7-1.pdf'),('Исходная модель Rhino','documentation/01-hull-and-geometry/3d/2-1.3dm'),('Теоретические линии DWG','documentation/01-hull-and-geometry/lines/Linie teoretyczne VDS 67.DWG'),('EXP-003: сохранённая идея надстройки','experiments/EXP-003/00_proposal.md')]),('Требования и контроль',[('Исходные требования оборудования','docs/16-premium-builder-specification.md'),('Пустой шаблон УТВ — не утверждённая смета','deliverables/U01/v001/00_UTV_template.xlsx'),('Проверка текущей сметы','deliverables/M07/v001/01_support/review.md'),('Правила налогового сценария','office/cost-policy.md')])]
parts=['<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Машина — версия 1.0</title><style>body{font:16px/1.5 system-ui,sans-serif;max-width:1200px;margin:40px auto;padding:0 24px;color:#213f4b;background:#f5f7f8}h1{font-size:38px}h2{font-size:22px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}.card{background:white;padding:20px;border:1px solid #d6e0e4;border-radius:10px}a{color:#126882}li{margin:9px 0}.note{border-left:4px solid #bd8647;padding:12px 18px;background:#fff7e9}input{font:inherit;padding:12px;width:95%;margin:15px 0}table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;padding:9px;border-bottom:1px solid #dde5e8;font-size:13px;overflow-wrap:anywhere}small{color:#526973}details{margin:20px 0}</style><h1>Машина — версия 1.0</h1>',f'<p>Van de Stadt 67 · Польша · комплект документов на 11.09.2026<br><small>Снимок исходной базы {base[:12]}. Новые изменения оформляются следующей версией.</small></p>','<div class="note"><b>Актуальная смета: M07.</b> Оценено 131 819,50 EUR с учётом налога; это частичная сумма, 30 строк ещё без оценки. НДС в колонках сметы. Компоновка G03 — исследование: полы, окончательный облик и полный сервис не утверждены. Индивидуальные КП не получены; RFQ не отправлен.</div><div class="cards">']
for title,links in sections:
 parts.append('<section class="card"><h2>'+E(title)+'</h2><ul>')
 for label,p in links:assert (D/p).is_file(),p;parts.append('<li><a href="'+href('Документы/'+p)+'">'+E(label)+'</a></li>')
 parts.append('</ul></section>')
parts.append('</div><h2>Локальные каталоги производителей</h2><p>Полные PDF находятся в этой локальной папке. На GitHub опубликованы реестр и исходные URL; сами сторонние PDF там отсутствуют. Это технические каталоги/прайсы, а не полученные персональные КП.</p><ul>')
seen=set()
for c in catalog:
 if c['sha256'] in seen:continue
 seen.add(c['sha256']);parts.append('<li><a href="'+href(c['packet_path'])+'">'+E(Path(c['source_path']).name)+'</a> <small>· '+E(c['source_path'])+'</small></li>')
parts.append('</ul><details><summary>Полный список документов и поиск</summary><input id="q" placeholder="Название, M07, Panda, сечения…" aria-label="Поиск документов"><table><thead><tr><th>Раздел</th><th>Файл</th><th>КБ</th></tr></thead><tbody id="files">')
for f in files:parts.append('<tr><td>'+E(f['category'])+'</td><td><a href="'+href(f['packet_path'])+'">'+E(f['source_path'])+'</a></td><td>'+str(round(f['bytes']/1024,1))+'</td></tr>')
parts.append('</tbody></table></details><p><a href="Реестры/Документы.csv">Реестр документов</a> · <a href="Реестры/Каталоги.json">Происхождение каталогов</a> · <a href="README.md">Как устроен комплект</a></p><script>document.getElementById("q").addEventListener("input",e=>{const q=e.target.value.toLocaleLowerCase();document.querySelectorAll("#files tr").forEach(r=>r.hidden=!r.textContent.toLocaleLowerCase().includes(q))})</script></html>')
(B/'00_Оглавление.html').write_text(''.join(parts))
(B/'README.md').write_text(f'''# Машина — версия 1.0

Откройте [00_Оглавление.html](00_Оглавление.html) в браузере. Это самостоятельная папка с физическими копиями документов; оригиналы не перемещены, символьных ссылок нет. Копии сохраняют точные байты и исходную структуру путей в «Документы». Снимок базы `{base}` от11.09.2026; не редактировать этот выпущенный комплект, следующие изменения — версия1.1.

Включены M01–M07 полностью, G03 обеих версий, G01/G02, исходные PDF/DWG/Rhino и EXP-003 с геометрическими зависимостями, требования, пустая основа УТВ, ведомости цен/комплектности и протоколы проверок. Сопутствующие документы общей яхты вложены как исходная подоснова и зависимости ссылок, а не как новая смета этих частей. Актуальные документы выделены в оглавлении, ранние выпуски сохраняют исторические статусы.

Оценённая часть M07 —131819,50EUR с налогом,8оценённыхстрок/30безсуммы; это не полный бюджет. Полы/облик/компоновка не утверждены. G03v002 содержит неразмещённый гидропривод и сервисные конфликты. RFQ — проект, не отправлен; индивидуальные КП не получены. Общие каталоги и публичные цены не называются КП.

Полные сторонние PDF в «Каталоги производителей» локальные и исключены из Git; в публичной версии остаются реестр, SHA и имеющиеся URL. Одинаковые PDF по содержимому хранятся один раз; реестр показывает все исходные вхождения. У старых записей без восстановленного URL сохраняется путь архива и связанный исследовательский выпуск, адрес не придуман. Воспроизведение кода дополнительно требует исходных Linux-инструментов/библиотек; они в пакет не входят.

Скопировано {len(files)} публичных файлов, {len(byhash)} уникальных локальных PDF из {len(catalog)} вхождений. Реестр — [Документы.csv](Реестры/Документы.csv), [каталоги](Реестры/Каталоги.json). Исходные файлы не исправлялись: прежние недоступные ссылки перечислены в [реестре ссылок](Реестры/Ссылки-исходников.json). Для основной навигации используйте проверенное HTML-оглавление. Интернет-URL могут требовать сети, CSV/MD открываются редактором, CAD — установленным CAD-приложением.
''')
print(json.dumps(summary,ensure_ascii=False,indent=2))
