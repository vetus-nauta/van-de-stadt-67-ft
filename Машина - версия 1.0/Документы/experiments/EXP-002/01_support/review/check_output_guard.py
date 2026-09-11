"""Independent negative tests: never attempt to write an existing release directory."""
from pathlib import Path
import subprocess,hashlib,json
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
MODEL=ROOT/'experiments/EXP-002/01_support/model'
def snapshot():return {str(p.relative_to(MODEL)):hashlib.sha256(p.read_bytes()).hexdigest() for p in MODEL.rglob('*') if p.is_file()}
before=snapshot();cases=[]
for name,extra,marker in [('missing-output',[],'required'),('existing-release',['--','--out-dir',str(MODEL)],'Output must')]:
 r=subprocess.run(['blender','-b','-t','2','--python',str(MODEL/'build_model.py')]+extra,capture_output=True,text=True,timeout=30)
 log=r.stdout+r.stderr;(OUT/(name+'.log')).write_text(log)
 assert r.returncode!=0 and marker in log,log
 assert 'Read blend:' not in log,log
 cases.append({'case':name,'exit_code':r.returncode,'refused_before_scene_read':True})
assert snapshot()==before
(OUT/'guard-check.json').write_text(json.dumps({'status':'PASS','cases':cases,'model_files_unchanged':True},indent=2)+'\n')
print('PASS output guard and file preservation')
