"""Five complete BW2 sheets from real native renders:30/30/30/30/25 frames."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json

out = Path(__file__).resolve().parent
frames = out / 'frames'
sheets = out / 'contact-sheets-final'
sheets.mkdir(exist_ok=False)
font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 16)
headerfont = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)
images = [frames / f'frame_{frame:04}.png' for frame in range(1, 146)]
assert all(path.is_file() for path in images)
tile_w, tile_h, label_h, header_h = 230, 230, 28, 75
inventory = []
for start in range(1, 146, 30):
    end = min(start + 29, 145)
    count = end - start + 1
    rows = (count + 4) // 5
    canvas = Image.new('RGB', (tile_w * 5, (tile_h + label_h) * rows + header_h), (28, 30, 33))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 11), f'BW3 THUMB APPROACH / OTHER FINGERS OPEN / NOT A GRIP | frames {start:03}-{end:03} | 24fps | ART_REVISE', font=font, fill=(238, 238, 238))
    for offset, frame in enumerate(range(start, end + 1)):
        col, row = offset % 5, offset // 5
        x, y = col * tile_w, header_h + row * (tile_h + label_h)
        with Image.open(frames / f'frame_{frame:04}.png') as image:
            assert image.size == (800, 800)
            image = image.convert('RGB')
            image.thumbnail((tile_w, tile_h), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + (tile_w - image.width) // 2, y))
        phase = 'approach' if frame < 25 else 'thumb carry'
        draw.text((x + 7, y + tile_h + 3), f'{frame:03} | {(frame - 1) / 24:.3f}s | {phase}', font=font, fill=(240, 240, 240))
    path = sheets / f'frames_{start:03}_{end:03}.jpg'
    canvas.save(path, quality=94, subsampling=0)
    inventory.append({'file': str(path), 'first_frame': start, 'last_frame': end,
                      'frame_count': count, 'dimensions': list(canvas.size),
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
manifest = {
    'status': 'ALL145_NATIVE_FRAMES_INCLUDED_UNSKIPPED',
    'source': 'Actual unchanged Blender PNGs; uniform800x800 to230x230 downsample; labels outside image; no invented frames, warping, or pixel repairs.',
    'source_blend_sha256': '2dad0803a3e8bfd1974b3bf86dbf5377cd462807f02fb9e76f45463205ba2a1d',
    'total_frames': 145, 'sheet_count': len(inventory), 'sheets': inventory,
    'native_frames': [{'frame': frame, 'file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                      for frame, path in enumerate(images, 1)],
    'art_approval': False,
}
assert [row['frame_count'] for row in inventory] == [30, 30, 30, 30, 25]
with (out / 'contact_sheet_manifest_final.json').open('x', encoding='utf-8') as stream:
    json.dump(manifest, stream, indent=2)
    stream.write('\n')
print(json.dumps({'sheets': len(inventory), 'frames': sum(row['frame_count'] for row in inventory)}))


