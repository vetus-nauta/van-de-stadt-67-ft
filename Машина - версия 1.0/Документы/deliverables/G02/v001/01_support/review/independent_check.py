"""Separate reviewer code; run from repo root in Rhino venv. No author code imported."""
import json, csv, hashlib, subprocess, sys
from pathlib import Path
import numpy as np
import rhino3dm as rh
P=Path('deliverables/G02/v001/01_support'); out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
assert not (out/'results.json').exists()
load=lambda f:json.loads((P/f).read_text())
t=load('alignment/transform.json');r={}
for a,b in [('dwg_to_rhino_native','rhino_native_to_dwg'),('rhino_native_to_working','working_to_rhino_native'),('dwg_to_working','working_to_dwg')]:
 d=float(np.max(abs(np.array(t[a])@np.array(t[b])-np.eye(4))));assert d<1e-10;r[a+'_inverse_max_error']=d
assert np.max(abs(np.array(t['rhino_native_to_working'])@np.array(t['dwg_to_rhino_native'])-t['dwg_to_working']))<1e-10
for f,h in t['inputs_sha256'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
model=rh.File3dm.Read('documentation/01-hull-and-geometry/3d/2-1.3dm'); objects={str(o.Attributes.Id):o for o in model.Objects};shift=np.array(t['rhino_native_to_working'])[:3,3]
back=load('layout/backdrop-curves.json');prov=load('layout/sketch-provenance.json')
assert hashlib.sha256(Path(prov['alignment_file']).read_bytes()).hexdigest()==prov['alignment_sha256']
maxerr=0;pointcount=0
for item in prov['objects']:
 obj=objects[item['id']];assert str(model.Objects[item['index']].Attributes.Id)==item['id']
 for edge,pts in zip(obj.Geometry.Edges,back[str(item['index'])]):
  assert len(pts)==257
  vals=[]
  for u in np.linspace(edge.Domain.T0,edge.Domain.T1,257):
   p=edge.PointAt(float(u));vals.append((np.array([p.X,p.Y,p.Z])+shift)/1000)
  maxerr=max(maxerr,float(np.max(abs(np.array(vals)-pts))));pointcount+=len(pts)
assert maxerr<1e-9;r['native_rhino_layout_points_checked']=pointcount;r['max_layout_point_delta_m']=maxerr
anchors=list(csv.DictReader((P/'alignment/anchors.csv').open()));res=[]
for row in anchors:
 d=np.array([float(row['dwg_'+a]) for a in 'xyz']+[1.]); target=np.array([float(row['rhino_'+a]) for a in 'xyz']);native=(np.array(t['dwg_to_rhino_native'])@d)[:3]
 n=float(np.linalg.norm(target-native));assert abs(n-float(row['norm_mm_hypothesis']))<1e-8
 # Independently recover native Rhino points. Holdout uses a denser 8193-point edge, not author's 2049.
 uid=row['rhino_reference'].split(' / ')[0];e=objects[uid].Geometry.Edges[17]
 if row['id']=='FIT-01':p=e.PointAtEnd;actual=np.array([p.X,p.Y,p.Z])
 elif row['id']=='HOLD-BOW-END':p=e.PointAtStart;actual=np.array([p.X,p.Y,p.Z])
 else:
  ps=[]
  for u in np.linspace(e.Domain.T0,e.Domain.T1,8193):
   p=e.PointAt(float(u));ps.append([p.X,p.Y,p.Z])
  ps=np.array(ps);ps=ps[np.argsort(ps[:,0])];actual=np.array([target[0],np.interp(target[0],ps[:,0],ps[:,1]),np.interp(target[0],ps[:,0],ps[:,2])])
 delta=float(np.linalg.norm(actual-target));assert delta<0.02
 res.append({'id':row['id'],'role':row['role'],'residual_recomputed_mm_hypothesis':n,'native_reference_delta_mm_at_8193_samples':delta})
r['anchors']=res
zones=list(csv.DictReader((P/'layout/zones.csv').open(),delimiter=';'));r['zones']=len(zones)
for option in 'AB':
 z=[x for x in zones if x['option']==option];assert sum(x['kind']=='cabin' for x in z)==4;assert sum(x['kind']=='wet' for x in z)==4
 assert all(x['status']=='PROPOSED_NOT_FIT_CHECKED' and x['height_status']=='OPEN' for x in z)
 byid={x['zone_id']:x for x in z};g=byid[option+'-GARAGE'];m=byid[option+'-MASTER']
 overlap=[max(0,min(float(g[a+'w_max_m']),float(m[a+'w_max_m']))-max(float(g[a+'w_min_m']),float(m[a+'w_min_m']))) for a in 'xy'];r[option+'_garage_master_rectangle_overlap_m']=overlap
 assert (overlap[0]*overlap[1]>0)==(option=='A')
cad=subprocess.run(['.local/cad-tools/dwg/venv/bin/python',str(P/'review/independent_dxf.py')],check=True,capture_output=True,text=True);r['dxf']=json.loads(cad.stdout)
(out/'results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
