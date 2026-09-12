# Optional contact mathematics — not a Blender solver

`contact_math.py` is standard-library-only code for the spatial error identified in BW1. It is not a general-purpose asset studio, finger IK, collision solver or neural model.

It builds a hand frame from manually identified/verified OPEN-pose landmarks in world metres. It deliberately fails on ambiguous palm markers, backward tips and invalid rigid transformations. It provides relative rigid-frame calculations and point-to-finite-cylinder screens. The actual Blender adapter must extract evaluated geometry, account for units and modifiers, and handle bones/constraints in the installed API.

Run tests with `python -m unittest discover -s tests -v` from the packet root. Run the synthetic CLI with `python tools/contact_math.py examples/synthetic_open_hand.json --output reports/my_synthetic_frame.json`.

The CLI refuses an existing output file. Templates with null entries are deliberately incomplete and must not be treated as a measured dataset. `input_example_only` and `art_approval` labels are retained in output.

A sampled numeric PASS means only those points satisfied the chosen ideal-cylinder screen. It does not establish full mesh enclosure, force closure, collision-free animation, correct bone control, attractive art or runtime suitability.

All matrices use column-vector convention with basis axes stored as matrix columns. Transforms must be proper rigid transforms; nonuniform scale, shear and reflection are rejected rather than silently stripped.
