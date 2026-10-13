"""Create original, non-production media for reversible tool qualification."""
import io
import json
import math
import struct
import wave
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'support/tools/pipeline/fixtures'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bg = Image.new('RGBA', (1024, 768), '#f3eee0')
    layer = Image.new('RGBA', bg.size)
    draw = ImageDraw.Draw(layer)
    draw.text((32, 24), 'WONDER CHESS - TOOL INTERCHANGE FIXTURE / NOT CREATURE ART', fill='#202838')
    for i, (name, color) in enumerate(zip(('MAIN +X', 'LEFT -Y', 'BACK -X', 'RIGHT +Y'),
                                         ('#b98553', '#738d61', '#d7bb66', '#8ca9b2'))):
        x = 32 + i * 248
        draw.rectangle((x, 80, x + 224, 680), fill=color, outline='#202838', width=3)
        draw.text((x + 15, 100), name, fill='#202838')
        draw.line((x + 20, 550, x + 204, 550), fill='#202838', width=3)
        draw.ellipse((x + 45, 180, x + 180, 315), outline='#202838', width=8)
    merged = Image.alpha_composite(bg, layer)
    merged.save(OUT / 'reference-board.png')
    with zipfile.ZipFile(OUT / 'reference-board.ora', 'w') as z:
        z.writestr('mimetype', 'image/openraster', compress_type=zipfile.ZIP_STORED)
        z.writestr('stack.xml', '<image w="1024" h="768" name="Qualification only"><stack>'
                   '<layer name="View markers" src="data/markers.png" opacity="1.0" visibility="visible" composite-op="svg:src-over" x="0" y="0"/>'
                   '<layer name="Neutral background" src="data/background.png" opacity="1.0" visibility="visible" composite-op="svg:src-over" x="0" y="0"/>'
                   '</stack></image>')
        for name, img in [('data/markers.png', layer), ('data/background.png', bg), ('mergedimage.png', merged)]:
            b = io.BytesIO(); img.save(b, format='PNG'); z.writestr(name, b.getvalue())
    # 100 cm diagnostic cube, deliberately asymmetric vertex label in source comment.
    (OUT / 'cube-centimeters.obj').write_text('''# Qualification only; units=centimeters; +X forward +Y right +Z up
o qualification_cube
v -50 -50 0
v 50 -50 0
v 50 50 0
v -50 50 0
v -50 -50 100
v 50 -50 100
v 50 50 100
v -50 50 100
vt 0 0
vt 1 0
vt 1 1
vt 0 1
f 1/1 3/3 2/2
f 1/1 4/4 3/3
f 5/1 6/2 7/3
f 5/1 7/3 8/4
f 1/1 2/2 6/3
f 1/1 6/3 5/4
f 2/1 3/2 7/3
f 2/1 7/3 6/4
f 3/1 4/2 8/3
f 3/1 8/3 7/4
f 4/1 1/2 5/3
f 4/1 5/3 8/4
''', encoding='utf-8')
    with wave.open(str(OUT / 'qualification-tone-48k.wav'), 'wb') as w:
        w.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        for i in range(48000 * 3):
            t = i / 48000
            env = max(0, min(1, (t - 0.3) / 0.02, (2.7 - t) / 0.02))
            w.writeframesraw(struct.pack('<h', round(32767 * 0.12 * env * math.sin(2 * math.pi * 440 * t))))
    (OUT / 'README.md').write_text('# Tool qualification fixtures\n\nOriginal synthetic files created locally. No accepted art, AI media, microphone or desktop recording. These are interoperability tests, not approved production assets.\n', encoding='utf-8')
    print(json.dumps({'directory': str(OUT), 'files': sorted(p.name for p in OUT.iterdir())}))


if __name__ == '__main__':
    main()
