from pathlib import Path
import csv,json,textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
S=Path(__file__).resolve().parent;rows=list(csv.DictReader((S/'estimate-lines.csv').open(),delimiter=';'));tot=json.loads((S/'totals.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
def money(x):return f'{float(x):,.2f}'.replace(',',' ').replace('.',',') if x else '—'
pdf=PdfPages(S/'01_estimate-print.pdf')
f=plt.figure(figsize=(16.54,11.69));f.text(.05,.94,'МО / Рабочая смета по имеющимся данным',fontsize=23,color='#234351');f.text(.05,.90,'M07/v001 • 11.09.2026 • Фиксация текущего состава и цен. Компоновка по сечениям — отдельная следующая работа.',fontsize=11)
f.text(.05,.80,'Оценённая часть с НДС',fontsize=16);f.text(.05,.73,money(tot['known_gross_mixed_basis_eur'])+' EUR',fontsize=34,color='#234351')
f.text(.05,.68,'Частичный ориентир. Полная стоимость установленного МО ещё не определена.',fontsize=13,color='#ad4149')
data=[['Известная часть без НДС',money(tot['known_net_eur'])+' EUR','7 строк; Yanmar сюда не входит'],['Расчётный НДС23% на эти строки',money(tot['estimated_vat_identified_part_eur'])+' EUR','Округление каждой строки до цента'],['Yanmar: исходная цена с НДС',money(tot['source_gross_tax_not_split_eur'])+' EUR','Ставка в источнике неизвестна; повторного23% нет'],['Всего оценено',money(tot['known_gross_mixed_basis_eur'])+' EUR','8 строк из38; остальные30 — без суммы']]
ax=f.add_axes([.05,.39,.90,.24]);ax.axis('off');tb=ax.table(cellText=data,colLabels=['Основание','Сумма','Ограничение'],colWidths=[.38,.20,.42],cellLoc='left',loc='center');tb.auto_set_font_size(False);tb.set_fontsize(12);tb.scale(1,2.5)
for (r,c),cell in tb.get_celld().items():
 if r==0:cell.set_facecolor('#234351');cell.set_text_props(color='white')
f.text(.05,.29,'Включено в перечень: двигатель с редуктором,2 генератора,2 инвертора,9 АКБ,2 водяные установки,опреснитель,2 чиллера,\nгидравлика,щитовая аппаратура,сервисные системы и открытые монтажные работы.',fontsize=12,linespacing=1.5)
f.text(.05,.20,'НДС находится в колонках самой сметы.23% — предварительное допущение владельца; фактический режим закупки/ввоза уточняется.\nИтог смешивает этот расчёт с опубликованной gross-ценой Yanmar, а не представляет единую польскую налоговую базу.',fontsize=11,linespacing=1.5)
f.text(.05,.12,'Монтаж,трассы,фундаменты,доставка/таможня,ПНР и часть комплектности не оценены. Неизвестное не заменено нулями.\nM05: отдельные редуктор/панель/демпфер/охладитель для6LPA сохранены приложением и не добавлены повторно к8LV.',fontsize=11,linespacing=1.5)
f.text(.05,.055,'Это рабочий выпуск, не утверждённая УТВ и не разрешение закупки. Основной файл — 00_engine-room-estimate.xlsx с формулами и прямыми ссылками.',fontsize=10,color='#657780')
pdf.savefig(f);f.savefig(S/'summary.png',dpi=110);plt.close(f)
for page,start in enumerate(range(0,len(rows),19),2):
 f=plt.figure(figsize=(16.54,11.69));f.text(.035,.95,'МО / Построчная смета с налоговой колонкой',fontsize=22,color='#234351');f.text(.035,.912,f'M07/v001 • лист{page} • EUR • «—» означает не оценено/не выделено, а не ноль. PL23 — предварительный сценарий.',fontsize=11)
 data=[]
 for r in rows[start:start+19]:
  name='\n'.join(textwrap.wrap(r['name'],width=48))
  mark='НДС продавца\nставка неизвестна' if r['tax_mode']=='SOURCE_GROSS' else ('23% расчётно' if r['rate'] else 'Уточнить')
  data.append([r['id'],name,r['qty'] or '—',money(r['net_eur']),mark,money(r['vat_eur']),money(r['gross_eur'])])
 ax=f.add_axes([.035,.13,.93,.73]);ax.axis('off');tb=ax.table(cellText=data,colLabels=['Строка','Наименование','Кол-во','Без НДС','Налог','НДС','С НДС'],colWidths=[.13,.35,.06,.11,.13,.10,.12],cellLoc='left',loc='center');tb.auto_set_font_size(False);tb.set_fontsize(9.4)
 for (r,c),cell in tb.get_celld().items():
  cell.set_height(.045 if r==0 else .046)
  if r==0:cell.set_facecolor('#234351');cell.set_text_props(color='white',weight='bold')
  elif r%2==0:cell.set_facecolor('#f0f5f7')
 f.text(.035,.075,'Источник,цена единицы,валюта,состав и прямой URL — в основной книге. Пустая цена или количество сохраняют открытое обязательство оценки.',fontsize=10)
 f.text(.035,.04,'Итог оценённых строк всех листов: '+money(tot['known_gross_mixed_basis_eur'])+' EUR. Полный бюджет МО не определён; альтернативыA/B/C не суммируются.',fontsize=10,color='#ad4149')
 pdf.savefig(f);plt.close(f)
pdf.close()
