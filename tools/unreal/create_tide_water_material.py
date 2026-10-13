"""Build the Tide Caller's living-water material and assign it to the rigged mesh.

The painted water texture is kept, but its lookup is pushed around by two fields of noise that drift through the body
(one rising, one circling), so the painted swirls flow instead of sitting still. Bright bands of light travel up the
body on top. The noise is laid out in the body's own rest-pose space, so it stays attached when the body bends.
Writes reports/creature-production/wc_vn_tide_caller/blender_rig_r001/water-material.json.
"""
import json
import traceback
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
report = {"status": "STARTED"}
folder = "/Game/WonderChess/VNext/Heroes/TideCaller_r002"
try:
    lib = unreal.MaterialEditingLibrary
    source = "/Game/WonderChess/VNext/Heroes/TideCaller_r001/model_urls_glb/Textures"
    colour_map = unreal.EditorAssetLibrary.load_asset(f"{source}/Image_0")
    normal_map = unreal.EditorAssetLibrary.load_asset(f"{source}/normal")
    if colour_map is None:
        raise RuntimeError("The painted water texture is missing")
    path = f"{folder}/M_TideWater"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        material = unreal.EditorAssetLibrary.load_asset(path)
        lib.delete_all_material_expressions(material)
    else:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_TideWater", folder, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("used_with_skeletal_mesh", True)
    spot = [0]

    def node(kind, **properties):
        spot[0] += 1
        made = lib.create_material_expression(material, kind, -1800 + (spot[0] % 8) * 220, (spot[0] // 8) * 220)
        for key, value in properties.items():
            made.set_editor_property(key, value)
        return made

    def join(a, b, pin, out=""):
        if not lib.connect_material_expressions(a, out, b, pin) and not lib.connect_material_expressions(a, out, b, ""):
            raise RuntimeError(f"Could not connect {a.get_name()} to {b.get_name()}.{pin}")

    def op(kind, a, b=None, **properties):
        made = node(kind, **properties)
        join(a, made, "A" if b is not None or kind in (unreal.MaterialExpressionMultiply, unreal.MaterialExpressionAdd) else "")
        if b is not None:
            join(b, made, "B")
        return made

    def vector(x, y, z):
        return node(unreal.MaterialExpressionConstant3Vector, constant=unreal.LinearColor(x, y, z, 0))

    def noise(position):
        made = node(unreal.MaterialExpressionNoise, scale=1.0, levels=2, output_min=-1.0, output_max=1.0, turbulence=False,
                    noise_function=unreal.NoiseFunction.NOISEFUNCTION_GRADIENT_TEX3D)
        join(position, made, "Position")
        return made

    time = node(unreal.MaterialExpressionTime)
    place = node(unreal.MaterialExpressionPreSkinnedPosition)
    # Two drifting fields: one sinks slowly so the pattern appears to rise, one slides round the body.
    rising = op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionMultiply, place, vector(0.022, 0.022, 0.022)), op(unreal.MaterialExpressionMultiply, time, vector(0.05, 0.0, -0.32)))
    circling = op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionMultiply, place, vector(0.034, 0.034, 0.016)), op(unreal.MaterialExpressionMultiply, time, vector(0.24, -0.20, 0.06)))
    first, second = noise(rising), noise(circling)
    push = node(unreal.MaterialExpressionAppendVector)
    join(first, push, "A")
    join(second, push, "B")
    swirl = op(unreal.MaterialExpressionAdd, node(unreal.MaterialExpressionTextureCoordinate), op(unreal.MaterialExpressionMultiply, push, node(unreal.MaterialExpressionConstant, r=0.028)))
    colour = node(unreal.MaterialExpressionTextureSample, texture=colour_map)
    join(swirl, colour, "UVs")
    # Bands of light that travel up the body, bent by the same noise so they wander like caustics.
    height = node(unreal.MaterialExpressionComponentMask, r=False, g=False, b=True, a=False)
    join(place, height, "")
    phase = op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionMultiply, height, node(unreal.MaterialExpressionConstant, r=0.075)),
                                                op(unreal.MaterialExpressionMultiply, first, node(unreal.MaterialExpressionConstant, r=2.4))),
               op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionMultiply, second, node(unreal.MaterialExpressionConstant, r=1.6)),
                  op(unreal.MaterialExpressionMultiply, time, node(unreal.MaterialExpressionConstant, r=-2.2))))
    wave = node(unreal.MaterialExpressionSine)
    join(phase, wave, "")
    crest = node(unreal.MaterialExpressionSaturate)
    join(wave, crest, "")
    bands = node(unreal.MaterialExpressionPower, const_exponent=5.0)
    join(crest, bands, "Base")
    light = op(unreal.MaterialExpressionMultiply, bands, vector(0.35, 0.85, 1.25))
    body_glow = op(unreal.MaterialExpressionMultiply, colour, node(unreal.MaterialExpressionConstant, r=0.35))
    glow = op(unreal.MaterialExpressionAdd, body_glow, light)
    # The surface itself moves: every vertex is pushed in and out along its normal by the drifting noise, and a slow
    # wave rolls up the body. The base and the foam crests heave most; the head and hands stay nearly still.
    normal = node(unreal.MaterialExpressionVertexNormalWS)
    ripple = op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionMultiply, first, node(unreal.MaterialExpressionConstant, r=1.7)),
                op(unreal.MaterialExpressionMultiply, second, node(unreal.MaterialExpressionConstant, r=1.2)))
    roll_phase = op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionMultiply, height, node(unreal.MaterialExpressionConstant, r=0.09)),
                    op(unreal.MaterialExpressionMultiply, time, node(unreal.MaterialExpressionConstant, r=-3.0)))
    roll = node(unreal.MaterialExpressionSine)
    join(roll_phase, roll, "")
    heave = op(unreal.MaterialExpressionAdd, ripple, op(unreal.MaterialExpressionMultiply, roll, node(unreal.MaterialExpressionConstant, r=1.2)))
    # Less motion higher up: weight = 1 at the floor falling to 0.25 at the head (220 cm).
    low_weight = node(unreal.MaterialExpressionClamp, min_default=0.25, max_default=1.0)
    join(op(unreal.MaterialExpressionAdd, op(unreal.MaterialExpressionMultiply, height, node(unreal.MaterialExpressionConstant, r=-0.0045)), node(unreal.MaterialExpressionConstant, r=1.15)), low_weight, "")
    offset = op(unreal.MaterialExpressionMultiply, normal, op(unreal.MaterialExpressionMultiply, heave, low_weight))
    lib.connect_material_property(offset, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    lib.connect_material_property(colour, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    lib.connect_material_property(glow, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    lib.connect_material_property(node(unreal.MaterialExpressionConstant, r=0.22), "", unreal.MaterialProperty.MP_ROUGHNESS)
    lib.connect_material_property(node(unreal.MaterialExpressionConstant, r=0.35), "", unreal.MaterialProperty.MP_SPECULAR)
    if normal_map:
        bump = node(unreal.MaterialExpressionTextureSample, texture=normal_map, sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        join(swirl, bump, "UVs")
        lib.connect_material_property(bump, "RGB", unreal.MaterialProperty.MP_NORMAL)
    lib.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    mesh = unreal.EditorAssetLibrary.load_asset(f"{folder}/SK_TideCaller")
    slots = mesh.materials
    for slot in slots:
        slot.material_interface = material
    mesh.set_editor_property("materials", slots)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    report.update(status="CREATED", material=path, expressions=spot[0])
except Exception:
    report["status"] = "FAILED"
    report["error"] = traceback.format_exc()
out = root / "reports/creature-production/wc_vn_tide_caller/blender_rig_r001/water-material.json"
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
