"""Original offline 24-hero and seven-neutral cues with preserved legacy PCM.

No recorded samples, downloaded media, runtime synthesizer, or voice service.
Mechanical checks do not certify listening quality or the packaged mix.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import wave

from hero_variants import Sound, RATE, digest, measure, synthesize as legacy_synthesize, RECIPES as LEGACY

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'exports/audio'
NEW={
 'wc_u_human_warrior':(.48,.056,.36,'One narrow brush, a compact steel modal contact; no splash or second strike.'),
 'wc_u_elf_mage':(.80,.043,.30,'Pale two-part star chime resolving once for the ordered damage and stun payload.'),
 'wc_u_dwarf_priest':(.93,.041,.28,'Warm amber bell cluster, one quiet aggregate arrival for all healed recipients.'),
 'wc_u_orc_guardian':(.85,.045,.31,'Low shared ward chime with a subdued wooden support knock.'),
 'wc_u_halfling_warrior':(.59,.048,.32,'Dry orchard-wood knock with one small warm protection chime.'),
 'wc_u_halfling_ranger':(.65,.042,.29,'Descending two-note tempo arrival; no poison, freezing or movement cue.'),
 'wc_u_halfling_rogue':(.43,.048,.31,'Two short baton taps and a compact golden control accent, without a dash.'),
 'wc_u_halfling_mage':(.53,.044,.31,'A brief rising whistle and soft low mist pop; no sustained cloud.'),
 'wc_u_dragonkin_guardian':(1.02,.044,.31,'A low resonant modal shield chime with no roar or immunity fanfare.'),
 'wc_u_dragonkin_ranger':(.58,.047,.32,'Taut synthetic string release and narrow cyan prism contact.'),
 'wc_u_dragonkin_rogue':(.41,.045,.30,'A small dry crescent sweep with a white-violet inharmonic edge.'),
 'wc_u_dragonkin_priest':(.98,.042,.29,'An open-voiced low gold hexagonal ward chime, distinct from healing bells.'),
}


def finish(sound,target,ceiling):
    samples=sound.samples
    mean=sum(samples)/len(samples)
    samples=[(v-mean)*max(0,min(1,i/(RATE*.004),(len(samples)-1-i)/(RATE*.025))) for i,v in enumerate(samples)]
    rms=math.sqrt(sum(v*v for v in samples)/len(samples));peak=max(abs(v) for v in samples)
    gain=min(target/max(rms,1e-12),ceiling/max(peak,1e-12))
    pcm=[round(v*gain*32767) for v in samples]
    return struct.pack('<'+'h'*len(pcm),*pcm)


def hero_pcm(uid):
    if uid in LEGACY:return legacy_synthesize(uid)
    duration,target,ceiling,_=NEW[uid]
    s=Sound(uid,duration)
    if uid=='wc_u_human_warrior':
        s.brush(0,.20,260,2300,.62,1.45,.2)
        s.tone(.10,.31,369.99,.55,15,partials=((1,1),(2.63,.18),(4.11,.04)))
        s.tone(.105,.14,110,.17,22,78)
    elif uid=='wc_u_elf_mage':
        s.tone(0,.20,540,.19,2.5,810)
        s.tone(.08,.65,830.61,.54,7.8,partials=((1,1),(2.03,.11)))
        s.tone(.10,.61,554.37,.30,8.2,partials=((1,1),(2.72,.08)))
        s.brush(.07,.15,1100,4200,.13,.7)
    elif uid=='wc_u_dwarf_priest':
        for delay,freq,gain in [(0,329.63,.44),(.035,415.30,.33),(.07,493.88,.25)]:
            s.tone(delay,.80,freq,gain,5.4,partials=((1,1),(2.02,.10),(3.97,.03)))
        s.brush(.035,.28,300,1300,.11,.8)
    elif uid=='wc_u_orc_guardian':
        s.tone(0,.15,88,.23,18,72)
        s.tone(.02,.76,246.94,.55,6,partials=((1,1),(2.71,.18),(4.04,.035)))
        s.tone(.055,.67,369.99,.18,6.6)
        s.brush(0,.08,130,800,.20)
    elif uid=='wc_u_halfling_warrior':
        s.brush(0,.075,120,1600,.48,.6)
        s.tone(0,.13,180,.42,21,100)
        s.tone(.07,.45,523.25,.40,8,partials=((1,1),(2.69,.13)))
    elif uid=='wc_u_halfling_ranger':
        s.string(0,.17,740,.15)
        s.tone(.025,.36,659.25,.46,8,partials=((1,1),(2.01,.08)))
        s.tone(.17,.42,440,.50,8,partials=((1,1),(2.01,.08)))
    elif uid=='wc_u_halfling_rogue':
        for delay,frequency,gain in [(0,300,.5),(.085,380,.4)]:
            s.tone(delay,.14,frequency,gain,22,frequency*.73)
            s.brush(delay,.04,550,2400,.22)
        s.tone(.11,.27,1174.66,.12,13)
    elif uid=='wc_u_halfling_mage':
        s.tone(0,.25,470,.21,1.8,1050)
        s.brush(.16,.19,180,1600,.48,.55,.6)
        s.tone(.19,.27,196,.42,18,123)
    elif uid=='wc_u_dragonkin_guardian':
        s.tone(0,.95,130.81,.54,4.8,partials=((1,1),(2.72,.26),(4.03,.09)))
        s.tone(.04,.88,261.63,.23,5.3)
        s.brush(.008,.105,170,1400,.21,.9)
    elif uid=='wc_u_dragonkin_ranger':
        s.string(0,.24,554.37,.36)
        s.tone(.03,.40,1108.73,.36,11,880,partials=((1,1),(2.39,.14)))
        s.brush(.035,.28,1400,5400,.37,.66,.9)
    elif uid=='wc_u_dragonkin_rogue':
        s.brush(0,.17,650,3900,.45,1.25,.5)
        s.tone(.045,.30,1046.5,.28,15,830,partials=((1,1),(1.414,.24),(2.23,.055)))
    elif uid=='wc_u_dragonkin_priest':
        for delay,freq,gain in [(0,220,.42),(.045,329.63,.25),(.08,440,.18)]:
            s.tone(delay,.84,freq,gain,5.2,partials=((1,1),(2.71,.15),(4.03,.03)))
        s.brush(.055,.26,240,1100,.10,.8)
    else:raise ValueError('Unmapped 24-hero cue '+uid)
    return finish(s,target,ceiling)


def neutral_pcm(uid,active):
    kind=uid.removeprefix('wc_n_')
    duration=({'wisp':.58,'stoneback':.70,'prowler':.34,'sentinel':.86,'warden':.88}[kind] if active else .25)
    s=Sound(uid+('_active' if active else '_basic'),duration)
    if kind=='sprout':
        s.brush(0,.13,130,1250,.47,.7);s.tone(.02,.19,160,.36,22,105)
    elif kind=='thorn':
        s.string(0,.17,330,.36);s.brush(.015,.20,800,3600,.45,.6)
    elif kind=='wisp':
        s.tone(0,duration-.035,active and 880 or 1174.66,.43,active and 8 or 17,
               partials=((1,1),(2.04,.10),(3.91,.035)))
        s.brush(.025,min(.22,duration-.04),1200,4000,.13,.8)
    elif kind=='stoneback':
        s.tone(0,min(.2,duration-.02),92,.46,18,62)
        s.brush(.005,.13,55,850,.48,.62)
        if active:s.tone(.03,.60,196,.44,7,partials=((1,1),(2.73,.20)))
    elif kind=='prowler':
        s.brush(0,active and .23 or .13,340,2200,.47,active and 1.6 or .72,.6)
        s.tone(active and .20 or .06,.12,125,.35,25,77)
    elif kind=='sentinel':
        s.tone(0,duration-.025,active and 174.61 or 261.63,.57,active and 5.8 or 16,
               partials=((1,1),(2.71,.23),(4.12,.08)))
        s.brush(.006,.085,200,1300,.21,.7)
    elif kind=='warden':
        s.tone(0,duration-.04,active and 146.83 or 587.33,.45,active and 5.5 or 15,
               partials=((1,1),(1.5,.18),(2.76,.11)))
        s.brush(0,min(duration-.03,.24),140,1300,.25,1.55,.6)
        if active:s.tone(.075,.74,440,.17,6.8,partials=((1,1),(2.04,.06)))
    else:raise ValueError('Unmapped neutral cue '+uid)
    return finish(s,.038 if active else .026,.28 if active else .22)


def spectrum(pcm):
    values=struct.unpack('<'+'h'*(len(pcm)//2),pcm)
    crossings=sum((a<0)!=(b<0) for a,b in zip(values,values[1:]))
    # A bounded sampled DFT describes frequency placement, not perceived quality.
    stride=1;sampled=[v/32768 for v in values]
    bins=(110,220,440,880,1760,3520,7040)
    powers=[]
    for frequency in bins:
        phase=2*math.pi*frequency/(RATE/stride)
        real=sum(v*math.cos(phase*i) for i,v in enumerate(sampled))
        imag=sum(v*math.sin(phase*i) for i,v in enumerate(sampled))
        powers.append((real*real+imag*imag)/max(1,len(sampled)**2))
    return {'zero_crossings_per_second':crossings/(len(values)/RATE),
            'sampled_dft_bins_hz':list(bins),'sampled_dft_powers':powers,
            'spectral_limits':'Seven sampled frequency bins only; not loudness, timbre or listening acceptance.'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--report',type=Path)
    args=parser.parse_args()
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report=args.report or ROOT/'reports/WC-U450'/stamp/'audio.json'
    if report.exists():raise RuntimeError('Use a fresh audio evidence path; refusing to overwrite '+str(report))
    report.parent.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    units={u['id']:u for u in json.loads((ROOT/'data/units.json').read_text())['units']}
    rules=json.loads((ROOT/'data/rules.alpha.json').read_text())
    alpha=rules['alpha_unit_ids']
    creatures=json.loads((ROOT/'data/neutrals.json').read_text())['creatures']
    if len(alpha)!=24 or set(alpha)!=set(LEGACY)|set(NEW):raise RuntimeError('24 hero recipes must exactly cover the active profile')
    recipes=[]
    for uid in alpha:recipes.append((uid,'active',units[uid]['display_name'],NEW.get(uid,LEGACY.get(uid))[3],lambda uid=uid:hero_pcm(uid)))
    for creature in creatures:
        uid=creature['id']
        for clip in (['basic','active'] if creature['ability'] else ['basic']):
            recipes.append((uid,clip,creature['display_name'],'Original '+uid.removeprefix('wc_n_')+' '+clip+' mechanical/modal cue',lambda uid=uid,clip=clip:neutral_pcm(uid,clip=='active')))
    expected={'S_WC_'+uid+'_'+clip+'.wav' for uid,clip,*_ in recipes}
    protected={p.name:digest(p) for p in OUT.glob('*.wav') if p.name not in expected}
    original_legacy={uid:digest(OUT/('S_WC_'+uid+'_active.wav')) for uid in LEGACY if (OUT/('S_WC_'+uid+'_active.wav')).exists()}
    result={'status':'STARTED','generated_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
            'schema_version':rules['schema_version'],'balance_version':rules['balance_version'],
            'generator':'tools/audio/update_variants.py','generator_sha256':digest(Path(__file__)),
            'legacy_generator_sha256':digest(Path(__file__).with_name('hero_variants.py')),
            'units_sha256':digest(ROOT/'data/units.json'),'neutrals_sha256':digest(ROOT/'data/neutrals.json'),
            'external_samples':False,'recorded_voices':False,'unreal_import':'NOT_RUN','listening_review':'NOT_RUN',
            'playback_policy':'One active cue per observed combat source/action; AOE and ordered payload share cue. Neutral basic cue at impact. Controller shared concurrency limit applies.',
            'records':[]}
    report.write_text(json.dumps(result,indent=2)+'\n')
    for uid,clip,name,description,render in recipes:
        pcm=render()
        if pcm!=render():raise RuntimeError('Nondeterministic original synthesis: '+uid+'/'+clip)
        path=OUT/('S_WC_'+uid+'_'+clip+'.wav')
        with wave.open(str(path),'wb') as stream:
            stream.setparams((1,2,RATE,len(pcm)//2,'NONE','not compressed'));stream.writeframes(pcm)
        metrics=measure(path)
        if metrics['clipped_samples'] or metrics['first_sample'] or metrics['last_sample']:
            raise RuntimeError('Clipping/nonzero edge: '+str(path))
        if not (.15<=metrics['duration_seconds']<=1.5 and .004<metrics['rms_linear']<.1):
            raise RuntimeError('Unexpected duration/level: '+str(path))
        result['records'].append({'unit_id':uid,'clip':clip,'name':name,'description':description,
            'path':str(path.relative_to(ROOT)),'sha256':digest(path),**metrics,**spectrum(pcm)})
    if protected!={p.name:digest(p) for p in OUT.glob('*.wav') if p.name not in expected}:raise RuntimeError('Protected shared WAV changed')
    if any(digest(OUT/('S_WC_'+uid+'_active.wav'))!=before for uid,before in original_legacy.items()):raise RuntimeError('Legacy hero PCM changed')
    if len({r['sha256'] for r in result['records']})!=36:raise RuntimeError('Expected36 distinct character WAVs')
    result.update(status='GENERATED_AND_PCM_CHECKED',hero_active_count=24,neutral_basic_count=7,neutral_active_count=5,
                  preserved_legacy_hero_count=len(original_legacy),preserved_shared_wavs=protected,
                  checks={'deterministic_pcm_repeated':True,'distinct_sha256':True,'zero_clipping':True,'zero_edges':True,'legacy_pcm_unchanged':True})
    report.write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'update_provenance.json').write_text(json.dumps(result,indent=2)+'\n')
    print('WC_UPDATE_AUDIO_PCM_PASS '+json.dumps({'hero_actives':24,'neutral_basics':7,'neutral_actives':5,'total_wavs':len(list(OUT.glob('*.wav'))),'report':str(report)}))


if __name__=='__main__':main()
