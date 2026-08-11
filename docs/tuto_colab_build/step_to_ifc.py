# %% [markdown]
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/255ribeiro/cadquery_basics/blob/master/docs/tuto_colab_build/step_to_ifc.ipynb)
#

# %% [markdown]
#
# # STEP → IFC Converter
# Reads `output.step` from the displaced-floors notebook and produces a proper
# IFC4 building model with:
# - One `IfcBuildingStorey` per solid
# - `IfcSlab` (DefaultFloor, t=0.20m) — bottom face **unioned** with the
#   previous storey's top face at each level
# - `IfcWall` (DefaultWall, t=0.15m) — one per non-horizontal face
# - `IfcSlab` (DefaultFloor) on the roof — top face of the last solid

# %% [markdown]
# ### Package installation (Colab only)

# %%
import sys
IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    print("Running in Colab — installing packages …")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install",
                    "cadquery-ocp", "ifcopenshell", "shapely"], check=True)
else:
    print("Local environment — skipping installation.")

# %% [markdown]
# ### Imports

# %%
import ifcopenshell
import ifcopenshell.api
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

# OCP geometry analysis
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs     import GeomAbs_Plane
from OCP.TopExp      import TopExp_Explorer
from OCP.TopAbs      import TopAbs_FACE, TopAbs_REVERSED, TopAbs_SOLID
from OCP.BRepTools   import BRepTools, BRepTools_WireExplorer
from OCP.BRep        import BRep_Tool
from OCP.TopoDS      import TopoDS

# OCP STEP reader
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect    import IFSelect_RetDone

# %% [markdown]
# ### Parameters

# %%
STEP_FILE       = "output.step"
IFC_FILE        = "building.ifc"

FLOOR_THICKNESS = 0.20   # IfcSlab thickness  [m]
WALL_THICKNESS  = 0.15   # IfcWallType nominal thickness (informational) [m]

# %% [markdown]
# ### OCC geometry helpers

# %%
def get_boundary_points(face):
    """
    Ordered XYZ vertices of the outer wire of a planar face.
    Uses BRepTools_WireExplorer which follows edge connectivity.
    """
    wire = BRepTools.OuterWire_s(face)
    pts  = []
    exp  = BRepTools_WireExplorer(wire)
    while exp.More():
        v = exp.CurrentVertex()
        p = BRep_Tool.Pnt_s(v)
        pts.append((p.X(), p.Y(), p.Z()))
        exp.Next()
    return pts


def face_normal(face):
    """
    Outward unit normal of a planar face.
    Flips sign when the face has REVERSED orientation in its parent solid.
    """
    surf = BRepAdaptor_Surface(face)
    if surf.GetType() != GeomAbs_Plane:
        return None
    d = surf.Plane().Axis().Direction()
    n = np.array([d.X(), d.Y(), d.Z()])
    if face.Orientation() == TopAbs_REVERSED:
        n = -n
    return n


def classify_faces(solid):
    """
    Split all planar faces of a solid into:
      bottom - horizontal, normal pointing down  (lowest Z group)
      top    - horizontal, normal pointing up    (highest Z group)
      walls  - all non-horizontal faces

    Each entry is a dict: {face, pts, z_min, z_max}
    """
    exp   = TopExp_Explorer(solid, TopAbs_FACE)
    horiz, walls = [], []

    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        surf = BRepAdaptor_Surface(face)

        if surf.GetType() != GeomAbs_Plane:
            exp.Next()
            continue

        pts   = get_boundary_points(face)
        zs    = [p[2] for p in pts]
        z_min = min(zs)
        z_max = max(zs)
        entry = dict(face=face, pts=pts, z_min=z_min, z_max=z_max)

        if (z_max - z_min) < 1e-3:      # horizontal face
            horiz.append(entry)
        else:
            walls.append(entry)

        exp.Next()

    # Partition horizontal faces into bottom / top by Z elevation
    if horiz:
        all_z  = [f['z_min'] for f in horiz]
        z_lo   = min(all_z)
        z_hi   = max(all_z)
        bottom = [f for f in horiz if abs(f['z_min'] - z_lo) < 1e-3]
        top    = [f for f in horiz if abs(f['z_min'] - z_hi) < 1e-3]
    else:
        bottom, top = [], []

    return dict(bottom=bottom, top=top, walls=walls)


