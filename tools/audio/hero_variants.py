"""Deterministic original active-skill sounds, derived from the 12 alpha dossiers.

Uses only Python's standard library. These PCM assets contain no recordings,
voices, external samples, or runtime generators. Shared family WAVs are read
only for preservation checks and are never rewritten by this script.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import random
import struct
import sys
import wave

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "exports/audio"
REPORT = ROOT / "reports/WC-350/hero-audio.json"
RATE = 22050
TAU = 2 * math.pi

RECIPES = {
    "wc_u_human_guardian": (.84, .060, .36, "Rounded modal shield chime, restrained metal knock and small low foot placement."),
    "wc_u_human_priest": (1.04, .043, .25, "Soft inharmonic bell pair with a quiet filtered-air arrival; lower target level than damage variants."),
    "wc_u_human_mage": (.72, .062, .38, "Brief rising furnace tone and filtered rush, followed by one soft modal pop; no crackling loop."),
    "wc_u_elf_ranger": (.44, .046, .30, "Soft bow-string snap and short high-frequency leaf-brush sweep; no impact or sustained status sound."),
    "wc_u_elf_priest": (1.12, .048, .30, "Three damped Karplus-Strong string notes, voiced as a restrained chord distinct from healing bells."),
    "wc_u_elf_rogue": (.56, .048, .31, "Dry cloth snap and longer bright magical pitch sweep; no explosive or invisibility cue."),
    "wc_u_dwarf_guardian": (.70, .063, .38, "Low short bell knock over a compact footfall, with no repeated target layers or long reverberation."),
    "wc_u_dwarf_ranger": (.47, .058, .35, "Two dry mechanism clicks, compact bowed thump and short metal accent; no firearm sample or report."),
    "wc_u_dwarf_warrior": (.66, .064, .39, "Broad brushed whoosh followed by one compact stone-grit and metal impact."),
    "wc_u_orc_warrior": (.70, .055, .34, "Two hand-drum-like resonant accents and a restrained synthetic filtered-air exhale; no recorded voice."),
    "wc_u_orc_mage": (1.10, .062, .38, "Low rising filtered wind followed by a short soft three-tone thunder body; no sustained storm loop."),
    "wc_u_orc_rogue": (.36, .043, .29, "Quick brushed wind, short falling pitch envelope and light landing; shorter than Sylas's dash."),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Sound:
    def __init__(self, uid, duration):
        self.samples = [0.0] * round(duration * RATE)
        self.rng = random.Random(int.from_bytes(hashlib.sha256(uid.encode()).digest()[:8], "little"))

    def add(self, start, values):
        offset = round(start * RATE)
        for i, value in enumerate(values):
            if offset + i >= len(self.samples):
                break
            self.samples[offset + i] += value

    def tone(self, start, duration, frequency, gain, decay=6, end_frequency=None,
             attack=.008, partials=((1, 1),)):
        count = round(duration * RATE)
        end = frequency if end_frequency is None else end_frequency
        values = []
        for i in range(count):
            t, u = i / RATE, i / max(1, count - 1)
            phase = TAU * (frequency * t + (end - frequency) * t * t / (2 * duration))
            env = (1 - math.exp(-t / attack)) * math.exp(-decay * t)
            env *= min(1, (1 - u) * duration / .025)
            values.append(gain * env * sum(weight * math.sin(ratio * phase)
                                           for ratio, weight in partials))
        self.add(start, values)

    def brush(self, start, duration, low_hz, high_hz, gain, sweep=1.0, decay=1.5):
        count = round(duration * RATE)
        low, high = 0.0, 0.0
        values = []
        for i in range(count):
            u = i / max(1, count - 1)
            multiplier = 1 + (sweep - 1) * u
            a = 1 - math.exp(-TAU * low_hz * multiplier / RATE)
            b = 1 - math.exp(-TAU * high_hz * multiplier / RATE)
            noise = self.rng.uniform(-1, 1)
            low += a * (noise - low)
            high += b * (noise - high)
            env = math.sin(math.pi * u) ** .65 * math.exp(-decay * u)
            values.append((high - low) * gain * env)
        self.add(start, values)

    def string(self, start, duration, frequency, gain):
        count = round(duration * RATE)
        period = max(2, round(RATE / frequency))
        buffer = [self.rng.uniform(-1, 1) for _ in range(period)]
        values = []
        for i in range(count):
            index = i % period
            value = buffer[index]
            buffer[index] = .496 * (value + buffer[(index + 1) % period])
            t = i / RATE
            edge = min(1, t / .003, (count - 1 - i) / (RATE * .03))
            values.append(gain * value * max(0, edge) * math.exp(-t * 1.5))
        self.add(start, values)


def synthesize(uid):
    duration, target_rms, ceiling, _ = RECIPES[uid]
    s = Sound(uid, duration)
    if uid == "wc_u_human_guardian":
        s.tone(0, .13, 100, .32, 22, 72)
        s.brush(.015, .09, 700, 3400, .36)
        s.tone(.025, .75, 392, .65, 5.8, partials=((1, 1), (2.71, .19), (4.12, .06)))
    elif uid == "wc_u_human_priest":
        s.tone(0, .9, 739.99, .50, 5.2, partials=((1, 1), (2.08, .12), (3.9, .035)))
        s.tone(.105, .87, 987.77, .38, 5.7, partials=((1, 1), (2.07, .10)))
        s.brush(.08, .54, 650, 3100, .12, .8)
    elif uid == "wc_u_human_mage":
        s.tone(0, .24, 170, .30, 1.8, 420, partials=((1, 1), (2, .12)))
        s.brush(0, .27, 140, 1350, .63, 1.6, .4)
        s.tone(.17, .44, 470, .48, 13, 270, partials=((1, 1), (1.47, .15)))
        s.brush(.17, .12, 600, 3300, .40, .6)
    elif uid == "wc_u_elf_ranger":
        s.string(0, .16, 610, .60)
        s.brush(.018, .35, 1200, 6100, .60, .58, .9)
        s.tone(.01, .18, 680, .12, 14, 380)
    elif uid == "wc_u_elf_priest":
        for offset, frequency, gain in ((0, 392, .80), (.025, 493.88, .66), (.05, 587.33, .58)):
            s.string(offset, 1.0, frequency, gain)
        s.tone(.012, .85, 196, .06, 4.7)
    elif uid == "wc_u_elf_rogue":
        s.brush(0, .065, 1400, 6700, .65, .9)
        s.brush(.035, .42, 350, 2400, .55, 1.7, .9)
        s.tone(.025, .32, 480, .20, 3.2, 1250, partials=((1, 1), (1.5, .08)))
        s.tone(.29, .19, 1046.5, .08, 15)
    elif uid == "wc_u_dwarf_guardian":
        s.brush(0, .13, 50, 700, .70, .7)
        s.tone(0, .18, 98, .35, 18, 66)
        s.tone(.024, .61, 164.81, .72, 7.0, partials=((1, 1), (2.73, .30), (4.09, .10)))
    elif uid == "wc_u_dwarf_ranger":
        s.brush(0, .035, 2100, 7300, .55)
        s.brush(.032, .025, 2400, 7100, .38)
        s.tone(.044, .19, 140, .56, 17, 85, partials=((1, 1), (3, .09)))
        s.tone(.051, .33, 932.33, .21, 15, partials=((1, 1), (2.67, .19)))
    elif uid == "wc_u_dwarf_warrior":
        s.brush(0, .25, 180, 1700, .70, 1.8, .2)
        s.brush(.15, .13, 75, 2100, .90, .6)
        s.tone(.15, .41, 311.13, .51, 12, partials=((1, 1), (2.57, .23), (4.21, .08)))
        s.tone(.15, .18, 104, .34, 22, 76)
    elif uid == "wc_u_orc_warrior":
        s.tone(0, .25, 170, .56, 12, 90, partials=((1, 1), (1.59, .15)))
        s.tone(.16, .24, 185, .42, 14, 100, partials=((1, 1), (1.61, .16)))
        s.brush(.065, .47, 170, 1500, .42, .66, .6)
    elif uid == "wc_u_orc_mage":
        s.brush(0, .40, 65, 600, .85, 2.3, .0)
        for frequency, gain in ((110, .41), (146.83, .28), (196, .22)):
            s.tone(.24, .73, frequency, gain, 5.4, frequency * .94, attack=.018)
        s.brush(.25, .46, 45, 1200, .35, .65, 1.5)
    elif uid == "wc_u_orc_rogue":
        s.brush(0, .205, 600, 3500, .65, .52, .5)
        s.tone(.012, .15, 620, .10, 8, 250)
        s.tone(.18, .12, 125, .30, 24, 78)
        s.brush(.18, .075, 180, 1500, .26)
    else:
        raise ValueError("Unmapped alpha hero: " + uid)
    # Fade edges and remove DC before a single linear gain; never hard-clip a cue.
    values = s.samples
    mean = sum(values) / len(values)
    values = [(v - mean) * min(1, i / (RATE * .004), (len(values) - 1 - i) / (RATE * .025))
              for i, v in enumerate(values)]
    rms = math.sqrt(sum(v * v for v in values) / len(values))
    peak = max(abs(v) for v in values)
    gain = min(target_rms / max(rms, 1e-12), ceiling / max(peak, 1e-12))
    pcm = [round(v * gain * 32767) for v in values]
    if any(abs(v) >= 32767 for v in pcm):
        raise RuntimeError("Unexpected clipping: " + uid)
    return struct.pack("<" + "h" * len(pcm), *pcm)


def measure(path):
    with wave.open(str(path), "rb") as stream:
        frames = stream.getnframes()
        if stream.getnchannels() != 1 or stream.getsampwidth() != 2 or stream.getframerate() != RATE:
            raise RuntimeError("Unexpected PCM format")
        pcm = struct.unpack("<" + "h" * frames, stream.readframes(frames))
    peak = max(abs(v) for v in pcm) / 32768
    rms = math.sqrt(sum((v / 32768) ** 2 for v in pcm) / frames)
    return {"duration_seconds": frames / RATE, "sample_rate": RATE, "channels": 1,
            "sample_width_bits": 16, "peak_dbfs": 20 * math.log10(max(peak, 1e-12)),
            "rms_dbfs": 20 * math.log10(max(rms, 1e-12)), "peak_linear": peak,
            "rms_linear": rms, "dc_mean": sum(pcm) / frames / 32768,
            "clipped_samples": sum(abs(v) >= 32767 for v in pcm),
            "first_sample": pcm[0], "last_sample": pcm[-1], "frames": frames}


def main():
    units_path, rules_path = ROOT / "data/units.json", ROOT / "data/rules.alpha.json"
    units = {u["id"]: u for u in json.loads(units_path.read_text(encoding="utf-8"))["units"]}
    alpha = json.loads(rules_path.read_text(encoding="utf-8"))["alpha_unit_ids"]
    if len(alpha) != 12 or set(alpha) != set(RECIPES):
        raise RuntimeError("Recipes must match the exact canonical alpha roster")
    expected_names = {"S_WC_" + uid + "_active.wav" for uid in alpha}
    protected = {p.name: digest(p) for p in OUT.glob("*.wav") if p.name not in expected_names}
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    result = {"status": "STARTED", "generated_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "generator": "tools/audio/hero_variants.py",
              "generator_sha256": digest(Path(__file__)), "units_sha256": digest(units_path),
              "rules_sha256": digest(rules_path), "external_samples": False, "recorded_voices": False,
              "generation": "Original deterministic additive/modal, filtered-noise and Karplus-Strong synthesis",
              "seed": "First eight SHA256 bytes of unit id interpreted little-endian",
              "measurement_boundary": "PCM duration/RMS/peak/DC/clipping, not perceptual loudness or final mix acceptance",
              "runtime_playback": "One active variant per confirmed observed action; use runtime voice limits and effects volume",
              "unreal_import": "NOT_RUN", "listening_review": "NOT_RUN", "records": []}
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for uid in alpha:
        unit = units[uid]
        dossier = ROOT / "docs/heroes" / (uid + ".md")
        cue = unit["art"]["audio"]
        if "**Sound:** " + cue not in dossier.read_text(encoding="utf-8"):
            raise RuntimeError("Dossier/canonical audio cue mismatch: " + uid)
        filename = "S_WC_" + uid + "_active.wav"
        path = OUT / filename
        pcm = synthesize(uid)
        if pcm != synthesize(uid):
            raise RuntimeError("Nondeterministic synthesis: " + uid)
        with wave.open(str(path), "wb") as stream:
            stream.setparams((1, 2, RATE, len(pcm) // 2, "NONE", "not compressed"))
            stream.writeframes(pcm)
        metrics = measure(path)
        if metrics["clipped_samples"] or metrics["first_sample"] or metrics["last_sample"]:
            raise RuntimeError("Clip/edge validation failed: " + uid)
        if not (.25 <= metrics["duration_seconds"] <= 1.5 and .005 < metrics["rms_linear"] < .1):
            raise RuntimeError("Duration or level outside intended small-cue limits: " + uid)
        result["records"].append({"unit_id": uid, "name": unit["name"], "ability": unit["ability"]["name"],
                                  "dossier": str(dossier.relative_to(ROOT)), "dossier_sha256": digest(dossier),
                                  "authored_sound_cue": cue, "synthesis_mapping": RECIPES[uid][3],
                                  "file": str(path.relative_to(ROOT)), "sha256": digest(path), **metrics})
    after = {p.name: digest(p) for p in OUT.glob("*.wav") if p.name not in expected_names}
    if protected != after:
        raise RuntimeError("Existing shared audio changed while variants were generated")
    if len({record["sha256"] for record in result["records"]}) != 12:
        raise RuntimeError("Variant files are not distinct")
    result["shared_wavs_preserved"] = protected
    result["checks"] = {"exact_alpha_12": True, "deterministic_pcm_repeated": True,
                        "distinct_sha256": True, "zero_clipped_samples": True,
                        "zero_edge_samples": True, "shared_wavs_unchanged": True}
    result["status"] = "GENERATED_AND_PCM_CHECKED"
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("WC_HERO_AUDIO_PCM_PASS " + json.dumps({"variants": len(alpha), "preserved_shared_wavs": len(protected),
          "clipped_samples": sum(r["clipped_samples"] for r in result["records"]),
          "duration_range": [min(r["duration_seconds"] for r in result["records"]), max(r["duration_seconds"] for r in result["records"])],
          "report": str(REPORT)}))


if __name__ == "__main__":
    main()
