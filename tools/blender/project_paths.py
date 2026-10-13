"""Resolve moved Wonder Chess image paths in memory; never save a source file."""
from pathlib import Path
import bpy


def relink_missing_images(project_root):
    root = Path(project_root).resolve()
    changed, unresolved = [], []
    for image in bpy.data.images:
        if image.source != 'FILE' or image.packed_file or not image.filepath:
            continue
        if Path(bpy.path.abspath(image.filepath)).is_file():
            continue
        old = image.filepath
        normalized = old.replace('\\', '/')
        marker = '/Wonder Chess/'
        candidate = (root / normalized.split(marker, 1)[1]).resolve() if marker in normalized else None
        if candidate and candidate.is_relative_to(root) and candidate.is_file():
            image.filepath = bpy.path.relpath(str(candidate)) if bpy.data.filepath else str(candidate)
            try:
                image.reload()
            except Exception:
                image.filepath = old
                raise
            changed.append({'image': image.name, 'previous': old, 'current': image.filepath})
        else:
            unresolved.append({'image': image.name, 'path': old})
    return {'relinked': changed, 'unresolved': unresolved, 'saved': False}