def to_shapely(pts):
    """Project a list of 3-D points to a 2-D shapely Polygon (drop Z)."""
    return Polygon([(p[0], p[1]) for p in pts])

# %% [markdown]
# ### Read and sort solids from STEP

# %%
reader = STEPControl_Reader()
status = reader.ReadFile(STEP_FILE)
assert status == IFSelect_RetDone, f"Failed to read {STEP_FILE}"
reader.TransferRoots()
shape = reader.Shape()

exp = TopExp_Explorer(shape, TopAbs_SOLID)
solids = []
while exp.More():
    solids.append(TopoDS.Solid_s(exp.Current()))
    exp.Next()

def _bottom_z(solid):
    fc = classify_faces(solid)
    return fc['bottom'][0]['z_min'] if fc['bottom'] else 0.0

solids_sorted = sorted(solids, key=_bottom_z)

print(f"Found {len(solids_sorted)} solids in {STEP_FILE}")
for i, s in enumerate(solids_sorted):
    print(f"  Solid {i:2d}  →  bottom z = {_bottom_z(s):.3f} m")

# %% [markdown]
# ### IFC model initialisation

# %%
model = ifcopenshell.file(schema="IFC4")

# ── Project ──────────────────────────────────────────────────────────────────
project = ifcopenshell.api.run("root.create_entity", model,
    ifc_class="IfcProject", name="CadQuery Displaced Floors")
ifcopenshell.api.run("unit.assign_unit", model,
    length={"is_metric": True, "raw": "METRES"})

# ── Geometric contexts ────────────────────────────────────────────────────────
ctx_model = ifcopenshell.api.run("context.add_context", model,
    context_type="Model")
ctx_body  = ifcopenshell.api.run("context.add_context", model,
    context_type="Model", context_identifier="Body",
    target_view="MODEL_VIEW", parent=ctx_model)

# ── Site and Building ─────────────────────────────────────────────────────────
def make_placement(model, x=0., y=0., z=0.):
    """Helper: identity IfcLocalPlacement at (x, y, z)."""
    loc = model.createIfcCartesianPoint([float(x), float(y), float(z)])
    ax  = model.createIfcAxis2Placement3D(loc, None, None)
    return model.createIfcLocalPlacement(None, ax)

site     = ifcopenshell.api.run("root.create_entity", model,
    ifc_class="IfcSite", name="Default Site")
building = ifcopenshell.api.run("root.create_entity", model,
    ifc_class="IfcBuilding", name="Default Building")

site.ObjectPlacement     = make_placement(model)
building.ObjectPlacement = make_placement(model)

ifcopenshell.api.run("aggregate.assign_object", model,
    relating_object=project,  products=[site])
ifcopenshell.api.run("aggregate.assign_object", model,
    relating_object=site,     products=[building])

print("IFC hierarchy: Project → Site → Building  ✓")

# %% [markdown]
# ### Element types

# %%
floor_type = ifcopenshell.api.run("root.create_entity", model,
    ifc_class="IfcSlabType", name="DefaultFloor")
floor_type.PredefinedType = "FLOOR"

wall_type  = ifcopenshell.api.run("root.create_entity", model,
    ifc_class="IfcWallType", name="DefaultWall")
wall_type.PredefinedType  = "STANDARD"

print(f"IfcSlabType  'DefaultFloor'  (t = {FLOOR_THICKNESS*100:.0f} cm)  ✓")
print(f"IfcWallType  'DefaultWall'   (t = {WALL_THICKNESS*100:.0f} cm)   ✓")

