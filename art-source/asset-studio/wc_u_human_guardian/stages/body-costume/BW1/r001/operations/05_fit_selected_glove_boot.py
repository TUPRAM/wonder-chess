import bpy,json
s=bpy.data.scenes['BW1_BODY_COSTUME'];body=bpy.data.objects['BW1_IndexedBody'];before=set(bpy.data.objects.keys())
s.MPFB_LC_object_type='Clothes';s.MPFB_ASLS_fit_to_body=True;s.MPFB_ASLS_set_up_rigging=True;s.MPFB_ASLS_interpolate_weights=True;s.MPFB_ASLS_import_subrig=False;s.MPFB_ASLS_import_weights=False;s.MPFB_ASLS_add_subdiv_modifier=True;s.MPFB_ASLS_subdiv_levels=1;s.MPFB_ASLS_makeclothes_metadata=False;s.MPFB_ASLS_delete_group=False;s.MPFB_ASLS_mask_base_mesh=False
for folder in ['toigo_gloves_short','toigo_ankle_boots_male']:
    for o in s.objects:o.select_set(False)
    body.select_set(True);bpy.context.view_layer.objects.active=body
    print(folder,bpy.ops.mpfb.load_clothes(filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/source-quarantine/selected/clothes/'+folder+'/'+folder+'.mhclo'))
new=[o for o in s.objects if o.name not in before]
for o in new:
    if o.type=='MESH':
        old=o.name;o.name='BW1_Glove_Pair_SourceFit' if 'glove' in old.lower() else 'BW1_Boot_Pair_SourceFit'
        for c in list(o.users_collection):c.objects.unlink(o)
        bpy.data.collections['BW1_CLOTH'].objects.link(o);o['source_asset']=old;o['construction']='Adapted CC0 MRT garment using native MHCLO source correspondence';o['approval']='CANDIDATE'
        o.data.materials.clear();o.data.materials.append(bpy.data.materials['BW1_Uniform_Clay'])
        for f in o.data.polygons:f.material_index=0
for m in body.modifiers:
    if m.type=='MASK' and m.name.startswith('Delete.'):m.show_viewport=False;m.show_render=False
states=[(m,m.show_viewport) for m in body.modifiers]
for m,_ in states:m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get();dg.update();ev=body.evaluated_get(dg)
groups={}
for name in ['helper-tights','helper-skirt','body']:
    i=body.vertex_groups[name].index;ids={v.index for v in body.data.vertices if any(g.group==i and g.weight>.5 for g in v.groups)};coords=[body.matrix_world@ev.data.vertices[j].co for j in ids];groups[name]={'vertices':len(ids),'faces':sum(all(v in ids for v in f.vertices) for f in body.data.polygons),'bounds':[[min(v[k] for v in coords),max(v[k] for v in coords)] for k in range(3)]}
for m,state in states:m.show_viewport=state
print(json.dumps({'imported':[(o.name,len(o.data.vertices),len(o.data.polygons),o.parent.name if o.parent else None,[(m.name,m.type) for m in o.modifiers]) for o in new if o.type=='MESH'],'helpers':groups},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
s.camera=bpy.data.objects['BW1_Camera_three_quarter'];s.render.filepath='C:/Users/iputu/Documents/Wonder Chess/art-source/asset-studio/wc_u_human_guardian/stages/body-costume/BW1/r001/captures/sourcefit_body_gloves_boots.png';bpy.ops.render.render(write_still=True)

