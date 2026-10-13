"""Local source evidence checks. No editor, network, service jobs or asset mutation.

OBJ inspection is geometry-only. GLB inspection supports ordinary embedded glTF
accessors; compressed geometry is explicitly unsupported, never silently passed.
"""
import argparse
import hashlib
import json
import math
import struct
import sys
import wave
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def confined(root, relative):
    root = Path(root).resolve()
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('Expected a nonempty relative path')
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Path escapes the bundle root')
    return path


def fingerprint(path, root):
    path = Path(path)
    return {'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha256(path)}


def verify_manifest(root, manifest):
    errors = []
    entries = manifest.get('files', [])
    if not entries:
        return ['Manifest contains no files']
    seen = set()
    for item in entries:
        try:
            path = confined(root, item.get('path'))
            if item['path'] in seen:
                errors.append('Duplicate manifest path: ' + item['path'])
            seen.add(item['path'])
            if not path.is_file():
                errors.append('Missing file: ' + item['path']); continue
            if path.stat().st_size != item.get('bytes') or sha256(path) != item.get('sha256'):
                errors.append('Stale or damaged bytes: ' + item['path'])
            with path.open('rb') as stream:
                pointer_header = stream.read(64)
            if pointer_header.startswith(b'version https://git-lfs.github.com/spec/'):
                errors.append('Unhydrated Git LFS pointer: ' + item['path'])
        except (OSError, ValueError, KeyError, TypeError) as e:
            errors.append(str(e))
    return errors


def geometry_metrics(vertices, triangles, uv_faces=None):
    if not vertices or not triangles:
        raise ValueError('No inspectable triangle geometry')
    if any(len(v) != 3 for v in vertices):
        raise ValueError('Vertex position must have three coordinates')
    if any(not all(math.isfinite(x) for x in v) for v in vertices):
        raise ValueError('Non-finite vertex position')
    bad, degenerate, edges = 0, 0, {}
    for tri in triangles:
        if len(tri) != 3 or any(i < 0 or i >= len(vertices) for i in tri):
            bad += 1; continue
        a, b, c = [vertices[i] for i in tri]
        v, w = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        cross = [v[1]*w[2]-v[2]*w[1], v[2]*w[0]-v[0]*w[2], v[0]*w[1]-v[1]*w[0]]
        degenerate += sum(x*x for x in cross) < 1e-20
        for i, j in ((tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])):
            k = tuple(sorted((i,j))); edges[k] = edges.get(k,0)+1
    lo = [min(v[i] for v in vertices) for i in range(3)]
    hi = [max(v[i] for v in vertices) for i in range(3)]
    return {'vertices': len(vertices), 'triangles': len(triangles), 'bounds_min': lo, 'bounds_max': hi,
            'dimensions': [hi[i]-lo[i] for i in range(3)], 'invalid_triangles': bad,
            'degenerate_triangles': degenerate, 'boundary_edges': sum(n==1 for n in edges.values()),
            'nonmanifold_edges': sum(n>2 for n in edges.values()),
            'triangles_missing_uv': None if uv_faces is None else sum(not x for x in uv_faces),
            'limits': ['Edges are indexed, not position-welded; seams can appear as boundaries.',
                       'Boundary edges need construction review: an intended opening is not automatically a defect.',
                       'These measurements do not prove topology, skin quality, silhouette or UV overlap quality.']}


def inspect_obj(path):
    vertices, triangles, uvfaces, texcoords = [], [], [], []
    def index(s, count):
        n = int(s); return n - 1 if n > 0 else count + n
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        p = line.split('#',1)[0].split()
        if not p: continue
        if p[0] == 'v':
            if len(p) < 4: raise ValueError('Incomplete OBJ vertex')
            vertices.append(tuple(map(float,p[1:4])))
        elif p[0] == 'vt': texcoords.append(tuple(map(float,p[1:3])))
        elif p[0] == 'f':
            corners = [x.split('/') for x in p[1:]]
            ids = [index(x[0],len(vertices)) for x in corners]
            gooduv = all(len(x)>1 and x[1] and 0 <= index(x[1],len(texcoords)) < len(texcoords) for x in corners)
            for i in range(1,len(ids)-1):
                triangles.append((ids[0],ids[i],ids[i+1])); uvfaces.append(bool(gooduv))
    result = geometry_metrics(vertices, triangles, uvfaces)
    result.update({'format':'obj','unit':'unspecified_by_format','uv_coordinates':len(texcoords)})
    return result


