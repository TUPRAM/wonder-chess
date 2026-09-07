# Ada costume roundtrip drill — Blender executed, Unreal pending

The historical `import-ada-revision2.json` establishes an imported mesh and seven clips. `ada-revision3-import.log` records successful atomic reimports. Neither includes a before/after placed-actor reference check and cold reload. Those imports also predate the subsequently fixed centimeter normalization and stored animation rotation settings. They therefore do not close the current ART-04 costume-change requirement.

`tools/blender/prepare_ada_costume_roundtrip.py` prepares an isolated source-copy drill. It copies the current Ada source into this report directory, duplicates the existing left gold chest fastener into a larger central breastplate medallion, and exports baseline/changed skeletal FBXs using the measured centimeter-copy helper. It preserves all production source/export files by SHA-256. The change reuses the original gold material atlas, UVs and `spine_03` skin weights. The medallion's back touches the breastplate front in the reference pose.

Actual Blender5.1.1 execution passed with exit0. The measured source delta is40 vertices and76 triangles:2517→2557 vertices and4760→4836 triangles. Assertions confirmed unchanged global bounds, existing vertices/UVs/weights, material slots, 27-bone rest hierarchy and seven animation actions. Unreal wedge-vertex counts may differ from source vertices; a positive same-asset imported vertex-count change is still measurable.

Executed outputs:

- `source-baseline.blend`: exact byte copy of the current production source.
- `source-changed.blend`: isolated edited source.
- `baseline/SK_wc_u_human_guardian.fbx`: normalized baseline mesh.
- `changed/SK_wc_u_human_guardian.fbx`: normalized changed mesh.
- `source-change-manifest.json`: source/export hashes, geometry before/after, invariant hashes and production byte-preservation result.

The parent released the measurement window after the normal-speed match reached results. This command then executed from the workspace root:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' --background --python 'tools/blender/prepare_ada_costume_roundtrip.py'
```

The toolchain lane will then duplicate Ada into an isolated Unreal verification package, import the baseline, create seven animation-reference actors in a verification map, reimport the changed costume into the same duplicate asset, and cold-load the results. Production skeleton, materials, animations, mesh, map and packaged artifacts remain protected. A Blender export alone does not complete ART-04, and this drill is not a production costume revision.

Current validation: Python AST syntax passed; Blender source-copy/export executed successfully; all source geometry/invariant assertions passed; production source/exports remained byte-identical. The read-only preview script also completed with exit0 and both generated768×768 images were visually opened. `baseline-breastplate.png` and `changed-breastplate.png` visibly differ by the small central gold medallion. This reference-pose front view shows a flush attachment without obscuring the original costume or equipment. It does not certify the added detail throughout animation.

Unreal reimport/reference checks and cold reload are owned by the toolchain lane and remain separate from this source result. `source-change-manifest.json` is stable at SHA-256 `9d7cab1003ad46f70bfaef9425f0fef15991e2fb288c526de811b0e057d7c0ca`. Blender exit files and full execution logs are retained. No failed source execution occurred in this drill.
