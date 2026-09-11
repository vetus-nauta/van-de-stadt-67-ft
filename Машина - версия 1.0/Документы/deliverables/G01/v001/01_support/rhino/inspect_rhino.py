"""Read-only 3dm inventory and sampled native-coordinate projections; no CAD edits.
Run from repo root with Python, rhino3dm==8.32.1, matplotlib==3.11.1.
Bounds of cached meshes / sampled edges are descriptive, not certified dimensions.
"""
import argparse, csv, hashlib, json, collections, importlib.metadata
from pathlib import Path
import rhino3dm as r
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

SOURCE=Path('documentation/01-hull-and-geometry/3d/2-1.3dm')
def point(p): return [p.X,p.Y,p.Z]
def bbox(b): return {'min':point(b.Min),'max':point(b.Max)} if b.IsValid else None
def bounds(p):
    a=np.asarray(p)
    return {'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()} if len(a) else None
def curve(c):
    d=c.Domain
    return [point(c.PointAt(t)) for t in np.linspace(d.T0,d.T1,129)]
def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,required=True,help='New or empty directory for generated inspection artifacts')
    args=parser.parse_args()
    OUT=args.out_dir
    if OUT.exists() and any(OUT.iterdir()):
        parser.error('Output directory must be new or empty; existing artifacts are never overwritten')
    OUT.mkdir(parents=True,exist_ok=True)
    m=r.File3dm.Read(str(SOURCE)); assert m is not None
    layers=[{'index':l.Index,'id':str(l.Id),'name':l.Name,'visible':l.Visible} for l in m.Layers]
    rows=[]; segments=[]; samples=[]
    for i,o in enumerate(m.Objects):
        g=o.Geometry;a=o.Attributes; ps=[];segs=[];mp=[]
        row={'index':i,'id':str(a.Id),'layer_index':a.LayerIndex,'layer':m.Layers[a.LayerIndex].Name,'name':a.Name,'type':type(g).__name__,'valid':g.IsValid,'visible':a.Visible,'mode':str(a.Mode),'bbox_api':bbox(g.GetBoundingBox()),'bbox_tight_api':bbox(g.GetTightBoundingBox())}
        if isinstance(g,r.Brep):
            row.update(faces=len(g.Faces),edges=len(g.Edges),vertices=len(g.Vertices),solid=g.IsSolid,manifold=g.IsManifold)
            row['cached_render_faces']=0
            for f in g.Faces:
                mesh=f.GetMesh(r.MeshType.Render)
                if mesh:
                    row['cached_render_faces']+=1
                    mp.extend(point(v) for v in mesh.Vertices)
            segs=[curve(e) for e in g.Edges]
        elif isinstance(g,r.Curve): segs=[curve(g)]
        elif isinstance(g,r.Point): ps=[point(g.Location)]
        elif isinstance(g,r.Text): row.update(text=g.PlainText,text_origin=point(g.Plane.Origin))
        for s in segs: ps.extend(s)
        row['sample_bounds']=bounds(ps);row['cached_mesh_bounds']=bounds(mp)
        for key in ['bbox_api','bbox_tight_api','sample_bounds','cached_mesh_bounds']:
            row[key+'_status']='AVAILABLE' if row[key] is not None else 'NOT_AVAILABLE_OR_NOT_APPLICABLE'
        row['sample_count']=len(ps);row['cached_mesh_vertices']=len(mp)
        rows.append(row);segments.append(segs);samples.append(ps)
    settings={k:str(getattr(m.Settings,k)) for k in ['ModelUnitSystem','ModelAbsoluteTolerance','ModelRelativeTolerance','ModelAngleToleranceDegrees','ModelBasePoint','PageUnitSystem']}
    summary={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'archive_version':m.ArchiveVersion,'rhino3dm_version':r.__version__,'rhino3dm_distribution_version':importlib.metadata.version('rhino3dm'),'matplotlib_version':matplotlib.__version__,'settings':settings,'object_count':len(rows),'types':dict(collections.Counter(x['type'] for x in rows)),'layers':layers,'object_table_bbox':bbox(m.Objects.GetBoundingBox()),'valid_count':sum(x['valid'] for x in rows),'solid_brep_count':sum(x.get('solid',False) for x in rows),'sample_definition':'129 equally spaced parameter values per native edge/curve; not arc-length; mesh vertices unchanged; all coordinates native mm','objects':rows}
    (OUT/'inventory.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    fields=['index','id','layer','name','type','valid','visible','faces','edges','solid','cached_render_faces','cached_mesh_vertices','sample_bounds','cached_mesh_bounds','bbox_api','bbox_tight_api','text','text_origin']
    with (OUT/'objects.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    selections={'shell-surfaces':[133,144],'deck-candidate':[478],'roof-candidates':[198,333,334,335,336],'internal-surfaces-example':[338,339,340,343,344]}
    selected={key:{'indices':ids,'object_ids':[rows[i]['id'] for i in ids],'sample_bounds':bounds([p for i in ids for p in samples[i]]),'method':'visual grouping of native sampled edges; no semantic CAD assembly; not an approved naval component classification'} for key,ids in selections.items()}
    (OUT/'selections.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    for name,idxs in [('all',range(len(rows))),('hull-layer',[i for i,x in enumerate(rows) if x['layer']=='HULL']),*selections.items()]:
        fig,axs=plt.subplots(3,1,figsize=(14,14),layout='constrained')
        for ax,(a,b,label) in zip(axs,[(0,1,'XY'),(0,2,'XZ'),(1,2,'YZ')]):
            for layer,color in [('HULL','#225ea8'),('MD_RAILS','#d95f0e')]:
                lines=[np.array(s)[:,[a,b]] for i in idxs if rows[i]['layer']==layer for s in segments[i]]
                if lines: ax.add_collection(LineCollection(lines,colors=color,linewidths=.4,label=layer))
            ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('XYZ'[a]+' [mm]');ax.set_ylabel('XYZ'[b]+' [mm]');ax.set_title(label+' — sampled native Brep edges / curves');ax.legend(loc='upper right')
        fig.suptitle('2-1.3dm | '+name+' | Native coordinates, no transforms; not construction drawings')
        fig.savefig(OUT/(name+'-projections.png'),dpi=120);fig.savefig(OUT/(name+'-projections.svg'));plt.close(fig)
    print(json.dumps({k:v for k,v in summary.items() if k!='objects'},ensure_ascii=False,indent=2))
if __name__=='__main__': run()
