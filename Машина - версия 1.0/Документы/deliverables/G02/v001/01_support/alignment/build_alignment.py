"""Read-only G02 coordinate experiment. Run at repository root using Rhino venv.
Uses the already installed DWG venv in a subprocess; never writes source CAD.
All sections use cached Rhino render meshes, not exact Brep intersections.
"""
import argparse, csv, hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np
import rhino3dm as r
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

RHINO=Path('documentation/01-hull-and-geometry/3d/2-1.3dm')
DXF=Path('deliverables/G02/v001/01_support/cad/lines-oda-noaudit.dxf')
G01_DXF=Path('deliverables/G01/v001/01_support/dwg/lines-derived.dxf')
ROOT=Path('deliverables/G02/v001/01_support/alignment')
def xyz(p): return np.array([p.X,p.Y,p.Z],float)
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def curve(e,n=2049):
    return np.array([xyz(e.PointAt(t)) for t in np.linspace(e.Domain.T0,e.Domain.T1,n)])
def transform_matrix(offset):
    m=np.eye(4);m[:3,3]=offset;return m
def section(meshes,x):
    result=[]
    for vs,fs in meshes:
        for face in fs:
            tris=[face[:3]] if face[2]==face[3] else [face[:3],[face[0],face[2],face[3]]]
            for inds in tris:
                tri=vs[list(inds)]; ps=[]
                for i,j in [(0,1),(1,2),(2,0)]:
                    a,b=tri[i],tri[j]
                    if (a[0]<x<=b[0]) or (b[0]<x<=a[0]):
                        ps.append(a+(b-a)*(x-a[0])/(b[0]-a[0]))
                if len(ps)==2:result.append(np.array(ps))
    return result
