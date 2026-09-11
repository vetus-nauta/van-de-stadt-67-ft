"""G03 approximate central machinery compartment: numerical proposal and plots.
Run from repository root using .local/cad-tools/rhino/venv/bin/python.
Original CAD/EXP003 files are read only. No equipment fit or strength approval.
"""
from pathlib import Path
import csv, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_pdf import PdfPages

S=Path(__file__).resolve().parent
R=S.parents[3]
ga=json.loads((S/'source-plan.json').read_text())
geom=json.loads((S/'geometry-basis.json').read_text())
old=ga['zones'][0]
inner=ga['zones'][1]
bc={r['zone']:r for r in geom['alternative_B_checks']}
er=bc['B3_ER_with_walls']; walk=bc['B3_passage']
up=lambda z: math.ceil((z-1e-10)/.05)*.05
floor=round(up(er['min_floor_with_150mm_reserve']),2)
walkfloor=round(up(walk['min_floor_with_150mm_reserve']),2)
saloon=1.10; slab=.18; ceiling=round(saloon-slab,2)
x0,x1,y0,y1=er['bounds_xy_m']; L=x1-x0; W=y1-y0; wall=.10
area=round(L*W,2); clean=round((L-2*wall)*(W-2*wall),2)
H=round(ceiling-floor,2); volume=round(clean*H,2)
roof=walk['conservative_roof_bottom_m']
roofmargin=round(walk['reserved_inner_halfwidth_m']-abs(walk['bounds_xy_m'][2]),2)
cabinfront=ga['bulkhead_X_bow_m'][1]-.2091
proposal={
 'status':'APPROXIMATE_PLANNING_PROPOSAL_NOT_APPROVED_LAYOUT',
 'owner_requirements':['Central engine room','Passage alongside galley','Lower galley confirmed by owner'],
 'source_geometry':'G02/EXP003 coordinates; bow-only GA overlay is approximate, not as-built registration',
 'plan_y_convention':'Y+ labelled port for this symmetric-hull overlay; no claim of independently proved native side naming',
 'ga_source':{'outer_area_m2':old['rectangle_area_m2'],'inner_drawn_area_m2':inner['rectangle_area_m2'],'outer_dimensions_m':[old['length_m'],old['width_m']],'outer_centre_y_m':round(sum(old['Y_port_m'])/2,3)},
 'A':{'outer_dimensions_m':[3.6,2.6],'outer_area_m2':9.36,'inner_dimensions_m':[3.4,2.4],'inner_area_m2':8.16,'corridor_width_m':.75,'corridor_headroom_low_deck_m':1.6865,'status':'REJECTED_FOR_TWO_METRE_SIDE_PASSAGE_WITH_EXISTING_DECK'},
 'B':{'geometry_basis_key':'B3_ER_with_walls / B3_passage','outer_bounds_xy_m':[x0,x1,y0,y1],'outer_dimensions_m':[round(L,2),round(W,2)],'wall_reserve_m':wall,'outer_area_m2':area,'inner_dimensions_m':[round(L-2*wall,2),round(W-2*wall,2)],'inner_area_m2':clean,'clear_geometric_height_m':H,'geometric_volume_m3':volume,'floor_z_m':floor,'ceiling_z_m':ceiling,'saloon_floor_z_m':saloon,'floor_slab_reserve_m':slab,'underfloor_reserve_m':.15,'floor_margin_above_sampled_shell_m':round(floor-er['max_shell_point']['z'],6),'centre_y_m':0,'inner_area_change_vs_GA_m2':round(clean-inner['rectangle_area_m2'],2),'inner_area_change_percent':round((clean/inner['rectangle_area_m2']-1)*100,1),'aft_extension_vs_GA_m':round(old['Xw_overlay_approx_m'][0]-x0,2),'aft_cabin_longitudinal_overlap_m':round(cabinfront-x0,2)},
 'passage':{'bounds_xy_m':walk['bounds_xy_m'],'clear_width_m':.70,'floor_z_m':walkfloor,'length_along_room_m':round(L,2),'area_along_room_m2':round(L*.70,2),'minimum_conservative_canopy_underside_z_m':roof,'open_well_geometric_height_after_alteration_m':round(roof-walkfloor,3),'saloon_headroom_to_conservative_canopy_m':round(roof-saloon,3),'side_structure_allowance_m':.10,'remaining_lateral_margin_m':roofmargin,'floor_margin_above_sampled_shell_m':round(walkfloor-walk['max_shell_point']['z'],6),'condition':'Requires redesign/opening of intervening salon floor and any obstructing original deck/liner over passage; no existing clear headroom claimed','galley_continuation':'Direction shown; furniture/doors/stairs and complete through-route not verified'},
 'height_sensitivity':{'floor_assumption_variation_m':.05,'ceiling_assumption_variation_m':.05,'clear_height_interval_m':[round(H-.10,2),round(H+.10,2)],'meaning':'Sensitivity to assumed construction/floor levels, not a surveyed confidence interval'},
 'two_metre_ER_scenario':{'required_saloon_floor_z_m':round(floor+2+slab,2),'required_raise_saloon_floor_m':round(floor+2+slab-saloon,2),'remaining_upper_headroom_m':round(roof-(floor+2+slab),3),'required_additional_roof_underside_raise_for_two_metre_saloon_m':round(2+(floor+2+slab)-roof,3),'status':'NOT_ADOPTED_REQUIRES_NEW_SUPERSTRUCTURE_AND_STRUCTURAL_DESIGN'},
 'limits':['Sampled historical mesh, not measured interior','150mm bottom reserve,100mm walls and180mm slab are planning allowances, not approved scantlings','No machinery, foundations, tanks, exhaust or service envelopes deducted from net area','Two-centimetre lateral residual is not an installation tolerance or demonstrated structural fit','Existing companion stair/WC and aft cabin layout intersect the new envelope','Shaft line/foundations and structural openings require separate design']}
