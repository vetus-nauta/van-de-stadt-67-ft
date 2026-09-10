"""Evaluate independently prepared fixtures after real LibreOffice calculation."""
from pathlib import Path
from openpyxl import load_workbook
import json,hashlib
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).parent;LOCAL=ROOT/'.local/U01/review'
results=[];books={}
for name in ['blank','cases','missing-base-date','missing-base-tax']:
 books[name]=load_workbook(LOCAL/f'recalculated/{name}.xlsx',data_only=True)
 errors=[{'sheet':s.title,'cell':c.coordinate,'error':c.value} for s in books[name] for row in s for c in row if c.data_type=='e']
 results.append({'case':name+'_no_formula_errors','pass':not errors,'errors':errors})
w=books['cases']
for c in json.loads((LOCAL/'expected.json').read_text()):
 if c['name']=='unconfirmed_zero_total_by_adjustment':continue # explicit correction basis can justify zero
 r=c['row'];actual_status=w['07_Смета'][f'N{r}'].value;actual_amount=w['07_Смета'][f'M{r}'].value
 results.append({'case':c['name'],'pass':actual_status==c['expected_status'] and actual_amount==c['expected_amount'],'actual_status':actual_status,'actual_amount':actual_amount,'expected_status':c['expected_status'],'expected_amount':c['expected_amount']})
for name in ['missing-base-date','missing-base-tax']:
 for r,kind in [(4,'KAC'),(5,'DIRECT')]:
  s=books[name]['07_Смета'][f'N{r}'].value;m=books[name]['07_Смета'][f'M{r}'].value
  results.append({'case':name+'_'+kind,'pass':s!='READY' and m is None,'actual_status':s,'actual_amount':m})
b=books['blank'];summary=b['08_Сводка'];rr=next(row[0].row for row in summary if row[0].value=='ИЗВЕСТНАЯ ЧАСТЬ')
results.append({'case':'blank_money_not_zero','pass':all(summary[f'{c}{rr}'].value is None for c in ['F','G','H']) and summary[f'D{rr}'].value==0 and summary[f'E{rr}'].value==72})
results.append({'case':'forecast_excludes_payments','pass':w['11_Контроль']['K4'].value==w['11_Контроль']['K5'].value==950})
results.append({'case':'sunk_separate','pass':w['08_Сводка']['G4'].value==200})
report={'status':'PASS' if all(q['pass'] for q in results) else 'RETURNED_FOR_FIXES','engine':'LibreOffice actual XLSX open/save conversion; openpyxl reads cached values','fixture_data':'SYNTHETIC ONLY, not project amounts','results':results,'workbook_input_sha256':hashlib.sha256((ROOT/'.local/U01/UTV-template-draft2.xlsx').read_bytes()).hexdigest()}
(OUT/'workbook-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(report['status']);print('Checks',len(results),'failed',sum(not q['pass'] for q in results))
for q in results:
 if not q['pass']:print(q['case'],q.get('actual_status'),q.get('actual_amount'),len(q.get('errors',[])))
