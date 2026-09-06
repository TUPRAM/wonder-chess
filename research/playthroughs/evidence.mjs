import { appendFile, mkdir, readFile, realpath, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const runsRoot = resolve(dirname(fileURLToPath(import.meta.url)), 'runs');

export async function saveCapture({ runDirectory, state, observedAtUtc, tag, screenshotIndex,
  round = null, elapsedSeconds = null }) {
  const root = await realpath(runsRoot);
  const run = await realpath(runDirectory);
  const child = relative(root, run);
  if (!child || child.startsWith('..') || child.includes(sep)) {
    throw new Error('Use an existing direct session directory under playthroughs/runs.');
  }
  await readFile(join(run, 'session.json'), 'utf8').then(JSON.parse);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(tag ?? '') || tag.length > 70) {
    throw new Error('tag must be a short lowercase filename label.');
  }
  if (typeof observedAtUtc !== 'string' || !observedAtUtc.endsWith('Z') ||
      !Number.isFinite(Date.parse(observedAtUtc))) {
    throw new Error('Supply the actual ISO UTC observation time.');
  }
  if (elapsedSeconds !== null && (!Number.isFinite(elapsedSeconds) || elapsedSeconds < 0)) {
    throw new Error('elapsedSeconds must be an observed nonnegative number or null.');
  }
  if (round !== null && !['string', 'number'].includes(typeof round)) {
    throw new Error('round must be a visible label, number or null.');
  }
  const shots = state?.screenshots;
  if (!Array.isArray(shots) || !shots.length || !state?.window?.app ||
      !Number.isInteger(state.window.id)) throw new Error('Supply an actual Computer Use window state.');
  if (screenshotIndex === undefined && shots.length !== 1) {
    throw new Error('Select screenshotIndex explicitly for a multi-image state.');
  }
  const shot = shots[screenshotIndex ?? 0];
  const match = /^data:image\/(png|jpeg);base64,([A-Za-z0-9+/]+={0,2})$/.exec(shot?.url ?? '');
  if (!match || !shot.id) throw new Error('Expected a returned PNG/JPEG data URL and screenshot ID.');
  const bytes = Buffer.from(match[2], 'base64');
  if (bytes.toString('base64') !== match[2]) throw new Error('Invalid base64 image data.');
  const png = match[1] === 'png';
  const signatureValid = png
    ? bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))
    : bytes.length >= 4 && bytes[0] === 255 && bytes[1] === 216 &&
      bytes[bytes.length - 2] === 255 && bytes[bytes.length - 1] === 217;
  if (!signatureValid) throw new Error('Image signature does not match the declared media type.');
  const indexPath = join(run, 'screenshots', 'index.jsonl');
  const existing = await readFile(indexPath, 'utf8').catch(error => {
    if (error.code === 'ENOENT') return '';
    throw error;
  });
  const records = existing.split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
  const id = `SHOT-${String(records.length + 1).padStart(3, '0')}`;
  const stamp = new Date(observedAtUtc).toISOString().replace(/[-:.]/g, '');
  const file = `screenshots/raw/${id}_${stamp}_${tag}.${png ? 'png' : 'jpg'}`;
  await mkdir(join(run, 'screenshots', 'raw'), { recursive: true });
  await writeFile(join(run, file), bytes, { flag: 'wx' });
  const record = {
    id, file, tag, observed_utc: observedAtUtc, saved_utc: new Date().toISOString(),
    elapsed_seconds: elapsedSeconds, round, source: 'computer-use:get_window_state',
    source_window: state.window, source_screenshot_id: shot.id,
    width: shot.width ?? null, height: shot.height ?? null,
    bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')
  };
  await appendFile(indexPath, JSON.stringify(record) + '\n');
  return record;
}
