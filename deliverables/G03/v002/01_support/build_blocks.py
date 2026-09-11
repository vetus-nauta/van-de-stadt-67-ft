"""Editable rectangular equipment study; no original model or released files changed.
Run from repo with .local/cad-tools/rhino/venv/bin/python this_file.
"""
import json,csv,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
S=Path(__file__).resolve().parent; R=S.parents[3]
aux=json.loads((S/'auxiliary-basis.json').read_text()); A={b['block_id']:b for b in aux['blocks']}
B=[]
def block(i,ax,label,x,y,z,dx,dy,dz,zone='wet',note=''):
 B.append(dict(id=i,source_block=ax,label=label,zone=zone,xyz_m=[x,y,z],size_xyz_m=[dx,dy,dz],note=note))
block('D','MAIN','Yanmar + редуктор',.50,1.16,.15,1.34,.88,.766)
block('V','ME-03','Муфта / вал',0,1.40,.15,.50,.40,.35,note='Условная зона линии, не утверждённая ось/комплект')
for i,y in enumerate([.20,2.295],1):block('G'+str(i),'GEN','Panda '+str(i),2.75,y,.15,.450,.705,.590,note='Продольная ось генератора поперёк МО; ремни к центральному проходу')
block('H','AX09','Гидробак / фильтр',.60,0,.15,1,.45,.85)
block('W24','AX14','Вода 24 В',.60,2.8,.15,.65,.4,.55)
block('W220','AX15','Вода 220 В',1.30,2.8,.15,.65,.4,.55)
block('HW','AX16','ГВС / коллектор',3.85,.05,.15,.55,.90,.70)
for i,y in enumerate([1.05,1.60],1):block('C'+str(i),'AX11','Чиллер '+str(i),4.0,y,.15,.40,.45,.45)
block('CP','AX12','Насосы климата',4.0,2.35,.15,.40,.75,.60)
block('RO','AX13','Опреснитель 150 л/ч',2.0,0,1.20,1.2,.45,.55,note='Верхняя полка; извлечение мембраны вдоль x+ на1м, крепление не рассчитано')
block('F','AX17','Топливный стенд',.65,0,1.10,.8,.25,.7)
block('OIL','AX22','Маслосмена / контроль',1.50,0,1.20,.45,.20,.60)
for i,(x,y) in enumerate([(0,0),(0,2.75),(1.9,0)],1):block('EX'+str(i),'AX18','Охл./выхлоп '+str(i),x,y,.10,.60,.45,.60,note='Карманы трёх независимых контуров, уклоны/петли/противодавление не проверены')
block('BIL','AX19','Осушение',0,.65,.05,.50,.35,.40)
for i,(x,y) in enumerate([(0,0),(3.95,2.80)],1):block('AIR'+str(i),'AX21','Воздух '+str(i),x,y,1.10,.40,.40,.90,note='Шахта продолжается наружу; сечение не рассчитано')
# Dry cabinet faces forward; yaw maps face width to local y, depth to local x.
def dry(i,ax,label,y,z,w,h,depth):block(i,ax,label,4.5,y,z,depth,w,h,'dry')
for row,z in enumerate([.10,.90]):
 for c in range(3):dry('BS'+str(row*3+c+1),'AX03','С'+str(row*3+c+1),.05+.22*c,z,.22,.38,.45)
