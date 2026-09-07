"""Check actual MP4 timing against rendered source frames; make a labeled pose index."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from PIL import Image, ImageDraw


def boxes(data):
    at = 0
    while at + 8 <= len(data):
        size, kind = struct.unpack_from('>I4s', data, at)
        header = 8
        if size == 1:
            size = struct.unpack_from('>Q', data, at + 8)[0]
            header = 16
        if not size:
            size = len(data) - at
        if size < header or at + size > len(data):
            raise ValueError('Invalid MP4 box bounds')
        yield kind, data[at + header:at + size]
        at += size


def one(data, wanted):
    return next(payload for kind, payload in boxes(data) if kind == wanted)


def video_timing(path):
    movie = one(path.read_bytes(), b'moov')
    for kind, track in boxes(movie):
        if kind != b'trak':
            continue
        media = one(track, b'mdia')
        if one(media, b'hdlr')[8:12] != b'vide':
            continue
        header = one(media, b'mdhd')
        timescale = struct.unpack_from('>I', header, 20 if header[0] == 1 else 12)[0]
        table = one(one(media, b'minf'), b'stbl')
        timing = one(table, b'stts')
        entries = struct.unpack_from('>I', timing, 4)[0]
        counts = [struct.unpack_from('>II', timing, 8 + 8 * index) for index in range(entries)]
        samples = sum(count for count, _ in counts)
        ticks = sum(count * delta for count, delta in counts)
        sizes = one(table, b'stsz')
        assert struct.unpack_from('>I', sizes, 8)[0] == samples
        return {'video_samples': samples, 'timescale': timescale, 'duration_seconds': ticks / timescale,
                'fps': samples * timescale / ticks, 'codec': one(table, b'stsd')[12:16].decode('ascii')}
    raise ValueError('No video track')


parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
out = parser.parse_args().output.resolve()
sequence = json.loads((out / 'motion-sequences.json').read_text())
records = []
for clip in sequence['clips']:
    path = Path(clip['path'])
    timing = video_timing(path)
    assert timing['video_samples'] == clip['frames'][1] - clip['frames'][0] + 1
    assert abs(timing['fps'] - 60) < 1e-6 and timing['codec'] == 'avc1'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == clip['sha256']
    records.append({'clip': clip['clip'], 'path': str(path), **timing})
poses = sorted(out.glob('pose_*.png'))
sheet = Image.new('RGB', (5 * 224, ((len(poses) + 4) // 5) * 248), '#141d28')
draw = ImageDraw.Draw(sheet)
for index, path in enumerate(poses):
    x, y = (index % 5) * 224, (index // 5) * 248
    with Image.open(path) as source:
        sheet.paste(source.convert('RGB').resize((224, 224)), (x, y))
    draw.text((x + 4, y + 228), path.stem.removeprefix('pose_'), fill='white')
sheet.save(out / 'pose-index.png')
(out / 'normal-speed-evidence.json').write_text(json.dumps({
    'status': 'ACTUAL_MP4_FRAME_COUNT_AND_60FPS_TIMING_VERIFIED', 'clips': records,
    'method': 'Read actual MP4 video stts/stsz/mdhd tables, codec and file hashes',
    'pose_index': str(out / 'pose-index.png'),
    'limits': ['Video rendering and timing are not continuous visual acceptance',
               'Pose index contains selected frames only', 'Unreal review remains pending']}, indent=2) + '\n')
print(json.dumps(records, indent=2))
