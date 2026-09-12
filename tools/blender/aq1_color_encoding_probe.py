"""Actual Cycles bake/save/reload regression for the AQ1 RGB16 color washout."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aq1_bake import _image, _save_image


def _linear(value):
    return value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4


def _png_center(path):
    """Read actual PNG samples without a Pillow dependency or display transform."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("Output is not a PNG")
    offset, compressed, header = 8, bytearray(), None
    while offset < len(data):
        size = struct.unpack_from(">I", data, offset)[0]
        kind, payload = data[offset + 4:offset + 8], data[offset + 8:offset + 8 + size]
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            compressed.extend(payload)
        offset += size + 12
    width, height, depth, color, compression, filtering, interlace = header
    if depth not in (8, 16) or color not in (2, 6) or compression or filtering or interlace:
        raise AssertionError("Probe expects a noninterlaced RGB/RGBA8/16 PNG")
    channels = 3 if color == 2 else 4
    pixel_bytes = channels * depth // 8
    stride = width * pixel_bytes
    raw = zlib.decompress(compressed)
    prior = bytearray(stride)
    center = None
    for y in range(height):
        start = y * (stride + 1)
        mode, row = raw[start], bytearray(raw[start + 1:start + 1 + stride])
        for i in range(stride):
            left = row[i - pixel_bytes] if i >= pixel_bytes else 0
            up, upper_left = prior[i], prior[i - pixel_bytes] if i >= pixel_bytes else 0
            if mode == 0:
                predictor = 0
            elif mode == 1:
                predictor = left
            elif mode == 2:
                predictor = up
            elif mode == 3:
                predictor = (left + up) // 2
            elif mode == 4:
                estimate = left + up - upper_left
                candidates = [left, up, upper_left]
                predictor = min(candidates, key=lambda value: abs(estimate - value))
            else:
                raise AssertionError("Unsupported PNG row filter")
            row[i] = (row[i] + predictor) & 255
        if y == height // 2:
            x = width // 2 * pixel_bytes
            sample = row[x:x + pixel_bytes]
            center = list(sample[:3]) if depth == 8 else list(struct.unpack(">" + "H" * channels, sample)[:3])
        prior = row
    return {"width": width, "height": height, "bit_depth": depth,
            "color_type": color, "center_rgb_integer": center,
            "center_rgb_normalized": [value / ((1 << depth) - 1) for value in center]}