dry('BD','AX04','Пуск Д',.80,.10,.55,.38,.30)
dry('BG1','AX05','Пуск G1',.80,.90,.55,.38,.30)
dry('BG2','AX05','Пуск G2',.80,1.70,.55,.38,.30)
dry('DC','AX07','Щит 24 В / резерв пуска',1.40,.10,.8,.9,.3)
dry('AC','AX08','Щит 220 В',2.30,.10,.8,.9,.3)
dry('INV1','AX01','Инв. 1',1.45,1.20,.3,.55,.2)
dry('INV2','AX01','Инв. 2',1.90,1.20,.3,.55,.2)
dry('ISO','AX06','Берег',2.35,1.20,.35,.45,.3)
dry('IW','AX02','Резерв воды',2.80,1.20,.3,.35,.2)
# Deliberately not hidden inside occupied machine footprint.
unplaced=[{'id':'HP','source_block':'AX10','label':'Гидропривод / PTO / охладитель','size_m':[.8,.45,.6],'status':'UNPLACED_REQUIRED','reason':'Кинематика PTO и автономный режим не выбраны; пробное место у двигателя перекрывает сервис ремней.'},
{'id':'FIRE','source_block':'AX20','label':'Пожарный баллонный шкаф','size_m':[.4,.35,.9],'status':'EXTERNAL_LOCATION_OPEN','reason':'Доступ снаружи МО; место и заряд ещё не определены.'},
{'id':'TANK','source_block':'AX23','label':'Танки / интерфейсы','size_m':[.4,.25,.5],'status':'EXTERNAL_TANK_VOLUMES_OPEN','reason':'Размер только узла; объёмы танков не помещены в этот прямоугольник.'},
{'id':'SAN','source_block':'AX24','label':'Санитарный модуль','size_m':[.6,.4,.5],'status':'EXTERNAL_LOCATION_OPEN','reason':'Отдельная санитарная зона; трассы открыты.'},
{'id':'HEAT','source_block':'AX25','label':'Отопитель — условно','size_m':[.65,.4,.5],'status':'CONDITIONAL_NOT_ADOPTED','reason':'Отдельная опция; не обязательное добавление.'}]
# Access rectangles in plan; full-height approach, not swept tool or human simulation.
access=[]
def svc(i,owner,label,x,y,dx,dy):access.append(dict(id=i,owner=owner,label=label,xywh_m=[x,y,dx,dy],basis='PROJECT_RESERVE_NOT_OEM_MINIMUM'))
svc('D-L','D','Боковой доступ',.50,.56,1.34,.60);svc('D-R','D','Боковой доступ',.50,2.04,1.34,.60)
svc('D-F','D','Ремни',1.84,1.16,.50,.88);svc('D-A','D','Редуктор/вал',0,1.16,.50,.88)
for i,(y,front_y) in enumerate([(.2,.905),(2.295,1.795)],1):
 svc(f'G{i}-A',f'G{i}','Боковой сервис',2.25,y,.50,.705)
 svc(f'G{i}-B',f'G{i}','Боковой сервис',3.20,y,.50,.705)
 svc(f'G{i}-F',f'G{i}','Ремни',2.75,front_y,.45,.50)
svc('H-F','H','Сервис гидромодуля',.60,.45,1,.70)
for i,x in [('W24',.6),('W220',1.3)]:svc(i+'-F',i,'Сервис воды',x,2.15,.65,.65)
svc('FRONT','HW|C1|C2|CP','Сервис переднего ряда',3.20,.05,.65,3.05)
# Calculate body collisions, plus access conflicts excluding own integrated gear shaft.
def overlap(lo1,sz1,lo2,sz2):return all(min(a+d,b+e)-max(a,b)>1e-8 for a,d,b,e in zip(lo1,sz1,lo2,sz2))
clashes=[]
for i,b in enumerate(B):
 for c in B[i+1:]:
  if overlap(b['xyz_m'],b['size_xyz_m'],c['xyz_m'],c['size_xyz_m']):clashes.append([b['id'],c['id']])
service_conf=[]
for s in access:
 x,y,dx,dy=s['xywh_m']
 for b in B:
  if b['zone']!='wet' or b['id'] in s['owner'].split('|') or (s['id']=='D-A' and b['id']=='V'):continue
  if overlap([x,y,0],[dx,dy,2.10],b['xyz_m'],b['size_xyz_m']):service_conf.append({'service':s['id'],'obstacle':b['id']})
layout={'status':'BLOCK_TEST_NOT_MINIMUM_APPROVAL_OR_COMPLETE_FIT','units':'m','wet_inner_LWH':[4.4,3.2,2.1],'dry_inner_LWH':[.6,3.2,2.45],'wall_reserve_m':.1,'outer_technical_footprint_LW':[5.3,3.4],'outer_technical_area_m2':18.02,'wet_internal_area_m2':14.08,'dry_internal_area_m2':1.92,'external_galley_passage_width_m':.70,'external_dry_service_width_m':.75,'coordinate_note':'Localx forward, y from port wall to starboard; hull overlay X=x-15.37 Y=1.6-y. z relative to each proposed floor, no actual floor adopted.','blocks':B,'service_rectangles':access,'unplaced_or_external':unplaced,'body_clashes':clashes,'service_obstacles':service_conf,'limits':['No proved minimum permissible size','No complete fit: HP mandatory module not placed','External galley passage and cabinet service floor/headroom/steps unresolved','Upper modules and battery shelves require engineered supports and removal method','Service volumes may overlap each other for sequential maintenance','Removal of whole main engine requires dedicated hatch; ordinary door not enough','Electrical candidates 12V starters conflict with owner24V architecture until resolved; rectangles not electrical selection']}
(S/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
with (S/'blocks.csv').open('w',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['id','basis','label','zone','x','y','z','dx','dy','dz','note'])
 for b in B:w.writerow([b['id'],b['source_block'],b['label'],b['zone'],*b['xyz_m'],*b['size_xyz_m'],b['note']])
# Publication plots; rectangles remain editable as SVG, exact coordinates in JSON/CSV.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
COL={'wet':'#bfdeea','dry':'#f1deaf','upper':'#dacde8','green':'#43a886','red':'#bd4750','ink':'#234351'}
pdf=PdfPages(S.parent/'00_equipment-block-layout.pdf')
def T(f,*args,**kw):
 kw.setdefault('va','top'); return f.text(*args,**kw)
def page(title,sub):
 f=plt.figure(figsize=(16.54,11.69));T(f,.045,.95,title,fontsize=23,color=COL['ink']);T(f,.045,.916,sub,fontsize=11,color='#677780');return f
def box(ax,x,y,w,h,label='',color='#bfdeea',ls='-',alpha=1,fs=9):
 ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor=COL['ink'],linewidth=1,linestyle=ls,alpha=alpha));
 if label:ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=fs)