def inspect_glb(path):
    data = Path(path).read_bytes()
    magic, version, length = struct.unpack_from('<III', data)
    if magic != 0x46546C67 or version != 2 or length != len(data):
        raise ValueError('Invalid GLB 2 header or length')
    chunks, offset = {}, 12
    while offset < length:
        size, kind = struct.unpack_from('<II', data, offset); offset += 8
        if offset + size > length: raise ValueError('Truncated GLB chunk')
        chunks[kind] = data[offset:offset+size]; offset += size
    doc = json.loads(chunks[0x4E4F534A]); blob = chunks.get(0x004E4942,b'')
    def accessor(i):
        a = doc['accessors'][i]
        if 'sparse' in a or 'bufferView' not in a: raise ValueError('Sparse/missing buffer accessor requires a qualified decoder')
        view = doc['bufferViews'][a['bufferView']]
        if view.get('buffer',0) != 0: raise ValueError('External buffer is not supported')
        if view.get('extensions'): raise ValueError('Compressed/extended buffer requires a qualified decoder')
        code = {5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}[a['componentType']]
        n = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
        fmt = '<'+code*n; size = struct.calcsize(fmt); stride = view.get('byteStride',size)
        if stride < size: raise ValueError('Accessor stride is smaller than element')
        start = view.get('byteOffset',0)+a.get('byteOffset',0)
        if a['count'] and start+(a['count']-1)*stride+size > view.get('byteOffset',0)+view['byteLength']:
            raise ValueError('Accessor exceeds buffer view')
        return [struct.unpack_from(fmt,blob,start+j*stride) for j in range(a['count'])]
    vertices, triangles, uvfaces, primitives = [], [], [], []
    for mesh in doc.get('meshes',[]):
        for p in mesh['primitives']:
            if p.get('extensions') or p.get('mode',4) != 4:
                raise ValueError('Compressed or non-triangle primitive requires editor inspection')
            attrs = p['attributes']; vs = accessor(attrs['POSITION']); base = len(vertices)
            vertices.extend(vs)
            ids = [a[0] for a in accessor(p['indices'])] if 'indices' in p else list(range(len(vs)))
            if len(ids)%3: raise ValueError('Incomplete triangle')
            tris = [tuple(base+x for x in ids[i:i+3]) for i in range(0,len(ids),3)]
            triangles.extend(tris)
            valid_uv = 'TEXCOORD_0' in attrs and len(accessor(attrs['TEXCOORD_0'])) == len(vs)
            uvfaces.extend([valid_uv]*len(tris)); primitives.append({'material':p.get('material'),'attributes':list(attrs)})
    result = geometry_metrics(vertices,triangles,uvfaces)
    result.update({'format':'glb','unit':'meters_in_local_mesh_coordinates', 'materials':len(doc.get('materials',[])),
                   'skins':len(doc.get('skins',[])), 'animations':len(doc.get('animations',[])), 'primitives':primitives,
                   'node_transforms_present':any(any(k in n for k in ('matrix','translation','scale','rotation')) for n in doc.get('nodes',[]))})
    result['limits'].append('Bounds are local mesh coordinates; node transforms/instances require the Unreal world-scale check.')
    return result


def inspect(path):
    path = Path(path); ext = path.suffix.lower()
    if ext == '.obj': result = inspect_obj(path)
    elif ext == '.glb': result = inspect_glb(path)
    elif ext == '.wav':
        with wave.open(str(path),'rb') as w:
            result = {'format':'wav','sample_rate':w.getframerate(),'channels':w.getnchannels(),
                      'sample_width_bytes':w.getsampwidth(),'frames':w.getnframes(),
                      'duration_seconds':w.getnframes()/w.getframerate()}
    elif ext in ('.png','.jpg','.jpeg','.webp','.tif','.tiff'):
        from PIL import Image
        with Image.open(path) as im:
            im.load(); result={'format':im.format,'size':list(im.size),'mode':im.mode,'icc_present':bool(im.info.get('icc_profile'))}
    else: raise ValueError('No qualified content inspector for '+ext)
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':sha256(path),'measurements':result}


def source_preflight(root, contract):
    errors = verify_manifest(root,contract.get('manifest',{})); measurements = []
    sources = contract.get('inspect',[])
    if not sources: errors.append('No source inspection specified')
    for req in sources:
        try:
            result = inspect(confined(root,req['path'])); measurements.append(result); m=result['measurements']
            for field, maximum in req.get('maximum',{}).items():
                if maximum is None or field not in m or m[field] is None or m[field] > maximum:
                    errors.append(req['path']+': failed maximum '+field)
            for field, expected in req.get('equals',{}).items():
                if expected is None or m.get(field) != expected: errors.append(req['path']+': unexpected '+field)
        except (ValueError,OSError,KeyError,TypeError,IndexError,struct.error) as e: errors.append(str(e))
    return {'status':'fail' if errors else 'pass','errors':errors,'measurements':measurements,
            'scope':'source_bytes_and_declared_numeric_constraints_only','human_acceptance':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('inspect'); p.add_argument('path',type=Path)
    p=sub.add_parser('seal'); p.add_argument('root',type=Path); p.add_argument('--output',required=True,type=Path)
    for name in ('verify','preflight'):
        p=sub.add_parser(name); p.add_argument('root',type=Path); p.add_argument('record',type=Path)
    args=parser.parse_args()
    try:
        if args.command=='inspect': result=inspect(args.path)
        elif args.command=='seal':
            root=args.root.resolve()
            files=[p for p in sorted(root.rglob('*')) if p.is_file() and p.resolve()!=args.output.resolve()]
            if any('.git' in p.relative_to(root).parts for p in files): raise ValueError('Seal an explicit delivery bundle, not a Git checkout')
            for path in files:
                confined(root, path.relative_to(root).as_posix())
            result={'schema_version':1,'files':[fingerprint(p,root) for p in files]}
            args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        elif args.command=='verify':
            errors=verify_manifest(args.root,json.loads(args.record.read_text(encoding='utf-8-sig')))
            result={'status':'fail' if errors else 'pass','errors':errors}
        else: result=source_preflight(args.root,json.loads(args.record.read_text(encoding='utf-8-sig')))
        print(json.dumps(result,indent=2)); return int(result.get('status')=='fail')
    except (ValueError,OSError,KeyError,TypeError,IndexError,struct.error) as e:
        print(json.dumps({'status':'fail','errors':[str(e)]})); return 1


if __name__=='__main__': sys.exit(main())
