"""Read-only live MCP handshake/scene/viewport check using project configuration."""
import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path
import tomllib
from datetime import datetime, timezone

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    root = Path(__file__).resolve().parents[2]
    config = tomllib.loads((root / '.codex/config.toml').read_text())['mcp_servers']['blender']
    folder = root / 'reports/blender-mcp' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder.mkdir(parents=True)
    source = root / 'art-source/heroes/wc_u_human_guardian/wc_u_human_guardian.blend'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    results = {'started_utc': datetime.now(timezone.utc).isoformat(), 'source_sha256_before': before}
    params = StdioServerParameters(command=config['command'], args=config['args'],
                                  cwd=config.get('cwd', str(root)), env={**os.environ, **config['env']})
    with (folder / 'server.log').open('w', encoding='utf-8') as log:
        async with stdio_client(params, errlog=log) as streams:
            async with ClientSession(*streams) as session:
                results['initialize'] = (await session.initialize()).model_dump(mode='json')
                listing = await session.list_tools()
                results['advertised_tools'] = [tool.name for tool in listing.tools]
                results['codex_enabled_tools'] = config['enabled_tools']
                results['tool_schemas'] = {tool.name: tool.inputSchema for tool in listing.tools if tool.name in config['enabled_tools']}
                for name, arguments in [
                    ('get_addon_status', {}),
                    ('get_scene_info', {}),
                    ('get_object_info', {'object_name': 'SK_wc_u_human_guardian'}),
                    ('execute_blender_code', {'code': 'import bpy\nimport json\nprint(json.dumps({"file": bpy.data.filepath, "version": bpy.app.version_string, "objects": len(bpy.context.scene.objects), "meshes": [o.name for o in bpy.context.scene.objects if o.type == "MESH"], "actions": [a.name for a in bpy.data.actions]}))'}),
                    ('get_viewport_screenshot', {'max_size': 1400}),
                ]:
                    arguments['user_prompt'] = 'lets conect this repo to blender using blender mcp'
                    result = await session.call_tool(name, arguments)
                    saved = result.model_dump(mode='json')
                    for block in saved.get('content', []):
                        if block['type'] == 'image':
                            path = folder / 'viewport.png'
                            path.write_bytes(base64.b64decode(block.pop('data')))
                            block['saved_path'] = str(path)
                    results[name] = saved
                    print(name, 'MCP_ERROR' if result.isError else 'returned', flush=True)
    results['source_sha256_after'] = hashlib.sha256(source.read_bytes()).hexdigest()
    results['source_unchanged'] = before == results['source_sha256_after']
    failures = []
    for name in config['enabled_tools']:
        result = results[name]
        texts = [block['text'] for block in result.get('content', []) if block['type'] == 'text']
        if result.get('isError') or any(text.lower().startswith(('error', 'failed', 'could not')) for text in texts):
            failures.append(name)
    if not results['source_unchanged']:
        failures.append('source_file_changed')
    status = json.loads(results['get_addon_status']['content'][0]['text'])
    if not status['up_to_date'] or status['telemetry_consent'] is not False:
        failures.append('protocol_or_telemetry')
    results['failures'] = failures
    results['passed'] = not failures
    (folder / 'verification.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(folder, flush=True)
    if failures:
        raise SystemExit('MCP verification failed: ' + ', '.join(failures))


if __name__ == '__main__':
    asyncio.run(asyncio.wait_for(main(), timeout=120))
