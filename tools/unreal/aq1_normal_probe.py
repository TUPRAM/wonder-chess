"""Actual Unreal render comparison of a baked normal against raised geometry.

Required: WC_AQ1_PROBE_SOURCE (Blender helper output), WC_AQ1_PROBE_RUN
(simple name), WC_AQ1_PROBE_REPORT (fresh reports/...json).
Optional WC_AQ1_PROBE_PHASE=prepare|capture|both, default both.
Run an isolated UnrealEditor-Cmd Python commandlet with -AllowCommandletRendering
and a real RHI, never -nullrhi. Root owns editor execution and binary changes.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import time
import traceback


MOUNT = "/Game/WonderChess/Candidates/AQ1/NormalProbe"
INPUTS = ("SM_AQ1_NormalProbe_Low.fbx", "SM_AQ1_NormalProbe_Control.fbx", "T_AQ1_NormalProbe_PosY.png")
PANELS = (("Control", -48), ("Keep", 0), ("Flip", 48))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scoped(value, root):
    path = Path(value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Path escaped assigned workspace scope: " + str(path))
    return path


def protected_hashes(root, run):
    content = root / "game/Content"
    exclude = content / "WonderChess/Candidates/AQ1/NormalProbe" / run
    return {path.relative_to(content).as_posix(): sha(path)
            for path in content.rglob("*") if path.is_file() and not path.resolve().is_relative_to(exclude.resolve())}


def save(unreal, value, mount):
    if not value.get_path_name().startswith(mount + "/"):
        raise RuntimeError("Refusing to save an asset outside the normal-probe run")
    if not unreal.EditorAssetLibrary.save_loaded_asset(value, only_if_is_dirty=False):
        raise RuntimeError("Could not save probe asset " + value.get_path_name())


def import_asset(unreal, source, folder, name, fbx=False):
    job = unreal.AssetImportTask()
    job.filename, job.destination_path, job.destination_name = str(source), folder, name
    job.automated, job.replace_existing, job.save = True, False, True
    if fbx:
        options = unreal.FbxImportUI()
        options.automated_import_should_detect_type = False
        options.import_mesh, options.import_as_skeletal = True, False
        options.import_materials, options.import_textures, options.import_animations = False, False, False
        options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        data = options.static_mesh_import_data
        # The control FBX intentionally contains a base, chevron and marker.
        # Import them as one comparison panel, retaining their source transforms.
        data.combine_meshes = True
        data.convert_scene, data.convert_scene_unit, data.force_front_x_axis = True, True, True
        data.import_rotation = unreal.Rotator(pitch=0, yaw=180, roll=0)
        data.import_uniform_scale = 1.0
        data.generate_lightmap_u_vs = False
        data.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
        data.normal_generation_method = unreal.FBXNormalGenerationMethod.MIKK_T_SPACE
        job.options, job.factory = options, unreal.FbxFactory()
    else:
        job.factory = unreal.TextureFactory()
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([job])
    assets = [unreal.load_asset(path) for path in job.imported_object_paths]
    expected = folder + "/" + name + "." + name
    paths = [value.get_path_name() if value else None for value in assets]
    unreal.log("WC_AQ1_PROBE_IMPORT_RESULT " + json.dumps({"source": str(source), "expected": expected, "actual": paths}))
    expected_type = unreal.StaticMesh if fbx else unreal.Texture2D
    if len(assets) != 1 or paths != [expected] or not isinstance(assets[0], expected_type):
        raise RuntimeError("Probe import must produce its exact isolated mesh/texture: " + json.dumps(paths))
    return assets[0]


def material(unreal, folder, name, normal=None):
    assets = unreal.AssetToolsHelpers.get_asset_tools()
    mat = assets.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    edit = unreal.MaterialEditingLibrary
    color = edit.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, -100)
    color.set_editor_property("constant", unreal.LinearColor(.32, .32, .32, 1))
    edit.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    for value, prop, y in ((.78, unreal.MaterialProperty.MP_ROUGHNESS, 80), (0, unreal.MaterialProperty.MP_METALLIC, 170)):
        node = edit.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, y)
        node.set_editor_property("r", value)
        edit.connect_material_property(node, "", prop)
    if normal:
        node = edit.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -350, 350)
        node.set_editor_property("texture", normal)
        node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        edit.connect_material_property(node, "RGB", unreal.MaterialProperty.MP_NORMAL)
    edit.recompile_material(mat)
    save(unreal, mat, folder)
    return mat


def prepare(unreal, root, source, folder):
    if unreal.EditorAssetLibrary.does_directory_exist(folder):
        raise RuntimeError("Probe run already exists; choose a new run identifier")
    for command in ("Interchange.FeatureFlags.Import.FBX 0", "Interchange.FeatureFlags.Import.Enable 0"):
        unreal.SystemLibrary.execute_console_command(None, command)
    low = import_asset(unreal, source / INPUTS[0], folder, "SM_AQ1_NormalProbe_Low", True)
    control = import_asset(unreal, source / INPUTS[1], folder, "SM_AQ1_NormalProbe_Control", True)
    textures = {}
    for label, flip in (("Keep", False), ("Flip", True)):
        texture = import_asset(unreal, source / INPUTS[2], folder, "T_AQ1_NormalProbe_" + label)
        texture.srgb = False
        texture.compression_settings = unreal.TextureCompressionSettings.TC_NORMALMAP
        texture.flip_green_channel = flip
        texture.lod_bias = 0
        save(unreal, texture, folder)
        textures[label] = texture
    mats = {label: material(unreal, folder, "M_AQ1_NormalProbe_" + label, textures.get(label)) for label, _ in PANELS}
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not levels.new_level(folder + "/L_AQ1_NormalProbe"):
        raise RuntimeError("Could not create isolated normal-probe level")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for label, y in PANELS:
        actor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, y, 0))
        actor.set_actor_label("AQ1_Probe_" + label)
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        component.set_static_mesh(control if label == "Control" else low)
        for section in range(component.get_num_materials()):
            component.set_material(section, mats[label])
        component.set_cast_shadow(False)
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 150), unreal.Rotator(pitch=-38, yaw=32, roll=0))
    light.set_actor_label("AQ1_Probe_Key")
    component = light.get_component_by_class(unreal.DirectionalLightComponent)
    component.set_intensity(3.2)
    component.set_light_color(unreal.LinearColor(1, 1, 1, 1))
    component.set_cast_shadows(False)
    if not levels.save_current_level():
        raise RuntimeError("Could not save isolated normal-probe level")


def render_steps(unreal, folder, output, paced=False, on_capture=None):
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not levels.load_level(folder + "/L_AQ1_NormalProbe"):
        raise RuntimeError("Could not load normal-probe level")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None:
        raise RuntimeError("No initialized editor world for real rendering")
    for command in ("r.DefaultFeature.AutoExposure 0", "r.DefaultFeature.MotionBlur 0", "r.AntiAliasingMethod 0", "r.Streaming.FullyLoadUsedTextures 1", "t.IdleWhenNotForeground 0", "Slate.bAllowThrottling 0"):
        unreal.SystemLibrary.execute_console_command(world, command)
    if paced:
        # The actual commandlet cold-load attempt had no usable lit render.
        # Allow full Editor world/render updates before creating any capture.
        yield 60
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # Installed UKismetRenderingLibrary::DrawMaterialToRenderTarget calls
    # Material->EnsureIsComplete() before drawing. This provides a supported
    # shader-completion barrier, rather than sleeping without engine ticks.
    warmup = unreal.RenderingLibrary.create_render_target2d(world, 16, 16, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    for label, _ in PANELS:
        mat = unreal.load_asset(folder + "/M_AQ1_NormalProbe_" + label)
        unreal.RenderingLibrary.draw_material_to_render_target(world, warmup, mat)
        unreal.RenderingLibrary.read_render_target_pixel(world, warmup, 8, 8)
    if paced:
        yield 12

    # One capture actor and one freshly created target per view. Retain all
    # objects until every export completes; never mutate/reuse a live capture's
    # target, resolution or camera during this commandlet frame.
    views = []
    for label, y, width, size_x, size_y in [("comparison", 0, 150, 1500, 500)] + [(label.lower(), y, 46, 768, 768) for label, y in PANELS]:
        actor = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, y, 180), unreal.Rotator(pitch=-90, yaw=0, roll=0))
        actor.set_actor_label("AQ1_TransientNormalCapture_" + label)
        component = actor.get_component_by_class(unreal.SceneCaptureComponent2D)
        component.capture_every_frame = False
        component.capture_on_movement = False
        component.projection_type = unreal.CameraProjectionMode.ORTHOGRAPHIC
        component.capture_source = unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
        component.post_process_blend_weight = 0
        component.ortho_width = width
        target = unreal.RenderingLibrary.create_render_target2d(world, size_x, size_y, unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.035, .035, .035, 1))
        if target is None or [target.size_x, target.size_y] != [size_x, size_y]:
            raise RuntimeError("New target dimensions differ from requested view " + label)
        component.texture_target = target
        views.append((label, y, width, size_x, size_y, actor, component, target))
    if len({view[-1].get_path_name() for view in views}) != len(views):
        raise RuntimeError("Render-target allocation reused an existing view resource")
    if paced:
        yield 12
    captured = []
    for label, y, width, size_x, size_y, actor, component, target in views:
        name = label + ".png"
        path = output / name
        if path.exists():
            raise RuntimeError("Refusing to overwrite probe render " + str(path))
        unreal.RenderingLibrary.clear_render_target2d(world, target, unreal.LinearColor(0, 0, 0, 1))
        if paced:
            yield 2
        component.capture_scene()
        if paced:
            yield 4
        # Readback is a resource barrier and verifies each expected panel is lit.
        # It is a validity check, not an orientation-quality score.
        centers = [270, 750, 1230] if label == "comparison" else [size_x // 2]
        panel_samples = []
        unlit_centers = []
        for center in centers:
            samples = []
            for dx, dy in ((-70, -70), (0, -70), (70, -70), (-70, 70), (70, 70)):
                color = unreal.RenderingLibrary.read_render_target_pixel(world, target, center + dx, size_y // 2 + dy)
                samples.append([int(color.r), int(color.g), int(color.b)])
            panel_samples.append(samples)
            if max(channel for sample in samples for channel in sample) <= 10:
                unlit_centers.append(center)
        unreal.RenderingLibrary.export_render_target(world, target, str(output), name)
        if not path.is_file() or path.stat().st_size < 1024:
            raise RuntimeError("Actual Unreal PNG was not produced: " + name)
        data = path.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("Render export is not a PNG: " + name)
        actual_dimensions = list(struct.unpack(">II", data[16:24]))
        if unlit_centers:
            raise RuntimeError("Invalid black/unlit panel; retained actual PNG " + str(path) + " centers=" + str(unlit_centers) + " samples=" + str(panel_samples))
        if actual_dimensions != [size_x, size_y]:
            raise RuntimeError("Stale/mismatched PNG resolution: " + name + " " + str(actual_dimensions))
        file_hash = sha(path)
        if any(previous["sha256"] == file_hash for previous in captured):
            raise RuntimeError("Different camera/normal views returned identical PNG bytes: " + name)
        captured.append({"file": str(path), "sha256": sha(path), "bytes": path.stat().st_size,
                         "camera_location_cm": [0, y, 180], "camera_rotation": [-90, 0, 0],
                         "ortho_width_cm": width, "dimensions": actual_dimensions,
                         "render_target": target.get_path_name(), "capture_component": component.get_path_name(),
                         "panel_rgb_readbacks": panel_samples})
        if on_capture:
            on_capture(captured)
    for view in views:
        actors.destroy_actor(view[-3])
    return captured


def render(unreal, folder, output):
    iterator = render_steps(unreal, folder, output)
    while True:
        try:
            next(iterator)
        except StopIteration as complete:
            return complete.value


def start_editor_capture(unreal, root, run, folder, output, report, persist, before):
    """Return to the full Editor and advance actual capture across Slate ticks."""
    global _ASYNC_PROBE_SESSION
    command = unreal.SystemLibrary.get_command_line().lower()
    if "-executepythonscript=" not in command or "-run=" in command:
        raise RuntimeError("ASYNC_UI requires a newly launched full UnrealEditor -ExecutePythonScript process")
    # UE 5.7 exports UEditorPythonScriptingLibrary with ScriptName=EditorPythonScripting.
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    report["status"] = "CAPTURING_ACROSS_EDITOR_TICKS"
    report["capture_schedule"] = {"initial_world_ticks": 60, "material_ready_ticks": 12, "new_capture_resource_ticks": 12, "clear_ticks": 2, "render_ticks_before_export": 4}
    report["captures"] = []
    def progress(captures):
        report["captures"] = list(captures)
        persist()
    iterator = render_steps(unreal, folder, output.parent, paced=True, on_capture=progress)
    state = {"wait": 0, "ticks": 0, "start": time.monotonic(), "iterator": iterator, "handle": None, "executing": False}
    _ASYNC_PROBE_SESSION = state
    def finish(error=None):
        if state["handle"] is not None:
            unreal.unregister_slate_post_tick_callback(state["handle"])
            state["handle"] = None
        try:
            report["loaded"] = measurements(unreal, folder)
            after = protected_hashes(root, run)
            report["protected_differences"] = {"modified": sorted(name for name in before.keys() & after.keys() if before[name] != after[name]),
                                              "created": sorted(after.keys() - before.keys()), "deleted": sorted(before.keys() - after.keys())}
            report["protected_unchanged"] = not any(report["protected_differences"].values())
            if not report["protected_unchanged"]:
                error = (error or "") + "\nProtected Content changed during asynchronous capture"
        except Exception:
            error = (error or "") + "\n" + traceback.format_exc()
        report["editor_ticks"] = state["ticks"]
        report["status"] = "FAIL" if error else "EXECUTED_ASYNC_CAPTURE_PIXEL_REVIEW_PENDING"
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        if error:
            report["error"] = error
            unreal.log_error(error)
        persist()
        # The -ExecutePythonScript executor owns this new editor process and
        # exits after the keep-alive flag clears. Never stop another editor.
        unreal.EditorPythonScripting.set_keep_python_script_alive(False)
    def tick(delta):
        # Asset compilation can pump Slate recursively inside one generator step.
        if state["executing"]:
            return
        state["ticks"] += 1
        if time.monotonic() - state["start"] > 600:
            finish("Actual Editor capture exceeded its ten-minute bound")
            return
        if state["wait"] > 0:
            state["wait"] -= 1
            return
        try:
            state["executing"] = True
            state["wait"] = int(next(iterator))
            report["editor_ticks"] = state["ticks"]
            persist()
        except StopIteration as complete:
            report["captures"] = complete.value
            finish()
        except Exception:
            finish(traceback.format_exc())
        finally:
            state["executing"] = False
    state["handle"] = unreal.register_slate_post_tick_callback(tick)
    persist()


def measurements(unreal, folder):
    rows = []
    actor_system = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = {actor.get_actor_label(): actor for actor in actor_system.get_all_level_actors()}
    for label, y in PANELS:
        actor = actors["AQ1_Probe_" + label]
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        mesh = component.get_editor_property("static_mesh")
        data = mesh.get_editor_property("asset_import_data")
        bounds = mesh.get_bounds()
        rows.append({"panel": label, "actor": actor.get_path_name(), "mesh": mesh.get_path_name(),
                     "position_cm": [0, y, 0], "section_count_lod0": mesh.get_num_sections(0),
                     "materials_by_slot": [component.get_material(index).get_path_name() for index in range(component.get_num_materials())],
                     "bounds_extent_cm": [float(bounds.box_extent.x), float(bounds.box_extent.y), float(bounds.box_extent.z)],
                     "normal_import_method": str(data.normal_import_method), "normal_generation_method": str(data.normal_generation_method),
                     "combine_meshes": bool(data.combine_meshes), "generate_lightmap_u_vs": bool(data.generate_lightmap_u_vs)})
    textures = {}
    for label in ("Keep", "Flip"):
        texture = unreal.load_asset(folder + "/T_AQ1_NormalProbe_" + label)
        textures[label] = {"path": texture.get_path_name(), "srgb": bool(texture.srgb),
                           "compression": str(texture.compression_settings), "flip_green_channel": bool(texture.flip_green_channel),
                           "normal_sampler": "SAMPLERTYPE_NORMAL", "uv_channel": 0}
    return {"panels": rows, "textures": textures}


def main():
    import unreal
    root = Path(unreal.Paths.project_dir()).resolve().parent
    source = scoped(os.environ["WC_AQ1_PROBE_SOURCE"], root)
    output = scoped(os.environ["WC_AQ1_PROBE_REPORT"], root / "reports")
    run = os.environ["WC_AQ1_PROBE_RUN"]
    phase = os.environ.get("WC_AQ1_PROBE_PHASE", "both")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", run) or phase not in ("prepare", "capture", "both"):
        raise ValueError("Invalid probe run/phase")
    if output.exists() or output.suffix != ".json":
        raise ValueError("A fresh JSON evidence path is required")
    manifest = json.loads((source / "probe_manifest.json").read_text(encoding="utf-8-sig"))
    for name in INPUTS:
        if not (source / name).is_file() or manifest["files"].get(name) != sha(source / name):
            raise ValueError("Frozen probe input missing or changed: " + name)
    folder = MOUNT + "/" + run
    before = protected_hashes(root, run)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {"status": "STARTED", "utc": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
              "engine": unreal.SystemLibrary.get_engine_version(), "folder": folder, "phase": phase,
              "blender_manifest_sha256": sha(source / "probe_manifest.json"), "source_files": {name: sha(source / name) for name in INPUTS},
              "method": "Actual Unreal SceneCapture2D rendering; physical raised control beside shared-UV normal Keep and Flip variants",
              "light": {"type": "DirectionalLight", "rotation": [-38, 32, 0], "intensity": 3.2, "white": True, "cast_shadows": False},
              "orientation_acceptance": "PENDING_ROOT_PIXEL_COMPARISON", "protected_before": before}
    report["capture_validation_revision"] = 3
    report["prior_capture_defect"] = "Initial r02 commandlet capture had a black Flip panel and stale duplicate PNGs; r03 cold commandlet capture was black across all panels. Both are invalid orientation evidence. ASYNC_UI uses a full Editor and staged world/render ticks plus fresh per-view resources and pixel/dimension validity checks."
    def persist():
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    persist()
    if os.environ.get("WC_AQ1_PROBE_ASYNC_UI") == "1":
        if phase != "capture":
            raise ValueError("ASYNC_UI is an existing-map capture operation; use phase=capture")
        try:
            start_editor_capture(unreal, root, run, folder, output, report, persist, before)
        except Exception:
            report["status"], report["error"] = "FAIL", traceback.format_exc()
            persist()
            unreal.EditorPythonScripting.set_keep_python_script_alive(False)
            raise
        return
    error = None
    try:
        if phase in ("prepare", "both"):
            prepare(unreal, root, source, folder)
        if phase in ("capture", "both"):
            report["captures"] = render(unreal, folder, output.parent)
        report["loaded"] = measurements(unreal, folder)
    except Exception:
        error = traceback.format_exc()
    finally:
        after = protected_hashes(root, run)
        report["protected_differences"] = {"modified": sorted(name for name in before.keys() & after.keys() if before[name] != after[name]),
                                          "created": sorted(after.keys() - before.keys()), "deleted": sorted(before.keys() - after.keys())}
        report["protected_unchanged"] = not any(report["protected_differences"].values())
        if not report["protected_unchanged"]:
            error = (error or "") + "\nProtected production/other candidate Content changed"
        report["status"] = "FAIL" if error else "EXECUTED_" + phase.upper() + "_PIXEL_REVIEW_PENDING"
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        if error:
            report["error"] = error
        persist()
    if error:
        unreal.log_error(error)
        raise RuntimeError("Normal probe failed; inspect " + str(output))
    unreal.log("WC_AQ1_NORMAL_PROBE " + str(output))


if __name__ == "__main__":
    main()