# %% [markdown]
# ### IFC geometry helpers

# %%
def _ax2p3d(model, ox=0., oy=0., oz=0., axis_z=(0,0,1), axis_x=(1,0,0)):
    """IfcAxis2Placement3D at origin (ox,oy,oz) with given local axes."""
    loc = model.createIfcCartesianPoint([float(ox), float(oy), float(oz)])
    az  = model.createIfcDirection([float(v) for v in axis_z])
    ax  = model.createIfcDirection([float(v) for v in axis_x])
    return model.createIfcAxis2Placement3D(loc, az, ax)


def create_floor_slab(model, ctx, polygon, z_top, thickness, slab_type):
    """
    IfcSlab from a shapely Polygon.
    The slab top surface sits at z_top; it extends downward by 'thickness'.
    Uses IfcExtrudedAreaSolid (SweptSolid) representation.
    """
    slab = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSlab")
    slab.PredefinedType = "FLOOR"

    # 2-D profile from shapely exterior (drop closing duplicate)
    coords   = list(polygon.exterior.coords)[:-1]
    ifc_pts  = [model.createIfcCartesianPoint([float(x), float(y)])
                for x, y in coords]
    ifc_pts.append(ifc_pts[0])                          # closed polyline
    polyline = model.createIfcPolyline(ifc_pts)
    profile  = model.createIfcArbitraryClosedProfileDef("AREA", None, polyline)

    # Placement at z_top; extrude downward
    placement   = _ax2p3d(model, oz=z_top)
    extrude_dir = model.createIfcDirection([0.0, 0.0, -1.0])
    solid       = model.createIfcExtrudedAreaSolid(
        profile, placement, extrude_dir, float(thickness))

    rep      = model.createIfcShapeRepresentation(ctx, "Body", "SweptSolid", [solid])
    prod_rep = model.createIfcProductDefinitionShape(None, None, [rep])

    slab.ObjectPlacement = make_placement(model)
    slab.Representation  = prod_rep

    ifcopenshell.api.run("type.assign_type", model,
        related_objects=[slab], relating_type=slab_type)
    return slab


def create_wall(model, ctx, pts_3d, wall_type):
    """
    IfcWall from an ordered list of 3-D face vertices.
    Geometry: IfcPolygonalFaceSet (tessellated surface, face-accurate).
    Thickness is carried by the IfcWallType and a Pset_WallCommon property set.
    """
    wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")
    wall.PredefinedType = "STANDARD"

    coord_list = model.createIfcCartesianPointList3D(
        [[float(p[0]), float(p[1]), float(p[2])] for p in pts_3d])
    indices  = list(range(1, len(pts_3d) + 1))
    ifc_face = model.createIfcIndexedPolygonalFace(indices)
    face_set = model.createIfcPolygonalFaceSet(coord_list, None, [ifc_face], None)

    rep      = model.createIfcShapeRepresentation(ctx, "Body", "Tessellation", [face_set])
    prod_rep = model.createIfcProductDefinitionShape(None, None, [rep])

    wall.ObjectPlacement = make_placement(model)
    wall.Representation  = prod_rep

    ifcopenshell.api.run("type.assign_type", model,
        related_objects=[wall], relating_type=wall_type)

    # Pset_WallCommon — nominal thickness so BIM tools can read it
    try:
        pset = ifcopenshell.api.run("pset.add_pset", model,
            product=wall, name="Pset_WallCommon")
        ifcopenshell.api.run("pset.edit_pset", model, pset=pset,
            properties={"IsExternal": False,
                        "LoadBearing": False,
                        "Thickness": float(WALL_THICKNESS)})
    except Exception:
        pass   # pset API might differ across ifcopenshell versions

    return wall

# %% [markdown]
# ### Main loop — storeys, floors, walls

# %%
prev_top_polygon = None   # shapely Polygon of previous solid's top face

