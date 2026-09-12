"""Enable the reviewed local MCP add-on for this visible session only."""
import json
import addon_utils
import bpy

# Create the add-on's preference entry in memory without persisting factory defaults.
bpy.context.preferences.use_preferences_save = False
addon_utils.enable("blender_mcp", default_set=True, persistent=True)
preferences = bpy.context.preferences.addons["blender_mcp"].preferences
preferences.telemetry_consent = False
scene = bpy.context.scene
scene.blendermcp_port = 9876
for integration in ("polyhaven", "sketchfab", "polypizza", "hyper3d", "hunyuan3d"):
    setattr(scene, "blendermcp_use_" + integration, False)
server = getattr(bpy.types, "blendermcp_server", None)
if server is None or not server.running:
    bpy.ops.blendermcp.start_server()
print("WONDER_CHESS_MCP_READY " + json.dumps({
    "file": bpy.data.filepath,
    "blender": bpy.app.version_string,
    "objects": len(scene.objects),
    "port": scene.blendermcp_port,
    "telemetry_consent": preferences.telemetry_consent,
    "preferences_auto_save": bpy.context.preferences.use_preferences_save,
    "running": bpy.types.blendermcp_server.running,
}), flush=True)
