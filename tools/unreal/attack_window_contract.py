"""Pure validation for optional authored presentation windows; no Unreal import side effects."""
import math

TRACK = 'WC_Attack_Windows'
PREFIX = 'WC_Attack_'


def attack_window_plan(clip, fps, windup_ms):
    windows = clip.get('presentation_windows')
    if windows is None:
        return None
    if fps != 60 or isinstance(fps, bool):
        raise ValueError('Attack windows require the authored 60 FPS contract')
    if not isinstance(windows, list) or len(windows) != 2:
        raise ValueError('Attack windows must contain exactly R and L cycles')
    bounds = clip.get('frames')
    if not isinstance(bounds, list) or len(bounds) != 2 or bounds[0] != 1:
        raise ValueError('Attack clip must start at authored frame1')
    if any(type(value) is not int for value in bounds) or bounds[1] <= bounds[0]:
        raise ValueError('Attack clip bounds must be increasing integer frames')
    if type(windup_ms) is not int or windup_ms <= 0 or windup_ms * fps % 1000:
        raise ValueError('Canonical windup must align to whole authored frame intervals')
    prior = bounds[0]
    markers = {}
    for expected, window in zip(('R', 'L'), windows):
        if not isinstance(window, dict) or set(window) != {'name', 'start_frame', 'release_frame', 'end_frame'}:
            raise ValueError('Attack window fields differ from the presentation contract')
        if window['name'] != expected:
            raise ValueError('Attack windows must be ordered R then L')
        start, release, end = (window[key] for key in ('start_frame', 'release_frame', 'end_frame'))
        if any(type(value) is not int for value in (start, release, end)):
            raise ValueError('Attack window frames must be integers')
        if start != prior or not start < release < end or end > bounds[1]:
            raise ValueError('Attack windows must be contiguous, bounded, complete cycles')
        if (release - start) * 1000 != windup_ms * fps:
            raise ValueError('Each cut must release at the canonical basic windup')
        for suffix, frame in (('Start', start), ('Release', release), ('End', end)):
            markers[PREFIX + expected + '_' + suffix] = (frame - bounds[0]) / fps
        prior = end
    if prior != bounds[1] or clip.get('release_frame') != windows[0]['release_frame']:
        raise ValueError('Attack windows must cover the clip and preserve its first release marker')
    return {'markers': markers, 'duration_seconds': (bounds[1] - bounds[0]) / fps,
            'windows': windows, 'track': TRACK}


def validate_imported_markers(plan, duration_seconds, markers):
    """Readback may contain unrelated markers, but every owned marker must match exactly once."""
    expected = plan['markers'] if plan else {}
    found = {}
    for name, value in markers:
        if not name.startswith(PREFIX):
            continue
        if name in found or name not in expected or not math.isfinite(value):
            raise ValueError('Duplicate, unknown or nonfinite imported attack marker: ' + name)
        found[name] = value
    if set(found) != set(expected) or any(abs(found[name] - value) > .0001 for name, value in expected.items()):
        raise ValueError('Imported attack-window marker names/times differ from the authored plan')
    if plan and (not math.isfinite(duration_seconds) or abs(duration_seconds - plan['duration_seconds']) > .0001):
        raise ValueError('Imported Attack duration differs from the authored window extent')
    return found
