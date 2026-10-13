"""Synthesize the courtyard and round sounds as WAV files. Everything is generated from arithmetic here, so the set
carries no third-party recording or licence.

    synthesize_sounds.py            writes art-source/audio/synth_r001/*.wav

Candidate placeholder audio; a sound designer would replace it.
"""
import math
import random
import struct
import wave
from pathlib import Path

RATE = 44100
OUT = Path(__file__).resolve().parents[2] / "art-source/audio/synth_r001"


def save(name, samples, gain=0.85):
    peak = max(1e-9, max(abs(s) for s in samples))
    data = b"".join(struct.pack("<h", int(max(-1, min(1, s / peak * gain)) * 32767)) for s in samples)
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(data)


def tone(freq, seconds, harmonics=((1, 1.0),), attack=0.02, release=0.2, vibrato=0.0):
    count = int(seconds * RATE)
    out = []
    for i in range(count):
        t = i / RATE
        envelope = min(1, t / attack) * min(1, (seconds - t) / release)
        wobble = 1 + vibrato * math.sin(2 * math.pi * 5.5 * t)
        out.append(envelope * sum(level * math.sin(2 * math.pi * freq * mult * wobble * t) for mult, level in harmonics))
    return out


def mix(*tracks):
    length = max(len(track) for track in tracks)
    return [sum(track[i] for track in tracks if i < len(track)) for i in range(length)]


def after(track, seconds):
    return [0.0] * int(seconds * RATE) + track


def lowpass(samples, strength):
    out, value = [], 0.0
    for sample in samples:
        value += (sample - value) * strength
        out.append(value)
    return out


def noise(seconds, rng):
    return [rng.uniform(-1, 1) for _ in range(int(seconds * RATE))]


def loopable(samples, fade=0.25):
    """Cross-fade the tail into the head so the file repeats without a click."""
    n = int(fade * RATE)
    body = samples[:-n]
    for i in range(n):
        k = i / n
        body[i] = body[i] * k + samples[len(samples) - n + i] * (1 - k)
    return body


def main():
    rng = random.Random(20261003)
    brass = ((1, 1.0), (2, 0.55), (3, 0.38), (4, 0.2), (5, 0.12))
    # War horn: two rising notes.
    save("horn_fight", mix(tone(146.8, 0.9, brass, 0.08, 0.3, 0.004), after(tone(196.0, 1.5, brass, 0.08, 0.7, 0.006), 0.75)))
    # Monster round: one low, rougher call.
    save("horn_monster", mix(tone(98.0, 2.0, brass, 0.15, 0.9, 0.012), tone(103.0, 2.0, brass, 0.15, 0.9, 0.01)))
    bell = ((1, 1.0), (2.76, 0.45), (5.4, 0.25), (8.9, 0.12))
    # Victory: a bright rising three-note figure. Defeat: a falling minor pair.
    save("victory", mix(tone(392.0, 0.5, brass, 0.02, 0.3), after(tone(523.3, 0.5, brass, 0.02, 0.3), 0.22), after(tone(659.3, 1.2, brass, 0.02, 0.8), 0.44)))
    save("defeat", mix(tone(220.0, 0.9, brass, 0.03, 0.5), after(tone(174.6, 1.6, brass, 0.03, 1.1), 0.55)))
    # Coin: two quick metallic pings.
    save("coin", mix(tone(1760, 0.18, bell, 0.002, 0.16), after(tone(2349, 0.32, bell, 0.002, 0.3), 0.07)), 0.6)
    # A piece set down on stone: a short low knock with a little grit.
    knock = tone(92, 0.16, ((1, 1.0), (2.1, 0.4)), 0.002, 0.14)
    grit = lowpass(noise(0.07, rng), 0.25)
    save("place", mix(knock, [g * 0.5 * (1 - i / len(grit)) for i, g in enumerate(grit)]), 0.7)
    thud = tone(140, 0.12, ((1, 1.0), (1.9, 0.5)), 0.002, 0.1)
    clack = lowpass(noise(0.05, rng), 0.45)
    save("hit", mix(thud, [c * 0.8 * (1 - i / len(clack)) for i, c in enumerate(clack)]), 0.6)
    save("skill", mix(tone(659.3, 0.5, bell, 0.005, 0.45), after(tone(987.8, 0.6, bell, 0.005, 0.55), 0.06)), 0.55)
    save("fall", mix(tone(70, 0.4, ((1, 1.0), (2.3, 0.3)), 0.004, 0.35), [g * 0.4 for g in lowpass(noise(0.25, rng), 0.12)]), 0.7)
    save("reroll", mix(*[after(tone(1200 + step * 180, 0.07, bell, 0.002, 0.06), step * 0.045) for step in range(5)]), 0.5)
    save("levelup", mix(*[after(tone(freq, 0.5, brass, 0.01, 0.4), index * 0.12) for index, freq in enumerate((392.0, 493.9, 587.3, 784.0))]), 0.7)
    # Fire: soft low roar with random crackles, loopable.
    roar = lowpass(noise(6.0, rng), 0.03)
    crackle = [0.0] * len(roar)
    for _ in range(70):
        at = rng.randrange(0, len(roar) - 600)
        strength = rng.uniform(0.3, 1.0)
        for i in range(rng.randrange(40, 400)):
            crackle[at + i] += strength * rng.uniform(-1, 1) * math.exp(-i / 60)
    save("fire_loop", loopable(mix([r * 3 for r in roar], [c * 0.35 for c in crackle])), 0.5)
    # Wind: slow swelling filtered noise, loopable.
    wind = lowpass(lowpass(noise(8.0, rng), 0.02), 0.05)
    save("wind_loop", loopable([w * (0.6 + 0.4 * math.sin(2 * math.pi * i / RATE / 4.0)) for i, w in enumerate(wind)]), 0.45)
    print("wrote", len(list(OUT.glob("*.wav"))), "files to", OUT)


if __name__ == "__main__":
    main()