def save(f,name):
 pdf.savefig(f);f.savefig(S/(name+'.svg'));f.savefig(S/(name+'.png'),dpi=125);plt.close(f)
f=page('01 / Как размещаются основные узлы','G03/v002 • 11.09.2026 • Тест габаритов и сервисных резервов. Полы и облик не утверждаются.')
ax=f.add_axes([.045,.20,.70,.67]);box(ax,-.1,-.1,4.6,3.4,color='#e8ecee');box(ax,0,0,4.4,3.2,color='white');box(ax,4.5,0,.6,3.2,'СУХОЙ\nШКАФ\nлист 03',COL['dry'])
box(ax,-.1,3.3,6.05,.7,'Проход к нижнему камбузу 0,70 м — уровни открыты','#eef4e9',fs=10)
box(ax,5.2,0,.75,3.3,'Доступ\nк щитам\n0,75 м','#eef4e9')
for s in access:
 x,y,w,h=s['xywh_m'];ax.add_patch(Rectangle((x,y),w,h,facecolor=COL['green'],edgecolor=COL['green'],alpha=.10,ls='--'))
for b in B:
 if b['zone']!='wet' or b['xyz_m'][2]>=1:continue
 x,y,z=b['xyz_m'];dx,dy,dz=b['size_xyz_m'];box(ax,x,y,dx,dy,b['id']+'\n'+b['label'],COL['wet'],fs=8)
for b in B:
 if b['zone']=='wet' and b['xyz_m'][2]>=1:
  x,y,z=b['xyz_m'];dx,dy,dz=b['size_xyz_m'];ax.add_patch(Rectangle((x,y),dx,dy,facecolor='none',edgecolor='#795490',linestyle='--',linewidth=1.5));ax.text(x,y-.05,b['id']+' ↑',color='#795490',fontsize=9)
# Highlight unclosed generator service and upper-module conflicts.
for bid in ['EX3','RO']:
 b=next(q for q in B if q['id']==bid);x,y,z=b['xyz_m'];dx,dy,dz=b['size_xyz_m'];ax.add_patch(Rectangle((x,y),dx,dy,facecolor='none',edgecolor=COL['red'],linewidth=2,hatch='///'))
