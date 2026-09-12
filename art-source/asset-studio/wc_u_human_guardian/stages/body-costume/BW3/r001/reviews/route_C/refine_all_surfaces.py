from pathlib import Path
script=Path(__file__).parent/'audit_route_C.py'
exec(compile(script.read_text().split('started = time.perf_counter()')[0],str(script),'exec'),globals())
path=OUT/'route_C_results.json';report=json.loads(path.read_text())
assert report['status']=='COMPLETE_READ_ONLY_GEOMETRY_SCREEN'
(OUT/'route_C_results_before_matched_refinement.json').write_text(json.dumps(report,indent=2))
frames=sorted({row['frame'] for v in report['variants'] for row in v['quarter_frames']})
added=0
for variant in report['variants']:
    obj=bpy.data.objects[variant['object']];raw=variant['surface']=='raw_posed_cage'
    done={row['frame'] for row in variant['quarter_frames']}
    for frame in frames:
        if frame not in done:
            variant['quarter_frames'].append(measure(obj,frame,raw));added+=1
    variant['quarter_frames'].sort(key=lambda row:row['frame'])
report['matched_adaptive_refinement']={'frames':frames,'added_surface_states':added,'reason':'Cross-check every surface at the union of detected body raw/evaluated onset subframes. Existing preceding/first onset records remain valid.'}
report['source_sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert report['source_sha256_after']==EXPECTED
path.write_text(json.dumps(report,indent=2));print('COMPLETE_ADDITIONAL_STATES',added,flush=True)
