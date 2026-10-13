"""Create the four particle materials the game's effect system draws with. Each reads a colour (floats 0-2) and an
alpha (float 3) per instance, so one material serves every particle of its kind.

  M_FxGlow    soft round additive light
  M_FxSmoke   soft translucent puff broken up by noise
  M_FxRing    thin additive ring, for shockwaves on the ground
  M_FxStreak  additive streak, bright in the middle and fading to both ends, for sparks, trails and beams
"""
import json
from pathlib import Path

import unreal

root = Path(unreal.Paths.project_dir()).resolve().parent
folder = "/Game/WonderChess/VNext/Effects"
tools = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.MaterialEditingLibrary
made = []


def build(name, additive, shape):
    path = f"{folder}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    material = tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE if additive else unreal.BlendMode.BLEND_TRANSLUCENT)
    material.set_editor_property("two_sided", True)
    material.set_editor_property("used_with_instanced_static_meshes", True)
    counter = [0]

    def node(cls, **props):
        counter[0] += 1
        expression = lib.create_material_expression(material, cls, -1400 + (counter[0] % 7) * 190, (counter[0] // 7) * 150)
        for key, value in props.items():
            expression.set_editor_property(key, value)
        return expression

    def link(source, target, pin, output=""):
        if not lib.connect_material_expressions(source, output, target, pin):
            raise RuntimeError(f"{name}: could not connect into {pin}")
        return target

    def unary(cls, source, **props):
        return link(source, node(cls, **props), "")

    def binary(cls, a, b):
        target = node(cls)
        link(a, target, "A")
        return link(b, target, "B")

    colour = node(unreal.MaterialExpressionPerInstanceCustomData3Vector, data_index=0,
                  const_default_value=unreal.LinearColor(1, 1, 1, 1))
    alpha = node(unreal.MaterialExpressionPerInstanceCustomData, data_index=3, const_default_value=1.0)
    uv = node(unreal.MaterialExpressionTextureCoordinate)
    centred = link(uv, node(unreal.MaterialExpressionSubtract, const_b=0.5), "A")
    mask = shape(node, link, unary, binary, uv, centred)
    faded = binary(unreal.MaterialExpressionMultiply, mask, alpha)
    if additive:
        lit = binary(unreal.MaterialExpressionMultiply, colour, faded)
        lib.connect_material_property(lit, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        lib.connect_material_property(colour, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        lib.connect_material_property(faded, "", unreal.MaterialProperty.MP_OPACITY)
    lib.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    made.append(name)


def radial(node, link, unary, centred, power):
    """1 at the centre of the quad, 0 at its edge, with a soft curve."""
    distance = unary(unreal.MaterialExpressionLength, centred)
    edge = unary(unreal.MaterialExpressionOneMinus, link(distance, node(unreal.MaterialExpressionMultiply, const_b=2.0), "A"))
    return link(unary(unreal.MaterialExpressionSaturate, edge), node(unreal.MaterialExpressionPower, const_exponent=power), "Base")


def glow(node, link, unary, binary, uv, centred):
    return radial(node, link, unary, centred, 2.2)


def smoke(node, link, unary, binary, uv, centred):
    body = unary(unreal.MaterialExpressionSaturate,
                 link(radial(node, link, unary, centred, 1.3), node(unreal.MaterialExpressionMultiply, const_b=1.7), "A"))
    texture = unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/Good64x64TilingNoiseHighFreq")
    if not texture:
        return body
    sample = node(unreal.MaterialExpressionTextureSample, texture=texture)
    link(link(uv, node(unreal.MaterialExpressionMultiply, const_b=0.55), "A"), sample, "UVs")
    grain = link(link(sample, node(unreal.MaterialExpressionMultiply, const_b=0.5), "A", "R"), node(unreal.MaterialExpressionAdd, const_b=0.5), "A")
    return binary(unreal.MaterialExpressionMultiply, body, grain)


def ring(node, link, unary, binary, uv, centred):
    distance = link(unary(unreal.MaterialExpressionLength, centred), node(unreal.MaterialExpressionMultiply, const_b=2.0), "A")
    off = unary(unreal.MaterialExpressionAbs, link(distance, node(unreal.MaterialExpressionSubtract, const_b=0.82), "A"))
    band = unary(unreal.MaterialExpressionOneMinus, link(off, node(unreal.MaterialExpressionDivide, const_b=0.15), "A"))
    return link(unary(unreal.MaterialExpressionSaturate, band), node(unreal.MaterialExpressionPower, const_exponent=1.6), "Base")


def streak(node, link, unary, binary, uv, centred):
    def side(channel_r, power):
        part = unary(unreal.MaterialExpressionComponentMask, centred, r=channel_r, g=not channel_r, b=False, a=False)
        far = link(unary(unreal.MaterialExpressionAbs, part), node(unreal.MaterialExpressionMultiply, const_b=2.0), "A")
        return link(unary(unreal.MaterialExpressionSaturate, unary(unreal.MaterialExpressionOneMinus, far)),
                    node(unreal.MaterialExpressionPower, const_exponent=power), "Base")
    return binary(unreal.MaterialExpressionMultiply, side(True, 0.8), side(False, 2.4))


build("M_FxGlow", True, glow)
build("M_FxSmoke", False, smoke)
build("M_FxRing", True, ring)
build("M_FxStreak", True, streak)
report = root / "reports/vnext/environment/fx-materials-r001.json"
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps({"folder": folder, "materials": made}, indent=2))