def run_probe(outdir):
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    report_path = outdir / "color-encoding-results.json"
    if report_path.exists() or any(outdir.glob("AQ1_Encoding_*.png")):
        raise FileExistsError("Use a fresh directory; preserve prior regression evidence")
    report = {"status": "STARTED", "regression_revision": 2,
              "blender_version": bpy.app.version_string,
              "source_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "bake_helper_sha256": hashlib.sha256(Path(__file__).with_name("aq1_bake.py").read_bytes()).hexdigest(),
              "method": "Cycles EMIT bake/save; raw PNG decode; reloaded image sampled by a shader and EMIT-baked into a linear readback image",
              "oracle_correction": "Revision 1 incorrectly treated byte-image Image.pixels as shader-linear values; that retained failure does not invalidate its correct RGB8 PNG bytes",
              "cases": [], "original_scene_restored": False}
    scene = bpy.data.scenes.new("AQ1_ColorEncodingRegression")
    window = bpy.context.window
    previous_scene = window.scene if window else None
    if window:
        window.scene = scene
    try:
        with bpy.context.temp_override(scene=scene, view_layer=scene.view_layers[0]):
            scene.render.engine = "CYCLES"
            scene.cycles.samples = 1
            scene.render.bake.use_selected_to_active = False
            scene.render.bake.use_clear = True
            scene.render.bake.margin = 0
            mesh = bpy.data.meshes.new("AQ1_EncodingPlane_Mesh")
            mesh.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
            mesh.update()
            uv = mesh.uv_layers.new(name="UV0")
            for index, pair in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
                uv.data[index].uv = pair
            plane = bpy.data.objects.new("AQ1_EncodingPlane", mesh)
            scene.collection.objects.link(plane)
            material = bpy.data.materials.new("M_AQ1_EncodingRegression")
            material.use_nodes = True
            material.node_tree.nodes.clear()
            output = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
            emission = material.node_tree.nodes.new("ShaderNodeEmission")
            material.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])
            destination = material.node_tree.nodes.new("ShaderNodeTexImage")
            reload_sample = material.node_tree.nodes.new("ShaderNodeTexImage")
            reload_sample.interpolation = "Closest"
            material.node_tree.nodes.active = destination
            mesh.materials.append(material)
            plane.select_set(True)
            scene.view_layers[0].objects.active = plane
            cases = [
                ("NavyBaseColor", "sRGB", [_linear(value / 255) for value in (37, 70, 107)], [37, 70, 107]),
                ("LinearORM", "Non-Color", [.77, .83, 0], None),
            ]
            for name, color_space, expected_linear, expected_bytes in cases:
                image = _image("AQ1_Encoding_" + name, 32, color_space)
                emission.inputs["Color"].default_value = (*expected_linear, 1)
                emission.inputs["Strength"].default_value = 1
                destination.image = image
                bpy.ops.object.bake(type="EMIT")
                path = outdir / ("AQ1_Encoding_" + name + ".png")
                saved = _save_image(image, path)
                decoded = _png_center(path)
                loaded = bpy.data.images.load(str(path), check_existing=False)
                loaded.colorspace_settings.name = color_space
                start = (16 * 32 + 16) * 4
                raw_reloaded = list(loaded.pixels[start:start + 3])
                # Image.pixels exposes encoded storage for byte images in the
                # installed Blender. Exercise the actual material color-space
                # conversion instead of labelling that raw view scene-linear.
                reload_sample.image = loaded
                readback = _image("AQ1_Encoding_" + name + "_ShaderLinear", 32, "Non-Color")
                destination.image = readback
                material.node_tree.nodes.active = destination
                sample_link = material.node_tree.links.new(reload_sample.outputs["Color"],
                                                           emission.inputs["Color"])
                try:
                    bpy.ops.object.bake(type="EMIT")
                finally:
                    material.node_tree.links.remove(sample_link)
                readback_path = outdir / ("AQ1_Encoding_" + name + "_ShaderLinear.png")
                readback_saved = _save_image(readback, readback_path)
                shader_png = _png_center(readback_path)
                shader_linear = shader_png["center_rgb_normalized"]
                linear_error = max(abs(a - b) for a, b in zip(shader_linear, expected_linear))
                record = {"name": name, "color_space": color_space,
                          "source_linear_rgb": expected_linear, "target_is_float": bool(image.is_float),
                          "saved": saved, "png": decoded,
                          "blender_reloaded_raw_pixels": raw_reloaded,
                          "raw_pixel_interpretation": "storage-level inspection only; shader readback is the linear oracle",
                          "shader_readback_saved": readback_saved,
                          "shader_readback_png": shader_png,
                          "blender_shader_reloaded_linear_rgb": shader_linear,
                          "max_shader_reloaded_linear_error": linear_error}
                report["cases"].append(record)
                assert shader_png["bit_depth"] == 16, "Linear shader readback lost its expected precision"
                if expected_bytes:
                    error = max(abs(a - b) for a, b in zip(decoded["center_rgb_integer"], expected_bytes))
                    record["max_encoded_byte_error"] = error
                    assert decoded["bit_depth"] == 8, "BaseColor game delivery must be RGB8"
                    assert error <= 1, "Known navy sRGB pixels changed by more than one encoded unit"
                    assert linear_error <= 1 / 255, "Shader sampling the saved sRGB PNG does not recover linear navy"
                else:
                    error = max(abs(a - b) for a, b in zip(decoded["center_rgb_normalized"], expected_linear))
                    record["max_raw_linear_channel_error"] = error
                    assert image.is_float, "Linear data authoring buffers must retain floating-point precision"
                    assert decoded["bit_depth"] == 16, "Linear data intermediate unexpectedly changed precision"
                    assert error <= 2 / 65535, "Saved ORM values acquired a gamma transform"
                    assert linear_error <= 2 / 65535, "Shader sampling the saved ORM acquired a gamma transform"
                record["status"] = "PASS"
            report["status"] = "PASS_ACTUAL_BAKE_SAVE_RELOAD"
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = repr(error)
        raise
    finally:
        if window and previous_scene:
            window.scene = previous_scene
        report["original_scene_restored"] = not window or window.scene == previous_scene
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("AQ1_COLOR_ENCODING_REGRESSION " + str(report_path), flush=True)
    return report


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    run_probe(parser.parse_args(arguments).output)