(S/'proposal.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n')
with (S/'area-height.csv').open('w',newline='') as f:
 w=csv.writer(f,delimiter=';',lineterminator='\n');w.writerow(['case','outer_length_m','outer_width_m','outer_area_m2','inner_length_m','inner_width_m','inner_area_m2','clear_height_m','passage_width_m','status'])
 w.writerow(['GA source',old['length_m'],old['width_m'],9.36,inner['length_m'],inner['width_m'],8.18,'','','CALIBRATED_DRAWING_NOT_AS_BUILT'])
 w.writerow(['A',3.6,2.6,9.36,3.4,2.4,8.16,'',.75,'LOW_PASSAGE_HEADROOM_REJECTED'])
 w.writerow(['B',round(L,2),round(W,2),area,round(L-.2,2),round(W-.2,2),clean,H,.70,'CONDITIONAL_PROPOSAL'])

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':13,'axes.labelsize':10,'svg.fonttype':'none'})
colors={'blue':'#237699','green':'#37856a','orange':'#bb713e','red':'#b33f48','grey':'#60717b','purple':'#715b8d'}
curves=json.loads((R/'deliverables/G02/v001/01_support/layout/backdrop-curves.json').read_text())
def plan_base(ax):
 for key in ['133','144','478']:
  ax.add_collection(LineCollection([[(p[0],p[1]) for p in e] for e in curves[key]],colors='#bcc7cc',linewidths=.65))
 ax.axhline(0,color='#67757a',lw=.8,ls='-.')
 ax.set(xlim=(-16.2,-8.4),ylim=(-3.15,3.15),xlabel='X рабочая, м — к носу →',ylabel='Y, м  (левый борт +)')
 ax.set_aspect('equal');ax.grid(alpha=.15)
def rect(ax,xlo,xhi,ylo,yhi,**kw):
 r=Rectangle((xlo,ylo),xhi-xlo,yhi-ylo,**kw);ax.add_patch(r);return r
def ga_zone(ax,name,**kw):
 z=next(x for x in ga['zones'] if x['name']==name);a,b=z['Xw_overlay_approx_m'];c,d=z['Y_port_m'];rect(ax,a,b,c,d,**kw)
