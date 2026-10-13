"""Decode the synthetic OBS capture; never records the desktop or microphone."""
import array
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from asset_checks import sha256

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'support/tools/pipeline/python'))
import imageio_ffmpeg

OUT = ROOT / 'reports/pipeline-tools-20260921'
FIX = ROOT / 'support/tools/pipeline/fixtures'
source = Path((OUT / 'obs-recording-path.txt').read_text().strip())
destination = FIX / 'obs-qualification.mp4'
if destination.exists() and sha256(destination) != sha256(source):
    raise RuntimeError('Existing recording differs; preserve it and choose a new revision')
if not destination.exists(): shutil.copy2(source, destination)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
decoded = subprocess.run([ffmpeg, '-v', 'info', '-i', str(destination), '-f', 'null', '-'],
                         capture_output=True, text=True, check=True)
(OUT / 'obs-decode.log').write_text(decoded.stderr, encoding='utf-8')
pcm = subprocess.run([ffmpeg, '-v', 'error', '-i', str(destination), '-vn', '-f', 'f32le', '-'],
                     capture_output=True, check=True)
samples = array.array('f', pcm.stdout)
peak = max(map(abs, samples), default=0.0)
for second in (1, 7):
    subprocess.run([ffmpeg, '-v', 'error', '-y', '-ss', str(second), '-i', str(destination),
                    '-frames:v', '1', str(OUT / f'obs-frame-{second}.png')], check=True)
result = {'status': 'pass' if peak == 0 and samples else 'fail',
          'source_path': str(source), 'preserved_path': destination.relative_to(ROOT).as_posix(),
          'sha256': sha256(destination), 'decoded_without_errors': True,
          'audio_peak_linear': peak, 'decoded_audio_samples': len(samples),
          'scope': 'image-only synthetic recording; no creature or performance acceptance',
          'ffmpeg_version': subprocess.run([ffmpeg, '-version'], capture_output=True, text=True).stdout.splitlines()[0],
          'duration_header': re.search(r'Duration: ([\d:.]+)', decoded.stderr).group(1),
          'visual_review': 'pending'}
(OUT / 'obs-qualification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
