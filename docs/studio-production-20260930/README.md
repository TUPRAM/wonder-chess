# Wonder Chess studio production review

Prepared 30 September 2026, Asia/Shanghai. These are **proposed planning artifacts**, not installed or qualified new skills. The report audits actual local evidence and existing definitions; it preserves the adopted product and art routes.

- [Complete ordered report](REPORT.md)
- [Machine-readable catalogue: 28 existing + 16 proposed responsibilities](skill-catalogue.json)
- [Local evidence snapshot and tool observations](current-state.json)
- [External primary-source register](sources.json)
- [Static browser preview](../../web/studio-production/index.html)

The preview publishes report text/metadata only. Local production paths are marked `[local]`; originals, private art, provider account files, game binaries and support archives are not uploaded. Existing unpublished game work remains outside this report commit. Technical study passes, visual/listening reviews, human acceptance and release status are distinct.

## Rebuild the static preview

Use Node with the qualified `marked` 17.0.5 renderer already supplied by the workspace runtime. No tool installation is required in this session:

```powershell
& '<Node executable>' tools/studio/build_preview.mjs --marked-dir '<directory containing marked/package.json>'
```

The generator assembles REPORT.md and skill-catalogue.json, copies the explicitly allowlisted downloads and generates the preview/build hash manifest. It reads no art or account files. Future maintainers can supply the same pinned renderer in another environment; rendering code is separate from the production-skill proposals.

Vercel project root is `web/studio-production`, framework Other/static, output directory `.`, no build/install command. The user-requested target is preview. The deployment evidence is recorded under `reports/studio-production-20260930/`. Report browser checks do not establish game quality or M7 acceptance.