def dim(ax,a,b,text,offset=(0,0),color='#223c49'):
 ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'<->','lw':1,'color':color})
 ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],text,ha='center',va='center',color=color,fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':1})

pdf=PdfPages(S.parent/'00_central-engine-room.pdf')
fig=plt.figure(figsize=(16.54,11.69))
fig.suptitle('VDS67  /  Центральное машинное отделение',x=.07,y=.955,ha='left',fontsize=23,color='#193848')
fig.text(.07,.921,'G03 • 11.09.2026 • предварительный пересчёт по GA и исторической 3D-геометрии',fontsize=12,color=colors['grey'])
ax1=fig.add_axes([.06,.29,.43,.58]);ax2=fig.add_axes([.53,.29,.43,.58])
for ax in [ax1,ax2]:plan_base(ax)
ax1.set_title('Исходный план: МО смещено влево',loc='left',pad=13)
ga_zone(ax1,'engine_room_outer_main_rectangle',facecolor='#f4dbc4',edgecolor=colors['orange'],lw=1.8)
ga_zone(ax1,'engine_room_inner_main_rectangle',facecolor='none',edgecolor=colors['orange'],lw=.7,ls='--')
ga_zone(ax1,'galley_appliance_band_starboard',facecolor='#e0e9d7',edgecolor=colors['green'],alpha=.8)
ga_zone(ax1,'aft_companion_stair_near_center',facecolor='#e8cdd0',edgecolor=colors['red'],hatch='///')
ax1.text(-12.45,.85,'МО ≈ 9,4 м²\nвнутри линий стен ≈ 8,2 м²',ha='center',va='center',fontsize=11)
ax1.text(-10.0,-1.7,'Нижний\nкамбуз',ha='center')
dim(ax1,(-13.642,3.0),(-11.265,3.0),'≈ 2,38 м',offset=(0,.0))
ax1.text(-15.1,.65,'Трап / WC',color=colors['red'],fontsize=9)
ax1.annotate('',xy=(-14.0,-.4),xytext=(-14.6,.6),arrowprops={'arrowstyle':'->','color':colors['red']})
ax2.set_title('Предлагаемый вариант B: МО по центру',loc='left',pad=13)
ga_zone(ax2,'engine_room_outer_main_rectangle',facecolor='none',edgecolor=colors['orange'],lw=1.1,ls='--')
ga_zone(ax2,'galley_appliance_band_starboard',facecolor='#e0e9d7',edgecolor=colors['green'],alpha=.65)
rect(ax2,x0,x1,y0,y1,facecolor='#c5e4ee',edgecolor=colors['blue'],lw=2)
rect(ax2,x0+.1,x1-.1,y0+.1,y1-.1,facecolor='none',edgecolor=colors['blue'],ls=':',lw=1)
rect(ax2,x0,x1,-1.75,-1.05,facecolor='#b4dcca',edgecolor=colors['green'],lw=1.5)
rect(ax2,x0,cabinfront,y0,y1,facecolor='none',edgecolor=colors['red'],hatch='///',lw=.8)
for name in ['aft_companion_stair_near_center','aft_starboard_stair']:
 ga_zone(ax2,name,facecolor='none',edgecolor=colors['red'],lw=1.1,ls='--')
