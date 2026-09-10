"""G02 functional alternatives on native Rhino edges. No CAD source modification.
Run from repository root in the G01 rhino venv; output must be new/empty.
The rectangles are PROPOSED study allocations, never measured clear rooms.
"""
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np
import rhino3dm as r
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle

SOURCE=Path('documentation/01-hull-and-geometry/3d/2-1.3dm')
ALIGNMENT=Path('deliverables/G02/v001/01_support/alignment/curves-working.json')
ALIGNMENT_SHA='65206919803104ff3f0424c3f01770cab0909918bcf90644b56fff79addf63c1'
SHIFT=np.array([1294.16,19381.843773828055,24837.674386867988])
SHELL=[133,144]; DECK=[478]; ROOF=[198,333,334,335,336]
# d is a convenient PROPOSED station parameter, Xw[m]=d-20.5.
# It is not a surveyed distance from the transom.
ZONES=[]
def zone(option,key,level,d0,d1,y0,y1,label,kind,source,limit):
    ZONES.append(dict(option=option,zone_id=option+'-'+key,level=level,
      xw_min_m=d0-20.5,xw_max_m=d1-20.5,yw_min_m=y0,yw_max_m=y1,
      label=label,kind=kind,status='PROPOSED_NOT_FIT_CHECKED',source_refs=source,
      height_status='OPEN',limit=limit))
def make_zones():
    for op in ['A','B']:
        zone(op,'VIP','lower',16.1,18.3,-1.1,1.1,'VIP', 'cabin','P01;P03;L01','Чистая ширина сечения/высота/койка OPEN; оконечное хранение не отменено')
        zone(op,'GUEST','lower',11.9,14.9,.5,2.25,'GUEST','cabin','P01;P03;L01','Мебель и чистый проход не размещены')
        zone(op,'CONV','lower',11.9,13.9,-2.25,-.5,'CONVERTIBLE\n2 нижние + 1 верхняя?','cabin','P01;P03;L01','Конфигурация brief не доказана; голова/разложенная койка/доступ конфликтуют с E4')
        zone(op,'E2','lower',14.9,16.1,-1.6,-.45,'E2\nVIP','wet','P01;P03;L01','Частная дверь из VIP предлагается; душ и уклоны OPEN')
        zone(op,'E3','lower',14.9,16.1,.45,1.6,'E3\nGUEST','wet','P01;P03;L01','Частная дверь из GUEST в передний санузел предлагается; дверные створки/душ OPEN')
        zone(op,'E4','lower',13.9,14.9,-2,-.5,'E4\nCONV','wet','P03;L01','Новый четвёртый санузел отнимает длину convertible; ещё не полноценный ensuite')
        zone(op,'FORE','lower',18.3,19.6,-.6,.6,'Носовое\nхранение','service','P01;L01','Якорное/парусное назначение и перегородка OPEN')
        zone(op,'ROOF','upper',5.4,11.8,-2,2,'FC-01: зона исследования крыши','future','P04;L02','Продление рубки вперёд — только один условный сценарий; высота и опоры OPEN')
        zone(op,'HARDTOP','upper',2.5,5.4,-1.9,1.9,'FC-02\nHARDTOP','future','P04;L02','Опоры/гик/высота/обзор OPEN; не конструктивный контур')
        zone(op,'TECHUP','upper',5.5,6.8,-1.7,-.65,'Пульт /\nлестницы','service','P01;P03;L01','Количество экранов/ступени/обзор OPEN')
    zone('A','MASTER','lower',2.9,6.8,-1.9,1.9,'MASTER\nсохранение кормовой идеи','cabin','P01;P03;L01','Прямое наложение с резервом гаража; полный поперечный объём не доказан')
    zone('A','E1','lower',5.4,6.8,-1.9,-.8,'E1\nMASTER','wet','P01;P03;L01','Резерв внутри жилого блока; частный вход и душ OPEN')
    zone('A','GARAGE','lower',.4,4.9,-1.6,1.6,'ГАРАЖ: конфликт с MASTER\nRESERVED / MODEL_NOT_SELECTED','garage','P04;L03','Произвольный сравнительный резерв; не габарит тендера; наложение с резервом Master по рабочей продольной координате Xw от −17.6 до −15.6 м; эскизные границы, не обмер')
    zone('A','ER','lower',6.8,9.3,-.85,2.15,'МО\nдвигатель / генераторы?','machinery','P01;P03;L01','Контур условный; агрегаты/снятие/выхлоп/доступ не проверены')
    zone('A','GALLEY','lower',9.3,11.8,-2.35,-.5,'КАМБУЗ','social','P01;P03;L01','Сохранение нижнего камбуза; полный комплект техники OPEN')
    zone('A','DINING','lower',9.3,11.8,.5,2.35,'НИЖНЯЯ\nСТОЛОВАЯ','social','P01;L01','Конкурирует с хранением/техзонами')
    zone('A','SALOON','upper',6.9,9.6,-1.7,1.7,'ВЕРХНИЙ САЛОН','social','P01;P03;L01','Посадочные места/лестница/чистая высота OPEN')
    zone('B','GARAGE','lower',.4,5.4,-1.7,1.7,'ГАРАЖ: приоритет кормы\nRESERVED / MODEL_NOT_SELECTED','garage','P04;L03','Произвольный сравнительный резерв; рулевое/закрытие/проём/балка OPEN')
    zone('B','ER','lower',5.5,8.8,-.9,2.15,'МО / ТЕХЗОНЫ\nперекомпоновка','machinery','P01;P03;L01','Смещение относительно GA требует проверки фундаментов/вала/выноса; полная начинка OPEN')
    zone('B','MASTER','lower',8.9,11.8,-.15,2.35,'MASTER\nсторона Y+','cabin','P03;L01','Уступает проходу: цель full-beam не выполнена; высота/ширина кровати OPEN')
    zone('B','E1','lower',10.5,11.8,.9,2.35,'E1\nMASTER','wet','P03;L01','Резерв внутри Master уменьшает жилой объём; геометрия двери/душа OPEN')
    zone('B','UTILITY','lower',8.9,11.8,-2.3,-1,'СЕРВИС /\nХРАНЕНИЕ','service','P03;L01','Часть уступит лестнице/трассам; не место утверждённых батарей')
    zone('B','GALLEY','upper',9.6,11.8,-1.9,-.45,'КАМБУЗ\nнаверх','social','P03;L02','Передняя зона за частью старой крыши; зависит от определения FC-01 и высоты')
    zone('B','SALOON','upper',6.9,9.6,-1.7,1.7,'САЛОН + СТОЛОВАЯ','social','P03;L01','Замена нижней столовой верхней; обеденные места OPEN')
    zone('B','STOREUP','upper',9.6,11.8,.45,1.9,'ХРАНЕНИЕ /\nрабочая зона','service','P03;L02','Зависит от условного объёма рубки и доступа к палубе')

