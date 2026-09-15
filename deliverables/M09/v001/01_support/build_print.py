from pathlib import Path
import csv,json,textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
S=Path(__file__).resolve().parent
rows=list(csv.DictReader((S/'estimate-lines.csv').open(),delimiter=';'))
t=json.loads((S/'totals.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
def money(v):return f'{float(v):,.2f}'.replace(',',' ').replace('.',',') if v not in ('',None) else '—'
with PdfPages(S/'01_estimate-print.pdf') as pdf:
 f=plt.figure(figsize=(16.54,11.69))
 f.text(.05,.94,'Машинное отделение / Рабочая смета',fontsize=25,color='#234351')
 f.text(.05,.89,'M09/v001 • 15.09.2026 • Цены SVB и других морских магазинов. Предварительный состав.',fontsize=12)
 f.text(.05,.77,money(t['known_gross_mixed_basis_eur'])+' EUR',fontsize=36,color='#234351')
 f.text(.05,.72,'Оценённая часть с налоговыми пометками. Полный бюджет установленного МО не определён.',fontsize=14,color='#ad4149')
 data=[['Известный NET',money(t['known_net_eur'])],['Предварительный НДС 23%',money(t['estimated_vat_identified_part_eur'])],['Цены продавцов с невыделенным налогом',money(t['source_gross_tax_not_split_eur'])],['Оценённая часть основного сценария',money(t['known_gross_mixed_basis_eur'])],['Опциональное отопление — вне итога',money(t['optional_gross_eur'])]]
 ax=f.add_axes([.05,.39,.9,.27]);ax.axis('off')
 tb=ax.table(cellText=data,colLabels=['Основание','EUR'],colWidths=[.72,.28],cellLoc='left',loc='center');tb.auto_set_font_size(False);tb.set_fontsize(13);tb.scale(1,2.4)
 for (i,j),cell in tb.get_celld().items():
  if i==0:cell.set_facecolor('#234351');cell.set_text_props(color='white')
 f.text(.05,.30,f"{t['new_price_records']} новых ценовых карточек; {t['priced_gross_rows']} основных строк с суммой, {t['unpriced_gross_rows']} без суммы; одна опция отдельно.",fontsize=13)
 f.text(.05,.24,'Основные агрегаты сохранены: 1 двигатель с редуктором, 2 генератора, 2 основных инвертора, 6+2+1 АКБ.\nКоличества мелких компонентов — явные предварительные допущения, не ведомость закупки.',fontsize=12,linespacing=1.6)
 f.text(.05,.16,'12 V стартерные аналоги не меняют требование сети 24 V. PTO, пожарный объём и диаметры не согласованы.\nМонтаж, трассы, фундаменты, доставка/ввоз, наладка и остатки систем требуют дальнейшей оценки.',fontsize=12,linespacing=1.6)
 f.text(.05,.075,'НДС 23% — предварительный сценарий D030. SOURCE_GROSS переносится без повторного начисления.\nИсходные M03/M07 сохранены. Это рабочая оценка, не утверждённая УТВ и не подтверждение поставки.',fontsize=11,linespacing=1.6)
 pdf.savefig(f);f.savefig(S/'summary.png',dpi=110);plt.close(f)
 for start in range(0,len(rows),15):
  f=plt.figure(figsize=(16.54,11.69));f.text(.04,.95,'МО / Смета компонентов с налоговой колонкой',fontsize=22,color='#234351')
  f.text(.04,.91,'M09/v001 • EUR • «—» означает не оценено или налог не выделен. ОПЦИЯ не входит в основной итог.',fontsize=11)
  data=[]
  for r in rows[start:start+15]:
   name=('ОПЦИЯ: ' if r['included']=='False' else '')+r['name']
   name='\n'.join(textwrap.wrap(name,52))
   tax='Налог продавца\nне выделен' if r['tax_mode']=='SOURCE_GROSS' else '23% план'
   data.append([r['id'],name,r['qty'] or '—',money(r['net_eur']),tax,money(r['vat_eur']),money(r['gross_eur'])])
  ax=f.add_axes([.04,.13,.92,.73]);ax.axis('off')
  tb=ax.table(cellText=data,colLabels=['ID','Компонент / открытый остаток','Кол-во','NET','Налог','НДС','С налогом'],colWidths=[.13,.35,.06,.12,.12,.10,.12],cellLoc='left',loc='center');tb.auto_set_font_size(False);tb.set_fontsize(9.2)
  for (i,j),cell in tb.get_celld().items():
   cell.set_height(.053)
   if i==0:cell.set_facecolor('#234351');cell.set_text_props(color='white')
   elif i%2==0:cell.set_facecolor('#f1f5f7')
  f.text(.04,.07,'Прямые ссылки, цены единиц, даты и основания количеств находятся в Excel. Пустые суммы сохраняют открытые затраты.',fontsize=10)
  f.text(.04,.035,'Основной частичный итог: '+money(t['known_gross_mixed_basis_eur'])+' EUR. Опция отдельно: '+money(t['optional_gross_eur'])+' EUR.',fontsize=10,color='#ad4149')
  pdf.savefig(f);plt.close(f)