ax2.text((x0+x1)/2,0,'МО 4,20 × 2,10 м\n8,82 м² снаружи / 7,60 м² внутри',ha='center',va='center',fontsize=11)
ax2.text((x0+x1)/2,-1.40,'Проход 0,70 м',ha='center',va='center',fontsize=10)
ax2.text(-10.02,-2.15,'Камбуз ниже салона\nмебель — следующий шаг',ha='center',fontsize=9)
ax2.annotate('',xy=(-9.15,-1.4),xytext=(-11.2,-1.4),arrowprops={'arrowstyle':'->','color':colors['green'],'lw':1.7,'linestyle':'--'})
dim(ax2,(x0,1.6),(x1,1.6),'4,20 м')
dim(ax2,(-10.8,-1.05),(-10.8,1.05),'2,10 м',offset=(.28,0))
ax2.text(x0+.12,2.2,'Корма: пересечение старого трапа/WC\nи ≈ 0,6 м передней части кормового блока',fontsize=9,color=colors['red'])
ax2.annotate('',xy=(x0+.3,.7),xytext=(x0+.3,2.05),arrowprops={'arrowstyle':'->','color':colors['red']})
table=fig.add_axes([.07,.115,.86,.13]);table.axis('off')
tb=table.table(cellText=[['Исходный GA','≈ 2,38 × 3,94','≈ 9,36','≈ 8,18','Пайол и чистая высота не установлены'],['A, проверен','3,60 × 2,60','9,36','8,16','Проход 0,75 м: местами лишь ≈ 1,69 м высоты'],['B, для дальнейшей проработки','4,20 × 2,10','8,82','7,60','МО ≈ 1,47 м; проход 0,70 м требует проёма сверху']],colLabels=['Вариант','Наружный габарит, м','Пятно, м²','Внутри стен, м²','Главное условие'],cellLoc='left',loc='center',colWidths=[.23,.17,.11,.13,.36])
tb.auto_set_font_size(False);tb.set_fontsize(10);tb.scale(1,1.8)
for (r,c),cell in tb.get_celld().items():
 cell.set_edgecolor('#d2dde1')
 if r==0:cell.set_facecolor('#193848');cell.set_text_props(color='white',weight='bold')
 elif r==3:cell.set_facecolor('#e1eef3')
fig.text(.07,.065,'Серый — проекция исходных кромок, не чистая внутренняя граница. Оранжевый пунктир — исходное МО. Красный — коллизии.',fontsize=10,color=colors['grey'])
fig.text(.07,.04,'GA привязан по носу приблизительно (положение ±0,2 м). Вариант B не подтверждает размещение агрегатов, проход через двери или прочность.',fontsize=10,color=colors['grey'])
pdf.savefig(fig);fig.savefig(S/'plan.png',dpi=150);fig.savefig(S/'plan.svg');plt.close(fig)

fig=plt.figure(figsize=(16.54,11.69))
fig.suptitle('Высота: два уровня и открытый боковой проход',x=.07,y=.955,ha='left',fontsize=22,color='#193848')
fig.text(.07,.919,'Контур сечения G02: X ≈ −12,25 м • уровни пола/перекрытия предложены, не взяты из исполнительного чертежа',fontsize=12,color=colors['grey'])
ax=fig.add_axes([.07,.30,.55,.56])
section_source=json.loads((R/'deliverables/G02/v001/01_support/alignment/sections-working.json').read_text())
cut=min(section_source,key=lambda s:abs(s['working_x_mm']+12250))
ax.add_collection(LineCollection([[(p[1]/1000,p[2]/1000) for p in segment] for segment in cut['rhino_mesh_segments_mm']],colors='#617987',linewidths=1.7))
ax.axvline(0,lw=.8,ls='-.',color='#859197')
rect(ax,-1.05,1.05,floor,ceiling,facecolor='#c5e4ee',edgecolor=colors['blue'],lw=2)
rect(ax,-1.05,1.05,ceiling,saloon,facecolor='#587e91',edgecolor='#587e91')
ax.plot([-1.05,1.65],[saloon,saloon],color='#315668',lw=2)
ax.plot([-1.75,-1.05],[saloon,saloon],color=colors['red'],ls='--',lw=2)
rect(ax,-1.75,-1.05,walkfloor,roof,facecolor='#c2e3d5',edgecolor='none',alpha=.55)
ax.plot([-1.75,-1.05],[walkfloor,walkfloor],color=colors['green'],lw=3)
ax.plot([-1.87,1.87],[roof,roof],color=colors['purple'],lw=2)
ax.text(0,roof+.13,'Консервативный низ крыши / набора EXP-003: Z = 3,125',ha='center',fontsize=9,color=colors['purple'])
ax.text(.15,-.05,'МО\nН ≈ 1,47 м',ha='center',fontsize=15,color='#1c516b')
ax.text(.45,2.18,'Верхний салон\n≈ 2,03 м до принятого\nнижнего резерва крыши',ha='center',fontsize=11)
ax.text(-2.95,.95,'Красный пунктир:\nперекрытие над проходом\nнужно переработать',color=colors['red'],fontsize=9)
ax.annotate('',xy=(-1.4,1.1),xytext=(-2.1,.92),arrowprops={'arrowstyle':'->','color':colors['red']})
# Two-metre reference figure; no anthropometric certification.
cx=-1.40;head=walkfloor+1.88
ax.add_patch(Circle((cx,head),.12,facecolor='none',edgecolor='#315f4f',lw=1.5))
ax.plot([cx,cx],[walkfloor+.8,walkfloor+1.76],color='#315f4f',lw=1.5)
for sign in [-1,1]:
 ax.plot([cx,cx+sign*.15],[walkfloor+.8,walkfloor],color='#315f4f',lw=1.5)
 ax.plot([cx,cx+sign*.22],[walkfloor+1.45,walkfloor+1.0],color='#315f4f',lw=1.5)
