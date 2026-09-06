"""Export the actual authored arrangement for the Unreal integrator to instance."""
import bpy
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
collection=bpy.data.collections.get('WC_COURTYARD')
if collection is None:raise RuntimeError('Expected authored courtyard collection')
records=[]
for ob in collection.objects:
    if ob.type!='MESH':continue
    records.append({'module':ob.data.name,'instance':ob.name,'location_m':list(ob.location),
                    'rotation_euler_radians':list(ob.rotation_euler),'scale':list(ob.scale)})
out=root/'exports/arena/courtyard_layout.json'
out.write_text(json.dumps({'source':'WC_SevenLanternCourtyard.blend','source_units':'meters','source_forward':'+Y','source_up':'+Z',
                          'requires_measured_unreal_basis_conversion':True,'instances':records},indent=2)+'\n')
print('WC_LAYOUT_INSTANCES',len(records))