# Door opening and principal human routes; route is schematic, detailed connections remain open.
ax.plot([1.95,2.70],[3.25,3.25],color='white',lw=8);ax.annotate('Вход ≥0,75',xy=(2.32,3.2),xytext=(1.85,3.10),arrowprops={'arrowstyle':'->'},fontsize=9)
ax.annotate('',xy=(2.35,1.55),xytext=(2.35,3.5),arrowprops={'arrowstyle':'->','color':'#268163','lw':2})
ax.annotate('',xy=(3.6,1.55),xytext=(2.35,1.55),arrowprops={'arrowstyle':'->','color':'#268163','lw':2})
ax.text(1.12,.80,'0,71 м',fontsize=9,color='#26765c');ax.text(1.2,2.4,'0,76 м',fontsize=9,color='#26765c')
ax.set(xlim=(-.2,6.15),ylim=(4.15,-.35),xlabel='x, м → к носу',ylabel='y, м → правый борт');ax.set_aspect('equal');ax.grid(alpha=.12)
T(f,.775,.845,'ТЕСТОВЫЙ ОБЪЁМ',fontsize=14,color=COL['ink'])
T(f,.775,.79,'МО внутри: 4,40 × 3,20 м\nПлощадь: 14,08 м²\nВысота сценария: 2,10 м\n\nСухой шкаф: 0,60 × 3,20 м\nПлощадь: ещё 1,92 м²\nВысота шкафа: 2,45 м\n\nСо стенами: 5,30 × 3,40 м\nПятно: 18,02 м²\nВнешние проходы — сверх этого.',fontsize=11,linespacing=1.5)
T(f,.775,.38,'Не минимально допустимый\nразмер и не готовая компоновка.\n\nHP: гидропривод/PTO пока\nне размещён — см. лист 04.\nСервис верхних модулей\nимеет пересечения.',fontsize=11,color=COL['red'],linespacing=1.4)
T(f,.045,.125,'Синий — низкие агрегаты; фиолетовый пунктир — узлы выше них (лист 02); зелёный — сервисные резервы.',fontsize=11)
T(f,.045,.09,'1 двигатель с редуктором, 2 генератора, 2 чиллера, 2 водяные установки. Прямоугольники — корпуса или явно условные модули.',fontsize=10)
T(f,.045,.055,'Резервы сервиса назначены для этого теста. Соответствие установочным требованиям конкретной поставки ещё не доказано.',fontsize=10,color='#677780')
save(f,'01-plan')
f=page('02 / Что размещено выше пола','Высоты относительно условного пайола МО. Его абсолютная отметка не выбрана. Проекции показывают наложения по высоте.')
for pos,side,title in [([.06,.52,.60,.32],'port','Левый борт: гидравлика, топливо, опреснитель'),([.06,.10,.60,.32],'starboard','Правый борт: водяные насосы и генератор')]:
 ax=f.add_axes(pos);ax.set_title(title,loc='left',fontsize=12)
 for b in B:
  x,y,z=b['xyz_m'];dx,dy,dz=b['size_xyz_m']
  if b['zone']=='wet' and ((side=='port' and y<1) or (side=='starboard' and y>2.2)):
   box(ax,x,z,dx,dz,b['id']+'\n'+b['label'],COL['upper'] if z>=1 else COL['wet'],fs=8)
 ax.axhline(2.1,color=COL['red'],ls='--');ax.set(xlim=(-.05,4.5),ylim=(0,2.2),xlabel='x, м',ylabel='z над пайолом, м');ax.set_aspect('equal');ax.grid(alpha=.15)
T(f,.70,.82,'ОБСЛУЖИВАНИЕ',fontsize=14,color=COL['ink'])
T(f,.70,.765,'D: обе стороны по 0,60 м;\nремни и редуктор по 0,50 м.\nИмпеллер на противоположной\nстороне от основных фильтров.\n\nG1/G2: по бокам 0,50 м,\nсо стороны ремней 0,50 м.\nКапсулы снимаются вверх: запас\n0,35 м только предварительный.\n\nRO: над генератором; торцевое\nизвлечение мембран на 1,00 м\nв сторону носа ещё проверить.\n\nНижние агрегаты мешают\nвстать вплотную к верхним\nстендам F, OIL и RO. Нужны\nвыдвижные/съёмные узлы либо\nдругое размещение.',fontsize=11,linespacing=1.4)
T(f,.06,.047,'Сечение 2,10 м — требуемый для этого расположения резерв, а не утверждённая высота/уровень салона. Фундаменты условно 0,15 м.',fontsize=10,color='#677780')
save(f,'02-elevations')
f=page('03 / Сухой шкаф: все 9 батарей и электротехника','Отдельные батарейный и электрический отсеки внутри общего резерва; вентиляция и перегородки требуют расчёта.')
ax=f.add_axes([.06,.23,.66,.63]);box(ax,0,0,3.2,2.45,color='#fcfaf5');ax.axvline(1.375,color=COL['ink'],lw=2)
for b in B:
 if b['zone']=='dry':
  x,y,z=b['xyz_m'];dx,dy,dz=b['size_xyz_m'];box(ax,y,z,dy,dz,b['id']+'\n'+b['label'],COL['dry'],fs=8)