dim(ax,(-1.75,walkfloor-.14),(-1.05,walkfloor-.14),'0,70 м',offset=(0,-.05))
dim(ax,(1.27,floor),(1.27,ceiling),'1,47 м',offset=(.27,0))
ax.text(-1.78,2.43,'Открытый\nпроём',ha='center',color=colors['green'],fontsize=10)
ax.set(xlim=(-3.05,3.05),ylim=(-1.35,3.75),xlabel='Y поперёк корпуса, м',ylabel='Z рабочая, м — не фактическая ватерлиния')
ax.set_aspect('equal');ax.grid(alpha=.16)
notes=fig.add_axes([.67,.30,.28,.56]);notes.axis('off')
text=(f'РАСЧЁТНЫЕ УРОВНИ\n\nПайол МО: {floor:.2f} м\nНиз перекрытия: {ceiling:.2f} м\nПол салона: {saloon:.2f} м\nПерекрытие: {slab:.2f} м\nПайол прохода: {walkfloor:.2f} м\n\nПЛОЩАДЬ И ВЫСОТА\n\n4,00 × 1,90 = 7,60 м² внутри стен\n0,92 − (−0,55) = 1,47 м\nГеометрический объём ≈ 11,2 м³\n\nЭто объём до размещения агрегатов,\nфундаментов, труб и сервисных зон.\n\nУ прохода запас до условного\nвнутреннего края крыши — лишь 0,02 м.\nСтойки, ограждение и зазоры\nещё не спроектированы.')
notes.text(0,1,text,ha='left',va='top',fontsize=12,linespacing=1.5,color='#234453')
fig.text(.07,.20,'Почему не 2 м в МО: над ним сохранён верхний салон. Для 2 м при том же пайоле его пол нужно поднять на 0,53 м;',fontsize=12,color=colors['red'])
fig.text(.07,.173,'тогда сверху останется около 1,50 м. Два полноценных уровня по 2 м потребуют отдельного изменения надстройки.',fontsize=12,color=colors['red'])
fig.text(.07,.115,'Проверка днища выполнена по сетке исторической оболочки. Резерв под пайолом 0,15 м, стен 0,10 м и перекрытия 0,18 м — допущения.',fontsize=10,color=colors['grey'])
fig.text(.07,.085,'Разрез показывает предложенное открытие объёма над проходом; существующее перекрытие не объявлено уже вырезанным.',fontsize=10,color=colors['grey'])
fig.text(.07,.055,'Внешняя крыша EXP-003 сохранена. Продольная схема, новый трап, WC, границы кормовой каюты, вал и силовые связи требуют следующей итерации.',fontsize=10,color=colors['grey'])
pdf.savefig(fig);fig.savefig(S/'section.png',dpi=150);fig.savefig(S/'section.svg');plt.close(fig);pdf.close()
print(json.dumps({'outer_area_m2':area,'inner_area_m2':clean,'height_m':H,'volume_m3':volume,'corridor_width_m':.70,'floor_z_m':floor,'passage_floor_z_m':walkfloor,'roof_margin_m':roofmargin},ensure_ascii=False))
