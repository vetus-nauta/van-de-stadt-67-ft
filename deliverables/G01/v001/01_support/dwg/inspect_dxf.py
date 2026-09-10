"""G01: inventory a converted DXF; never modify input. Run from repo root."""
import json,csv,hashlib,collections,pathlib,argparse
import ezdxf
from ezdxf import bbox
ROOT=pathlib.Path.cwd()
parser=argparse.ArgumentParser();parser.add_argument('--out-dir',default='.local/G01/dwg/recheck');args=parser.parse_args()
OUT=(ROOT/args.out_dir).resolve();OUT.mkdir(parents=True,exist_ok=True)
p=OUT/'lines-derived.dxf'; doc=ezdxf.readfile(p)
def serial(x):
 try:return list(x)
 except TypeError:return str(x)
def dump(n,obj): (OUT/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=serial)+'\n')
def csvout(n,rows,fields):
 with (OUT/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
entities=[];texts=[];dims=[]
for ly in doc.layouts:
 for e in ly:
  row={'layout':ly.name,'handle':e.dxf.handle,'type':e.dxftype(),'layer':e.dxf.layer}
  try:
   b=bbox.extents([e]);row['bbox_min']=list(b.extmin) if b.has_data else None;row['bbox_max']=list(b.extmax) if b.has_data else None
  except Exception as ex:row['bbox_error']=str(ex)
  entities.append(row)
  if e.dxftype() in ('TEXT','MTEXT','ATTRIB','ATTDEF'):
   texts.append(dict(row,text=e.plain_text() if hasattr(e,'plain_text') else e.dxf.get('text',''),attributes=e.dxf.all_existing_dxf_attribs()))
  if e.dxftype()=='DIMENSION':dims.append(dict(row,attributes=e.dxf.all_existing_dxf_attribs(),measured=e.get_measurement()))
audit=ezdxf.readfile(p).audit()
header={k:doc.header.get(k) for k in ['$ACADVER','$INSUNITS','$MEASUREMENT','$LUNITS','$LUPREC','$AUNITS','$DIMSCALE','$DIMLFAC','$INSBASE','$EXTMIN','$EXTMAX','$LIMMIN','$LIMMAX','$UCSORG','$UCSXDIR','$UCSYDIR']}
layers=[dict(x.dxf.all_existing_dxf_attribs(),off=x.is_off(),frozen=x.is_frozen(),locked=x.is_locked(),entities=sum(e['layer']==x.dxf.name for e in entities)) for x in doc.layers]
blocks=[{'name':b.name,'base_point':list(b.block.dxf.base_point),'flags':b.block.dxf.flags,'xref_path':b.block.dxf.get('xref_path',''),'count':len(b),'types':dict(collections.Counter(e.dxftype() for e in b))} for b in doc.blocks]
summary={'input':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'ezdxf':ezdxf.__version__,'header':header,'layouts':[{ 'name':l.name,'count':len(l),'types':dict(collections.Counter(e.dxftype() for e in l))} for l in doc.layouts],'audit_errors':[{'code':int(e.code),'message':e.message} for e in audit.errors],'audit_fixes':[{'code':int(e.code),'message':e.message} for e in audit.fixes],'layers':layers,'blocks':blocks,'dimension_count':len(dims),'text_count':len(texts),'warning':'Derived DXF only. Empty audit does not establish DWG conversion equivalence.'}
summary['block_texts']=[{'block':b.name,'handle':e.dxf.handle,'text':e.dxf.text} for b in doc.blocks if not b.name.startswith('*Model') for e in b if e.dxftype()=='TEXT']
summary['inserts']=[{'handle':e.dxf.handle,'name':e.dxf.name,'point':list(e.dxf.insert),'scale':[e.dxf.xscale,e.dxf.yscale,e.dxf.zscale]} for e in doc.modelspace().query('INSERT')]
dump('inventory.json',summary);dump('entities.json',entities);dump('texts.json',texts);dump('dimensions.json',dims)
csvout('layers.csv',[{'name':x['name'],'color':x.get('color'),'off':x['off'],'frozen':x['frozen'],'locked':x['locked'],'entities':x['entities']} for x in layers],['name','color','off','frozen','locked','entities'])
from ezdxf.addons.drawing import Frontend,RenderContext
from ezdxf.addons.drawing import layout,svg
viewdoc=ezdxf.readfile(p);viewaudit=viewdoc.audit()
backend=svg.SVGBackend();Frontend(RenderContext(viewdoc),backend).draw_layout(viewdoc.modelspace(),finalize=True)
(OUT/'lines-derived.svg').write_text(backend.get_string(layout.Page(0,0)))
print(json.dumps({k:summary[k] for k in ['header','layouts','dimension_count','text_count']},default=serial,indent=2))

from ezdxf.addons.drawing import matplotlib as drawing_matplotlib
drawing_matplotlib.qsave(viewdoc.modelspace(),OUT/'lines-derived-preview.png',dpi=170,bg='#FFFFFF',fg='#222222')
import matplotlib.pyplot as plt
from ezdxf.path import make_path
fig,axes=plt.subplots(3,1,figsize=(14,15));segments=[];skipped=[]
for e in doc.modelspace():
 if e.dxftype() not in ('LINE','ARC','LWPOLYLINE','POLYLINE'):continue
 try:
  pts=[tuple(v) for v in make_path(e).flattening(distance=2)]
  segments.append({'handle':e.dxf.handle,'layer':e.dxf.layer,'points':pts})
 except Exception as ex:skipped.append({'handle':e.dxf.handle,'error':str(ex)})
for ax,(i,j,title) in zip(axes,[(0,1,'XY: transverse / vertical (inferred)'),(2,0,'ZX: longitudinal / transverse (inferred)'),(2,1,'ZY: longitudinal / vertical (inferred)')]):
 for segment in segments:
  pts=segment['points'];ax.plot([v[i] for v in pts],[v[j] for v in pts],lw=.35)
 ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_title(title+' — raw drawing units; all linework, not hull envelope')
fig.tight_layout();fig.savefig(OUT/'orthographic-linework.png',dpi=140);plt.close(fig)
dump('projection-log.json',{'curves_plotted':len(segments),'excluded_types':['TEXT','INSERT','VIEWPORT'],'flattening_distance_drawing_units':2,'failed':skipped,'scope':'All direct model linework; no block expansion; not hull dimensions.'})