def run():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args()
    if a.out_dir.exists() and any(a.out_dir.iterdir()):p.error('Output directory must be new or empty')
    a.out_dir.mkdir(parents=True,exist_ok=True);make_zones()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='814ecb9ae6afa27963f288d52df8db9e67d5c43bf967131b89b5ff40f1c3caa8'
    assert hashlib.sha256(ALIGNMENT.read_bytes()).hexdigest()==ALIGNMENT_SHA
    working=json.loads(ALIGNMENT.read_text())
    assert np.allclose(np.asarray(working['native_to_working'])[:3,3],SHIFT,rtol=0,atol=1e-9)
    model=r.File3dm.Read(str(SOURCE)); curves={}
    for i in SHELL+DECK+ROOF:
        curves[i]=[]
        for edge in model.Objects[i].Geometry.Edges:
            dom=edge.Domain;pts=[]
            for t in np.linspace(dom.T0,dom.T1,257):
                pt=edge.PointAt(t);pts.append(((np.array([pt.X,pt.Y,pt.Z])+SHIFT)/1000).tolist())
            curves[i].append(pts)
    independent={i:[] for i in SHELL+DECK+ROOF}
    for group in ['shell','deck','roof']:
        for entry in working['groups'][group]:
            independent[entry['object_index']].append((np.asarray(entry['points_mm'])/1000).tolist())
    for i in curves:
        assert np.allclose(curves[i],independent[i],rtol=0,atol=1e-9),str(i)
    curves=independent
    colors={'cabin':'#cfe8e1','wet':'#8dccf2','machinery':'#c6bfaf','social':'#f9e8b3','service':'#ded7ef','garage':'#f8c3b9','future':'#fff4f1'}
    for op in ['A','B']:
        fig,axes=plt.subplots(3,1,figsize=(18,13),gridspec_kw={'height_ratios':[1,1,.65]},layout='constrained')
        for ax,level in zip(axes[:2],['lower','upper']):
            for i in SHELL+DECK:
                ax.add_collection(LineCollection([np.asarray(v)[:,:2] for v in curves[i]],colors='#5c6570' if i in SHELL else '#b4bdc3',linewidths=.65,zorder=1))
            for z in [z for z in ZONES if z['option']==op and z['level']==level]:
                x,y=z['xw_min_m'],z['yw_min_m'];w,h=z['xw_max_m']-x,z['yw_max_m']-y
                special=z['kind'] in ['future','garage']
                ax.add_patch(Rectangle((x,y),w,h,facecolor=colors[z['kind']],edgecolor='#a73b39' if special else '#566573',lw=1.2,alpha=.64 if special else .84,linestyle='--' if special else '-',hatch='///' if z['kind']=='garage' else None,zorder=2))
                if z['kind']!='future' or z['zone_id'].endswith('HARDTOP'):
                    label_y = 1.05 if z['zone_id']=='A-MASTER' else (-.35 if z['zone_id']=='A-GARAGE' else y+h/2)
                    ax.text(x+w/2,label_y,z['label'],ha='center',va='center',fontsize=7.5,zorder=5)
            if level=='upper':
                ax.add_collection(LineCollection([np.asarray(v)[:,:2] for i in ROOF for v in curves[i]],colors='#186ea0',linewidths=1,zorder=4))
                ax.text(-9.2,2.15,'FC-01: условный резерв впереди старой крыши; величина подъёма OPEN',fontsize=8,color='#a73b39',ha='center')
            else:
                # Schematic route centrelines only; no encoded clear width.
                route=[[-13.4,-1.25],[-11.3,-1.25],[-11.1,0],[-4.4,0]] if op=='A' else [[-15,-1.25],[-11.65,-1.25],[-11.6,-.6],[-8.7,-.6],[-8.55,0],[-4.4,0]]
                ax.plot(*np.asarray(route).T,color='#7346a8',lw=2,ls=':',zorder=6)
                ax.annotate('Боковой занос: сторона условная\nбалка / проём / траектория OPEN',xy=(-18,1.7),xytext=(-18,3.05),ha='center',fontsize=8,arrowprops={'arrowstyle':'->','color':'#a73b39'},color='#a73b39')
                ax.annotate('Прямоугольные резервы выходят за обвод!\nНужна новая форма / меньше полезного места',xy=(-5.6,2.25),xytext=(-5,3.05),ha='center',fontsize=8,color='#a73b39',arrowprops={'arrowstyle':'->','color':'#a73b39'})
                ax.text(-4.95,-2.7,'E1–E4: четыре резерва; двери/душ/высоты не проверены',fontsize=8,color='#a73b39',ha='center')
            ax.set_xlim(-21,.5);ax.set_ylim(-3.2,3.8);ax.set_aspect('equal');ax.grid(alpha=.12)
            ax.set_ylabel('Yw, м (стороны не назначены)');ax.set_xlabel('Xw, м → нос; рабочая система Rhino G02')
            ax.set_title(('Нижний уровень' if level=='lower' else 'Верхний уровень / палуба')+' — прямоугольники: функциональные предложения, не чистые помещения',loc='left',fontsize=11)
        ax=axes[2]
        for ids,c in [(SHELL+DECK,'#7d8790'),(ROOF,'#186ea0')]:
            ax.add_collection(LineCollection([np.asarray(v)[:,[0,2]] for i in ids for v in curves[i]],colors=c,linewidths=.8))
        ax.plot([-18,-15.1],[3.25,3.25],'--',color='#a73b39');ax.plot([-15.1,-8.7],[3.45,3.45],'--',color='#a73b39')
        ax.text(-17,3.5,'FC-02',color='#a73b39',ha='center',fontsize=9)
        ax.text(-11.7,3.7,'FC-01: показан принцип, не отметка крыши',color='#a73b39',ha='center',fontsize=9)
        ax.annotate('подъём OPEN',xy=(-12.8,3.4),xytext=(-12.8,2.8),arrowprops={'arrowstyle':'->'},fontsize=8)
        ax.set_xlim(-21,.5);ax.set_ylim(-1.5,4.2);ax.set_aspect('equal');ax.grid(alpha=.15)
        ax.set_xlabel('Xw, м');ax.set_ylabel('Zw, м');ax.set_title('Исторический профиль Rhino. Красные линии — символические намерения; полы/чистые высоты OPEN',loc='left',fontsize=10)
        fig.suptitle('VDS67 · G02 · '+op+(' — кормовой Master против гаража' if op=='A' else ' — гараж в корме, Master вперёд, камбуз наверх')+'\nКОНЦЕПТ / НЕ ДЛЯ ИЗГОТОВЛЕНИЯ · 3+1 / 4 ensuite — цели, помещаемость не подтверждена',fontsize=14)
        fig.savefig(a.out_dir/('option-'+op+'.png'),dpi=150);fig.savefig(a.out_dir/('option-'+op+'.svg'));plt.close(fig)
    with (a.out_dir/'zones.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(ZONES[0]),delimiter=';');w.writeheader();w.writerows(ZONES)
    metadata={'alignment_file':str(ALIGNMENT),'alignment_sha256':ALIGNMENT_SHA,'backdrop_independent_reproduction_matches_alignment_atol_m':1e-9,'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sample_points_per_edge':257,'transform_native_mm_to_working_mm_translation':SHIFT.tolist(),'plot_units':'m','symbolic_profile_marks_not_design_elevations':True,'plot_backdrop':'actual sampled Rhino trimmed edges; not inferred internal usable boundary','objects':[{'index':i,'id':str(model.Objects[i].Attributes.Id)} for i in SHELL+DECK+ROOF],'proposed_station_parameter':'Xw_m=d-20.5; d not surveyed distance from transom','zone_count':len(ZONES),'assumptions':['P01','P02','P03','P04','L01','L02','L03','L04'],'independent_fit_check':'NOT_DONE'}
    (a.out_dir/'sketch-provenance.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    (a.out_dir/'backdrop-curves.json').write_text(json.dumps(curves,allow_nan=False)+'\n')
    print(json.dumps({'out_dir':str(a.out_dir),'zones':len(ZONES),'source_sha256':metadata['sha256']}))
if __name__=='__main__':run()
