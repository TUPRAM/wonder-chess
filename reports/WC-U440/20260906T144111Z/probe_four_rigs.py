import sys,json
from pathlib import Path
import bpy
ROOT=Path('C:/Users/iputu/Documents/Wonder Chess');sys.path.insert(0,str(ROOT/'tools/blender'));import author_update_four as a
units=json.loads((ROOT/'data/units.json').read_text())['units'];a.export_normalized_copy=lambda *args:None;records=[]
for uid in ('wc_u_human_warrior','wc_u_elf_mage','wc_u_dwarf_priest','wc_u_orc_guardian'):
    bpy.ops.wm.read_factory_settings(use_empty=True);u=next(x for x in units if x['id']==uid);arm,p=a.rig_for(u)
    try:clips,reach=a.bake_actions(u,arm,ROOT);record={'unit':uid,'reach':reach,'status':'RIG_POSE_PROBE_ONLY_PASS'}
    except Exception as e:record={'unit':uid,'status':'FAIL','error':str(e)}
    records.append(record);print('PROBE '+json.dumps(record),flush=True)
(ROOT/'reports/WC-U440/20260906T144111Z/rig-pose-probe.json').write_text(json.dumps(records,indent=2))
