"""Save a copy of the user's loaded Ada scene through the configured safe MCP."""
import asyncio,hashlib,json,os,tomllib
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    root=Path(__file__).resolve().parents[2]
    cfg=tomllib.loads((root/'.codex/config.toml').read_text())['mcp_servers']['blender']
    out=root/'art-source/heroes/wc_u_human_guardian/candidates/AQ1/before_live_scene.blend'
    assert not out.exists()
    report=root/'reports/AQ1/20260908/live_snapshot.json'
    assert not report.exists()
    canonical=root/'art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend'
    before=hashlib.sha256(canonical.read_bytes()).hexdigest()
    code='import bpy\nimport json\nold_path=bpy.data.filepath\n'
    code+='stats=[]\nfor o in bpy.context.scene.objects:\n if o.type == "MESH":\n  o.data.calc_loop_triangles()\n  stats.append({"name":o.name,"vertices":len(o.data.vertices),"triangles":len(o.data.loop_triangles),"materials":[m.name for m in o.data.materials if m]})\n'
    code+=f'bpy.ops.wm.save_as_mainfile(filepath={str(out)!r},copy=True)\n'
    code+='print(json.dumps({"loaded_path_before":old_path,"loaded_path_after":bpy.data.filepath,"meshes":stats,"copy_saved":True}))\n'
    params=StdioServerParameters(command=cfg['command'],args=cfg['args'],cwd=cfg.get('cwd',str(root)),env={**os.environ,**cfg['env']})
    async with stdio_client(params) as streams:
        async with ClientSession(*streams) as s:
            await s.initialize()
            result=await s.call_tool('execute_blender_code',{'code':code,'user_prompt':'AQ1 Phase A: preserve a before-copy of the actual loaded Ada scene without changing canonical source.'})
    record=result.model_dump(mode='json')
    record['canonical_sha256_before']=before;record['canonical_sha256_after']=hashlib.sha256(canonical.read_bytes()).hexdigest()
    record['copy_exists']=out.exists();record['copy_sha256']=hashlib.sha256(out.read_bytes()).hexdigest() if out.exists() else None
    report.write_text(json.dumps(record,indent=2),encoding='utf-8');print(report)
    if result.isError or not out.exists() or record['canonical_sha256_after']!=before:raise RuntimeError('Live snapshot did not verify; see retained report')

if __name__=='__main__':asyncio.run(asyncio.wait_for(main(),timeout=90))