for i, solid in enumerate(solids_sorted):
    faces    = classify_faces(solid)
    bottom_z = faces['bottom'][0]['z_min'] if faces['bottom'] else i * 3.0
    top_z    = faces['top'][0]['z_min']    if faces['top']    else bottom_z + 3.0

    print(f"\n── Storey {i:02d}   z = {bottom_z:.2f} m → {top_z:.2f} m ──")

    # ── IfcBuildingStorey ─────────────────────────────────────────────────────
    storey = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcBuildingStorey", name=f"Level {i:02d}")
    storey.Elevation       = float(bottom_z)
    storey.ObjectPlacement = make_placement(model, z=bottom_z)
    ifcopenshell.api.run("aggregate.assign_object", model,
        relating_object=building, products=[storey])

    # ── Floor slab ────────────────────────────────────────────────────────────
    # Current bottom face (XY outline at bottom_z)
    if faces['bottom']:
        cur_poly = to_shapely(faces['bottom'][0]['pts'])

        # Union with the previous storey's top face (same XY plane, same Z level
        # because: top of solid[i-1] = bottom_z of solid[i] = i * pap)
        if prev_top_polygon is not None:
            floor_poly = unary_union([cur_poly, prev_top_polygon])
        else:
            floor_poly = cur_poly

        slab = create_floor_slab(model, ctx_body,
            floor_poly, bottom_z, FLOOR_THICKNESS, floor_type)
        ifcopenshell.api.run("spatial.assign_container", model,
            relating_structure=storey, products=[slab])

        print(f"  IfcSlab  (floor)   z={bottom_z:.2f} m  "
              f"area={floor_poly.area:.2f} m²")

    # ── Walls ─────────────────────────────────────────────────────────────────
    for wf in faces['walls']:
        pts = wf['pts']
        if len(pts) >= 3:
            wall = create_wall(model, ctx_body, pts, wall_type)
            ifcopenshell.api.run("spatial.assign_container", model,
                relating_structure=storey, products=[wall])

    print(f"  IfcWall × {len(faces['walls'])}")

    # ── Store top face for next iteration ─────────────────────────────────────
    if faces['top']:
        prev_top_polygon = to_shapely(faces['top'][0]['pts'])

# %% [markdown]
# ### Roof slab — top face of the last solid

# %%
last_faces = classify_faces(solids_sorted[-1])

if last_faces['top']:
    top_entry = last_faces['top'][0]
    roof_z    = top_entry['z_min']
    roof_poly = to_shapely(top_entry['pts'])

    roof_storey = ifcopenshell.api.run("root.create_entity", model,
        ifc_class="IfcBuildingStorey", name="Roof Level")
    roof_storey.Elevation       = float(roof_z)
    roof_storey.ObjectPlacement = make_placement(model, z=roof_z)
    ifcopenshell.api.run("aggregate.assign_object", model,
        relating_object=building, products=[roof_storey])

    roof_slab = create_floor_slab(model, ctx_body,
        roof_poly, roof_z, FLOOR_THICKNESS, floor_type)
    ifcopenshell.api.run("spatial.assign_container", model,
        relating_structure=roof_storey, products=[roof_slab])

    print(f"\nRoof IfcSlab  z={roof_z:.2f} m  area={roof_poly.area:.2f} m²  ✓")

# %% [markdown]
# ### Export

# %%
model.write(IFC_FILE)

entity_count = len(list(model))
slab_count   = len(model.by_type("IfcSlab"))
wall_count   = len(model.by_type("IfcWall"))
storey_count = len(model.by_type("IfcBuildingStorey"))

print(f"\nExported  →  {IFC_FILE}")
print(f"  IfcBuildingStorey : {storey_count}")
print(f"  IfcSlab           : {slab_count}  (includes roof)")
print(f"  IfcWall           : {wall_count}")
print(f"  Total entities    : {entity_count}")
print("\nOpen in FreeCAD, BlenderBIM, Revit, or any IFC viewer to inspect.")
