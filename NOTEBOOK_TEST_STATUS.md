# Notebook Test Status

Last updated: 2026-08-10

## Passing

- docs/tuto_colab_build/2d_to_3d.ipynb
- docs/tuto_colab_build/build123d_basic_gc.ipynb
- docs/tuto_colab_build/build123d_multiplos_pav_perfil.ipynb
- docs/tuto_colab_build/build123d_primitives_gc.ipynb
- docs/tuto_colab_build/build123d_trusses_gc.ipynb
- docs/tuto_colab_build/multi_pav_b3d_ramdom_disp_resolvido.ipynb
- docs/tuto_colab_build/multi_pav_b3d_resolvido.ipynb
- docs/tuto_colab_build/multi_pav_loft.ipynb

## Failing

### Expected Failures (deferred)

These are intentionally marked as failed for now because `ifcopenshell` is not installed yet.

- docs/tuto_colab_build/step_to_ifc.ipynb
  - Status: FAILED
  - Reason: ModuleNotFoundError: No module named `ifcopenshell`
- docs/tuto_colab_build/step_to_ifc_mesh.ipynb
  - Status: FAILED
  - Reason: ModuleNotFoundError: No module named `ifcopenshell`

### Other Failure (not related to ifcopenshell)

- docs/tuto_colab_build/build123d_multiplos_pav.ipynb
  - Status: FAILED
  - Reason: AttributeError: `'int' object has no attribute 'label'`

## Notes

- UTF-8 BOM parsing issue was fixed for notebooks edited previously.
- `cadquery_simple_viewer` import compatibility shim was added:
  - cadquery_simple_viewer.py
  - docs/tuto_colab_build/cadquery_simple_viewer.py