def distance_to_segments(points,segs):
    a=np.array([s[0] for s in segs]);b=np.array([s[1] for s in segs]);ab=b-a
    out=[]
    for p in points:
        t=np.clip(((p-a)*ab).sum(1)/np.maximum((ab*ab).sum(1),1e-30),0,1)
        out.append(np.sqrt(((p-(a+t[:,None]*ab))**2).sum(1)).min())
    return np.array(out)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out-dir',type=Path,required=True);args=ap.parse_args();out=args.out_dir
    if out.exists() and any(out.iterdir()):ap.error('Use a new or empty output directory')
    out.mkdir(parents=True,exist_ok=True)
    extractor="""import ezdxf,json,sys
d=ezdxf.readfile(sys.argv[1]);rows=[]
for e in d.modelspace():
 if e.dxftype()=='POLYLINE' and e.is_3d_polyline:p=[list(v.dxf.location) for v in e.vertices]
 elif e.dxftype()=='LWPOLYLINE':p=[list(v) for v in e.vertices_in_wcs()]
 else:continue
 rows.append({'handle':e.dxf.handle,'layer':e.dxf.layer,'type':e.dxftype(),'points':p,'bulges':list(e.get_points('b')) if e.dxftype()=='LWPOLYLINE' else None})
print(json.dumps({'INSUNITS':d.header.get('$INSUNITS'),'curves':rows}))
"""
    raw=subprocess.check_output(['.local/cad-tools/dwg/venv/bin/python','-c',extractor,str(DXF)],text=True)
    dwg=json.loads(raw);ds={a['handle']:a for a in dwg['curves']}
    old=json.loads(subprocess.check_output(['.local/cad-tools/dwg/venv/bin/python','-c',extractor,str(G01_DXF)],text=True));olds={a['handle']:a for a in old['curves']}
    selected=['7A76','7A9D','506C','5472','5878','5C7E']
    crosscheck={h:float(np.abs(np.array(ds[h]['points'])-np.array(olds[h]['points'])).max()) for h in selected}
    dump(out/'dwg-selected-extraction.json',{'INSUNITS':dwg['INSUNITS'],'source':str(DXF),'comparison_with_G01_max_coordinate_difference':crosscheck,'curves':[ds[h] for h in selected]})
    model=r.File3dm.Read(str(RHINO));objects=list(model.Objects)
    reference=objects[234].Geometry;refends=[xyz(reference.PointAtStart),xyz(reference.PointAtEnd)]
    origin=max(refends,key=lambda p:p[0]);work_offset=-origin
    # Fixed axis permutation established from longitudinal, vertical and symmetry directions.
    perm=np.array([[0,0,1],[1,0,0],[0,1,0]],float)
    # ONLY training landmark: aft negative-side sheer/transom junction.
    rp=xyz(objects[133].Geometry.Edges[17].PointAtEnd)
    dp=np.array(ds['7A9D']['points'][-1]);offset=rp-perm@dp
    # Do not force a one-sided transverse point to define centreline: use Rhino datum plane.
    offset[1]=origin[1]
    matrix=np.eye(4);matrix[:3,:3]=perm;matrix[:3,3]=offset
    work=transform_matrix(work_offset)
    curves={};meshes=[]
    groups={'shell':[133,144],'deck':[478],'roof':[198,333,334,335,336],'local_vertical':[338,339,340,343,344]}
    for group,ids in groups.items():
        curves[group]=[]
        for idx in ids:
            obj=objects[idx]
            for n,e in enumerate(obj.Geometry.Edges):
                ps=curve(e,257)+work_offset
                curves[group].append({'object_index':idx,'object_id':str(obj.Attributes.Id),'edge_index':n,'points_mm':ps.tolist()})
            if group=='shell':
                for f in obj.Geometry.Faces:
                    mesh=f.GetMesh(r.MeshType.Render)
                    meshes.append((np.array([xyz(v) for v in mesh.Vertices])+work_offset,list(mesh.Faces)))
    dump(out/'curves-working.json',{'status':'CONCEPTUAL_HISTORICAL_GEOMETRY','units':'mm','native_to_working':work.tolist(),'working_to_native':np.linalg.inv(work).tolist(),'origin_native_mm':origin.tolist(),'meaning':'X forward; Y transverse with centreline 0; Z upward relative to geometric line #234, not actual waterline. X=0 is forward endpoint of #234, not the stem.','groups':curves})
    rows=[]
    def add(key,role,handle,method,dpoint,rpoint,source_ref):
        prediction=perm@dpoint+offset;error=rpoint-prediction
        rows.append({'id':key,'role':role,'dwg_handle':handle,'rhino_reference':source_ref,'method':method,'dwg_x':dpoint[0],'dwg_y':dpoint[1],'dwg_z':dpoint[2],'rhino_x':rpoint[0],'rhino_y':rpoint[1],'rhino_z':rpoint[2],'residual_x_mm_hypothesis':error[0],'residual_y_mm_hypothesis':error[1],'residual_z_mm_hypothesis':error[2],'norm_mm_hypothesis':float(np.linalg.norm(error))})
    add('FIT-01','FIT_X_Z_ONLY','7A9D','aft sheer/transom junction; transverse constrained to geometric centreline',dp,rp,'47cc8bdb-89af-4af9-9312-275b5b3d047c / edge17.end')
    # Holdout longitudinal stations were not used for the translation.
    for j,(handle,idx) in enumerate([('7A76',144),('7A9D',133)]):
        ec=curve(objects[idx].Geometry.Edges[17]);ec=ec[np.argsort(ec[:,0])]
        for k,station in enumerate([-4250.,-8250.,-12250.,-16250.]):
            poly=np.array(ds[handle]['points']);poly=poly[np.argsort(poly[:,2])]
            if not(poly[0,2]<=station<=poly[-1,2]):continue
            p=np.array([np.interp(station,poly[:,2],poly[:,0]),np.interp(station,poly[:,2],poly[:,1]),station])
            targetx=station+offset[0]
            q=np.array([targetx,np.interp(targetx,ec[:,0],ec[:,1]),np.interp(targetx,ec[:,0],ec[:,2])])
            add(f'HOLD-SHEER-{j}-{k}','HOLDOUT_SECTION','7A76' if idx==144 else '7A9D','same longitudinal plane; linear interpolation of DWG vertices and 2049-point Rhino edge17',p,q,str(objects[idx].Attributes.Id)+' / edge17')
    # Forward endpoints are a mismatch test, not a fit landmark.
    add('HOLD-BOW-END','HOLDOUT_ENDPOINT','7A76','forward endpoints of candidate sheer curves; homologous identity NOT established',np.array(ds['7A76']['points'][0]),xyz(objects[144].Geometry.Edges[17].PointAtStart),'190edc86-b6f9-43b0-8e00-276eaca1a3ee / edge17.start')
    with (out/'anchors.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    stats=[];fig,axs=plt.subplots(2,2,figsize=(13,10),layout='constrained')
    sections=[]
    for ax,h in zip(axs.flat,['506C','5472','5878','5C7E']):
        p=np.array(ds[h]['points']);wp=p@perm.T+offset+work_offset;x=float(wp[0,0]);seg=section(meshes,x)
        # LWPOLYLINE vertices only, with explicit bulge check: no hidden approximation to arcs.
        assert all(abs(b[0])<1e-12 for b in ds[h]['bulges'])
        dd=distance_to_segments(wp[:,1:], [s[:,1:] for s in seg])
        stats.append({'handle':h,'layer':ds[h]['layer'],'role':'HOLDOUT_DIAGNOSTIC_DIFFERENT_FEATURE_CLASSES','dwg_longitudinal_native':float(p[0,2]),'working_x_mm':x,'vertex_count':len(p),'median_vertex_to_mesh_section_mm_hypothesis':float(np.median(dd)),'p95_mm_hypothesis':float(np.percentile(dd,95)),'max_mm_hypothesis':float(dd.max()),'note':'Frame-pattern vertices versus outer-shell cached mesh section; not identical features; no fit/no acceptance tolerance; possible plate offsets/cut-outs and mesh error.'})
        ax.add_collection(LineCollection([s[:,1:] for s in seg],colors='#1262a3',linewidths=1.2,label='Rhino cached shell mesh section'))
        ax.plot(wp[:,1],wp[:,2],color='#d55e00',linewidth=1,label=f'DWG #{h} frame-pattern vertices')
        ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('Y working [mm]');ax.set_ylabel('Z working [mm]');ax.set_title(f'DWG layer {ds[h]["layer"]}; Xw={x:.1f} mm');ax.legend(fontsize=7)
        sections.append({'dwg_handle':h,'working_x_mm':x,'rhino_mesh_segments_mm':[s.tolist() for s in seg],'dwg_vertices_working_mm':wp.tolist()})
    fig.suptitle('G02 holdout sections | mm-per-DWG-unit hypothesis | frame != shell | NOT FOR CONSTRUCTION')
    fig.savefig(out/'holdout-sections.png',dpi=140);fig.savefig(out/'holdout-sections.svg');plt.close(fig)
    dump(out/'sections-working.json',sections);dump(out/'section-diagnostics.json',stats)
    fig,axs=plt.subplots(3,1,figsize=(15,12),layout='constrained')
    for ax,(a,b) in zip(axs,[(0,1),(0,2),(1,2)]):
        ax.add_collection(LineCollection([np.array(c['points_mm'])[:,[a,b]] for c in curves['shell']],colors='#1262a3',linewidths=.65,label='Rhino shell native edges'))
        for h in ['7A76','7A9D']:
            wp=np.array(ds[h]['points'])@perm.T+offset+work_offset
            ax.plot(wp[:,a],wp[:,b],color='#d55e00',lw=1,label='DWG candidate sheer #'+h)
        ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('XYZ'[a]+' working [mm]');ax.set_ylabel('XYZ'[b]+' working [mm]');ax.legend(fontsize=8)
    fig.suptitle('G02 measured curve overlay | fixed axis permutation + constrained translation | identity NOT established')
    fig.savefig(out/'alignment-overlay.png',dpi=140);fig.savefig(out/'alignment-overlay.svg');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,(a,b) in zip(axs,[(0,1),(0,2)]):
        for c in curves['shell']:
            ps=np.array(c['points_mm']);mask=ps[:,0]>-700
            if mask.sum()>1:ax.plot(ps[mask,a],ps[mask,b],color='#1262a3',lw=1)
        ps=np.array(ds['7A76']['points'])@perm.T+offset+work_offset;mask=ps[:,0]>-700
        ax.plot(ps[mask,a],ps[mask,b],'-o',markersize=3,color='#d55e00',label='DWG #7A76 vertex chords')
        pp=np.array([rows[-1]['rhino_x'],rows[-1]['rhino_y'],rows[-1]['rhino_z']])+work_offset
        qp=perm@np.array(ds['7A76']['points'][0])+offset+work_offset
        ax.plot([pp[a],qp[a]],[pp[b],qp[b]],'k--',label='Endpoint difference (not proven homologous)')
        ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('XYZ'[a]+' working [mm]');ax.set_ylabel('XYZ'[b]+' working [mm]');ax.legend(fontsize=7)
    fig.suptitle('Bow discrepancy retained | no warp / no endpoint fit | geometry only')
    fig.savefig(out/'bow-detail.png',dpi=140);fig.savefig(out/'bow-detail.svg');plt.close(fig)
    dwgsource=next(Path('documentation').rglob('*.dwg'),None) or next(Path('documentation').rglob('*.DWG'))
    result={'status':'PROVISIONAL_ALIGNMENT_NOT_IDENTITY_NOT_AS_BUILT','method':'Fixed axis permutation; scale fixed at hypothesis 1 mm/DWG unit; translation X/Z from one aft sheer junction; transverse offset from Rhino datum symmetry. No least-squares/nearest-neighbour fitting.','unit_status':{'Rhino':'file declares millimetres','DWG_INSUNITS':dwg['INSUNITS'],'DWG_scale_mm_per_unit':1.0,'scale_status':'GEOMETRICALLY_PLAUSIBLE_UNCONFIRMED'},'dwg_to_rhino_native':matrix.tolist(),'rhino_native_to_dwg':np.linalg.inv(matrix).tolist(),'rhino_native_to_working':work.tolist(),'working_to_rhino_native':np.linalg.inv(work).tolist(),'dwg_to_working':(work@matrix).tolist(),'working_to_dwg':np.linalg.inv(work@matrix).tolist(),'origin_rhino_object_id':str(objects[234].Attributes.Id),'origin_definition':'larger-X endpoint of PolyCurve #234. Working plane z=0 is a drawing datum near CWL1250 text, not physical/design approved waterline.','fit_rows':1,'holdout_rows':len(rows)-1,'holdout_section_diagnostics':4,'independence_limit':'Holdouts excluded from fitting; sheer points share one source curve and are correlated. Four frame-pattern entities are separate source entities but same historical drawing; they are not independent surveys or exact homologous hull features.','inputs_sha256':{str(p):sha(p) for p in [RHINO,dwgsource,DXF,G01_DXF]},'limits':['Selected entities now read from independent ODA DXF; whole-file CAD acceptance belongs to CAD agent, not this alignment','Render mesh tessellation accuracy unknown; section metrics diagnostic only','No physical survey; no revision identity or production dimensions established','No scale optimisation, anisotropic rescaling, or bow warp applied']}
    dump(out/'transform.json',result)
    print(json.dumps({'offset':offset.tolist(),'working_offset':work_offset.tolist(),'anchor_rows':rows,'sections':stats},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
