BW6 shoulder construction notes — bounded source review

The supplied Ada front crop was actually inspected at native pixel size: `production/asset-studio/supplements/BW5/Wonder_Chess_Proportion_Fit_BW5/references/front_upper.png`. It supplies a broad cap, raised medial edge, and two subordinate overlapping layers. It is the design authority, not a measurement of hidden 3D dimensions.

The Wallace Collection's indexed description of its armor object records a main shoulder plate, smaller overlapping lames, leather/sliding-rivet articulation, and shoulder attachment to the gorget. This supports treating suspension and subordinate plates as separate relationships. It does not establish Ada's exact mechanism. The direct collection page timed out; the complete primary-source search excerpt was read, not its 3D object or unseen photographs: https://wallacelive.wallacecollection.org/eMP/eMuseumPlus?module=collection&objectId=60738&service=ExternalInterface

The Met's composed armor page was opened and read. It explicitly describes a composite assembled from different armor pieces/restorations. Accordingly, it was not treated as a single original mechanical blueprint: https://www.metmuseum.org/art/collection/search/24814

Blender's official Copy Rotation and Child Of documentation were located. Full manual fetches were blocked by the web tool (402); the indexed documentation identifies rotation mix modes and Child Of's inverse offset. The actual installed Blender 5.1.1 API was used and executed. Rest-delta matrices were numerically observed to be identity in the rest state, and posed images/checks establish the limited result; the documentation itself does not establish collision freedom.

- https://docs.blender.org/manual/en/5.0/animation/constraints/transform/copy_rotation.html
- https://docs.blender.org/manual/en/5.1/animation/constraints/relationship/child_of.html

Executed support: independent native helper objects, inverse-corrected shoulder and upper-arm rest deltas, a medial strap pivot, one rigid cap surface, and two independently rigid lames. New cages use purposeful ordered strips and individually controlled section widths/crowns; the new Solidify/Bevel result was actually checked for self-crossings. No cloth/body/rig masters, game clips, or canonical sockets were edited. These are candidate authoring constraints, not a tested runtime mechanism or physical simulation.


Under-strap implementation note: Blender official Hook modifier documentation was checked (https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/hooks.html). Native Hooks were used to bind explicitly selected strap stations to existing rigid plate objects. This documentation supports the operation only; the executed under-strap routes failed their independent collision checks.
