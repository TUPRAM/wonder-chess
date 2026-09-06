"""Original offline synthesized fantasy alpha audio; no samples or external media."""
from pathlib import Path
import math
import random
import struct
import wave
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'exports/audio'
RATE = 22050
TAU = 2 * math.pi

def save(name, samples):
    peak = max(.8, max(abs(x) for x in samples))
    with wave.open(str(OUT / (name + '.wav')), 'wb') as stream:
        stream.setparams((1, 2, RATE, len(samples), 'NONE', 'not compressed'))
        stream.writeframes(b''.join(struct.pack('<h', int(max(-1,min(1,x / peak)) * 25000)) for x in samples))

def chime(notes, duration=1.1, metallic=False):
    values = [0.0] * int(duration * RATE)
    for j, note in enumerate(notes):
        offset = int(j * .09 * RATE)
        for i in range(offset,len(values)):
            t = (i-offset)/RATE
            a = (1-math.exp(-t*150))*math.exp(-t*5)
            values[i] += a*.30*(math.sin(TAU*note*t)+.25*math.sin(TAU*note*(2.71 if metallic else 2)*t)+.11*math.sin(TAU*note*4*t))
    return values

def effect(name, length, tone, noise, sweep):
    rng = random.Random(name)
    result=[]; low=0.0
    for i in range(int(length*RATE)):
        t=i/RATE; u=t/length
        low=.78*low+.22*rng.uniform(-1,1)
        envelope=math.sin(math.pi*u)**.7 * math.exp(-3*u)
        result.append(envelope*(noise*low + tone*math.sin(TAU*(180*t+sweep*t*t))))
    return result

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    chords = {'buy':[523.25,659.25],'sell':[493.88,392],'merge':[523.25,659.25,783.99,1046.5],
              'reroll':[392,523.25,440],'ready':[392,587.33],'phase':[293.66,392,587.33],
              'health_loss':[196,185],'victory':[392,493.88,587.33,783.99],'draw':[349.23,392],
              'defeat':[329.63,293.66,196],'shield':[392,783.99],'heal':[659.25,783.99,987.77],
              'stun':[277.18,293.66]}
    for name,notes in chords.items(): save('S_WC_'+name,chime(notes,1.8 if name in ('victory','defeat','merge') else 1.1,name=='shield'))
    for name,args in {'movement':(.13,.05,.6,-50),'melee':(.25,.5,1.8,-220),'ranged_launch':(.24,.08,1.6,300),'ranged_impact':(.18,.35,1,-300),'magic_impact':(.65,.45,.65,550),'dash':(.4,.1,1.6,800)}.items():
        save('S_WC_'+name,effect(name,*args))
    length=24; music=[0.0]*(RATE*length)
    # Six-bar D Dorian harp melody with slow bowed harmonics and a seamless taper.
    progression=[(146.83,220,293.66),(174.61,261.63,349.23),(130.81,196,261.63),(146.83,220,293.66)]
    for i in range(len(music)):
        t=i/RATE; chord=progression[int(t//6)%4]
        fade=min(1,t/1.5,(length-t)/1.5)
        pad=sum(math.sin(TAU*f*t)*.028+math.sin(TAU*f*2*t)*.006 for f in chord)
        note=chord[int(t*2)%3]*2; local=t%0.5
        harp=.1*math.exp(-local*8)*math.sin(TAU*note*local)*(1-math.exp(-local*150))
        music[i]=fade*(pad+harp)
    save('S_WC_courtyard',music)
    (OUT/'provenance.json').write_text(json.dumps({'source':'Original mathematical synthesis authored for Wonder Chess','external_samples':False,'sample_rate':RATE,'review':'Generated; in-game mix/listening review still required','files':sorted(p.name for p in OUT.glob('*.wav'))},indent=2)+'\n')
    print(f'Created {len(list(OUT.glob("*.wav")))} original WAV files')

if __name__=='__main__':main()
