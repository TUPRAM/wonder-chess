"""Caption the AS1 comparison without changing the rendered image panels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json

out = Path(__file__).resolve().parent
source = out / 'comparison_verified_BW2_thumb_vs_C.png'
dest = out / 'comparison_verified_BW2_thumb_vs_C_final_labels.png'
assert not dest.exists()
image = Image.open(source).convert('RGB')
result = Image.new('RGB', (image.width, image.height + 118), (28, 29, 32))
result.paste(image, (0, 88))
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18)
d = ImageDraw.Draw(result)
d.text((16, 10), 'THUMB-ONLY ROUTE COMPARISON / OTHER FINGERS OPEN / NOT A GRIP', font=font, fill='white')
d.text((16, 47), 'BW2 ISOLATED THUMB / FAILED BASELINE', font=small, fill='white')
d.text((image.width // 2 + 16, 47), 'BW3 C / PARTIAL APPROACH, NOT A GRIP', font=small, fill='white')
d.text((16, image.height + 91), 'Same camera and lighting; other fingers OPEN; fixture HIDDEN. Changed thumb pose. No image warp or repair.', font=small, fill='white')
result.save(dest)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
(out / 'comparison_metadata_final.json').write_text(json.dumps({
    'sheet': str(dest), 'sha256': sha(dest), 'as1_sheet': str(source), 'as1_sha256': sha(source),
    'baseline': '../onset/isolated_verified_glove_frame25_oblique.png',
    'candidate': 'C_matched_BW2_isolated_thumb_oblique.png',
    'operation': 'AS1 downsample-only sheet plus external caption bands; rendered panels unmodified',
    'registered': False, 'quality_score': None,
    'scope': 'Other fingers open in both. Changed thumb route, not same pose or complete grip.'
}, indent=2) + '\n')