ax.set(xlim=(-.05,3.25),ylim=(0,2.52),xlabel='Ширина фасада, м',ylabel='Высота над полом шкафа, м');ax.set_aspect('equal');ax.grid(alpha=.15)
T(f,.755,.81,'КОЛИЧЕСТВА СОХРАНЕНЫ',fontsize=13,color=COL['ink'])
T(f,.755,.755,'BS1–BS6: 6 сервисных АКБ\nBD: 1 пусковая двигателя\nBG1/BG2: 2 пусковые генераторов\n\nINV1/INV2: 2 основных инвертора\nIW: независимый канал воды\nDC: 24 В, защиты, резерв пуска\nAC: 220 В, выбор источника\nISO: береговое разделение\n\nГлубина шкафа 0,60 м.\nПеред фасадом ≥0,75 м.\n\nПодъём батарей — поштучно;\nполки и грузовой доступ\nещё не спроектированы.\nШкаф 2,45 м — следствие\nпоказанной укладки,\nне утверждённая высота яхты.',fontsize=11,linespacing=1.4)
T(f,.06,.155,'«115 ампер», напряжение и химия каждой АКБ остаются открытыми. Размеры ячеек взяты как условные резервы, схема соединения не назначена.',fontsize=10)
T(f,.06,.115,'В корпусах-кандидатах двигателя и Panda штатный пуск 12 В. Для требования владельца 24 В нужна отдельная совместимая комплектация.',fontsize=10,color=COL['red'])
T(f,.06,.075,'Полки батарей нельзя объединять с электрическим отсеком без отдельной проработки вентиляции/изоляции. Верхние АКБ потребуют подъёмного приспособления.',fontsize=10,color='#677780')
save(f,'03-dry-cabinet')
f=page('04 / Где компоновка пока не проходит','Результат теста: геометрия основных агрегатов разложена, полного подтверждения помещаемости и сервиса пока нет.')
ax=f.add_axes([.045,.61,.91,.25]);ax.axis('off')
rows=[['4,00 × 1,90 м','7,60 м²','Не проходит: двигатель + 2 боковых резерва = 2,08 м'],['4,40 × 3,00 м','13,20 м²','У гидромодуля 0,61 м против принятого резерва 0,70 м'],['4,40 × 3,20 м','14,08 м²','Не закрыто: RO и EX3 мешают сервису G1; HP не размещён'],['Сухой шкаф 0,60 × 3,20','+1,92 м²','9 АКБ и электротехника показаны; высота 2,45 м']]
t=ax.table(cellText=rows,colLabels=['Внутренний габарит','Площадь','Проверка'],colWidths=[.24,.13,.63],cellLoc='left',loc='center');t.auto_set_font_size(False);t.set_fontsize(11);t.scale(1,2.1)
for (r,c),cell in t.get_celld().items():
 if r==0:cell.set_facecolor(COL['ink']);cell.set_text_props(color='white')
T(f,.045,.555,'ПРЯМОУГОЛЬНИКИ, КОТОРЫМ ЕЩЁ НУЖНО МЕСТО',fontsize=14,color=COL['red'])
ax=f.add_axes([.045,.34,.91,.18]);ax.axis('off')
for i,u in enumerate(unplaced):box(ax,i*.20,0,.18,.9,u['id']+'\n'+u['label']+'\n'+' × '.join(str(x) for x in u['size_m'])+' м',color='#f5dfe0',ls='--',fs=9)
ax.set(xlim=(0,1),ylim=(-.1,1))
T(f,.045,.28,'HP — обязательная гидравлическая функция не помещена. FIRE/SAN/TANK — вынесенные функции с незаданным местом; HEAT — условная опция.',fontsize=10)
T(f,.045,.235,'Демонтаж двигателя: нужен отдельный съёмный люк ориентировочно ≥1,60 × 1,10 м и расчёт подъёма. Дверь 0,75 м для двигателя не годится.',fontsize=11,color=COL['red'])
T(f,.045,.19,'Для расширенного МО оболочка проверяется отдельно. Снаружи проход смещается к борту: его пайол/ступени/потолок и связь с нижним камбузом не решены.',fontsize=10)
T(f,.045,.145,'Нельзя назначать новые полы из старых 1,47 м: сначала устраняем сервисные пересечения, размещаем гидропривод и трассы, затем увязываем уровни.',fontsize=10)
T(f,.045,.10,'RO / EX3 пересекают сервис G1; доступ к редуктору между кормовыми узлами и валом требует отдельной проверки. Эти объёмы не спрятаны в площади агрегатов.',fontsize=10)
T(f,.045,.055,'Предел проверки: прямоугольные корпуса и проектные зоны подхода. Не нормативный минимум, не расчёт прочности, не монтажный чертёж.',fontsize=10,color='#677780')
save(f,'04-open-issues');pdf.close()
print(json.dumps({'blocks':len(B),'body_clashes':clashes,'service_obstacles':service_conf,'unplaced':len(unplaced)},ensure_ascii=False))
