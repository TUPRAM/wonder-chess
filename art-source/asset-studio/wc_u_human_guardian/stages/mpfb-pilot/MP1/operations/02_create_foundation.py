import bpy,json
s=bpy.context.scene
assert s.name=='MP1_ADA_HEAD'
s.MPFB_NH_phenotype_gender='female';s.MPFB_NH_phenotype_age='young';s.MPFB_NH_phenotype_race='universal';s.MPFB_NH_phenotype_influence=1.0;s.MPFB_NH_add_phenotype=True;s.MPFB_NH_scale_factor='METER';s.MPFB_NH_mask_helpers=True;s.MPFB_NH_extra_vertex_groups=True
print(bpy.ops.mpfb.create_human())
o=bpy.context.object;o.name='MP1_MpfbFoundation_Source';o['provenance']='MPFB 2.0.17 core CC0 mesh and targets; fresh generated source for Ada trial';o['human_approval']=False
print(json.dumps({'object':o.name,'scale':list(o.scale),'location':list(o.location),'dimensions':list(o.dimensions),'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'keys':list(o.data.shape_keys.key_blocks.keys()) if o.data.shape_keys else [],'groups':[g.name for g in o.vertex_groups],'modifiers':[(m.name,m.type) for m in o.modifiers],'bounds':[list(v) for v in o.bound_box]},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
