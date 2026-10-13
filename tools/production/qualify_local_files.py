"""Check native tool exports and demonstrate local LFS recovery without a push."""
import io
import json
import os
import shutil
import subprocess
import time
import wave
import zipfile
from pathlib import Path
from PIL import Image, ImageChops
from asset_checks import inspect, sha256

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/'support/tools/pipeline/fixtures'
OUT=ROOT/'reports/pipeline-tools-20260921'


def native_files():
    with zipfile.ZipFile(FIX/'reference-board.kra') as z:
        merged=Image.open(io.BytesIO(z.read('mergedimage.png'))).convert('RGBA')
        xml=z.read('maindoc.xml').decode('utf-8')
    original=Image.open(FIX/'reference-board.png').convert('RGBA')
    diff=ImageChops.difference(original,merged)
    image_result={'dimensions':list(merged.size),'identical_pixels':all(b.getbbox() is None for b in diff.split()),
                  'layers_preserved':all(s in xml for s in ('View markers','Neutral background')),
                  'kra_sha256':sha256(FIX/'reference-board.kra')}
    audio=[]
    for name in ('qualification-tone-48k.wav','audacity-qualification.wav'):
        with wave.open(str(FIX/name),'rb') as w: audio.append(w.readframes(w.getnframes()))
    audio_result=inspect(FIX/'audacity-qualification.wav')
    audio_result['identical_pcm_samples']=audio[0]==audio[1]
    before=inspect(FIX/'cube-centimeters.obj')['measurements']
    after=inspect(FIX/'meshlab-roundtrip.obj')['measurements']
    geometry={k: {'before':before[k],'after':after[k]} for k in
              ('vertices','triangles','dimensions','triangles_missing_uv','degenerate_triangles','nonmanifold_edges')}
    result={'krita':image_result,'audacity':audio_result,'meshlab':geometry}
    result['status']='pass' if image_result['identical_pixels'] and image_result['layers_preserved'] and audio_result['identical_pcm_samples'] and all(x['before']==x['after'] for x in geometry.values()) else 'fail'
    (OUT/'native-file-roundtrips.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def lfs_recovery():
    parent=ROOT/'support/archives'/('lfs-qualification-'+time.strftime('%Y%m%d-%H%M%S'))
    repo=parent/'source'; clone=parent/'restore'; backup=parent/'lfs-object-backup'
    repo.mkdir(parents=True,exist_ok=False)
    def git(args,cwd=repo,env=None):
        r=subprocess.run(['git',*args],cwd=cwd,env=env,capture_output=True,text=True,check=True)
        return r.stdout.strip()
    git(['init']); git(['lfs','install','--local'])
    git(['config','user.name','Wonder Chess local qualification'])
    git(['config','user.email','qualification@localhost.invalid'])
    git(['lfs','track','*.kra'])
    shutil.copy2(FIX/'reference-board.kra',repo/'fixture.kra')
    expected=sha256(repo/'fixture.kra')
    git(['add','.gitattributes','fixture.kra']); git(['commit','-m','Local fixture only: verify LFS recovery'])
    pointer=git(['show','HEAD:fixture.kra'])
    assert pointer.startswith('version https://git-lfs.github.com/spec/v1')
    shutil.copytree(repo/'.git/lfs/objects',backup)
    env=dict(os.environ,GIT_LFS_SKIP_SMUDGE='1')
    git(['clone','--no-local',str(repo),str(clone)],cwd=parent,env=env)
    assert (clone/'fixture.kra').read_text().startswith('version https://git-lfs')
    shutil.copytree(backup,clone/'.git/lfs/objects',dirs_exist_ok=True)
    git(['lfs','checkout'],cwd=clone)
    actual=sha256(clone/'fixture.kra')
    fsck=git(['lfs','fsck'],cwd=clone)
    result={'status':'pass' if actual==expected else 'fail','source_sha256':expected,'restored_sha256':actual,
            'fresh_clone_started_as_pointer':True,'recovered_using_backed_up_lfs_objects':True,'fsck':fsck,
            'remote_upload':False,'scope':'synthetic_native_Krita_fixture_not_complete_project_backup',
            'archive':parent.relative_to(ROOT).as_posix()}
    (OUT/'git-lfs-recovery.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    print(json.dumps({'native':native_files(),'lfs':lfs_recovery()},indent=2))
