"""Inspect the structure of the GLB file to find Eholders."""

import trimesh
import json

glb_path = r"C:\Users\Dylan\Desktop\Side\NeuralES\neurales-web\public\Casque&ele.glb"
mesh = trimesh.load(glb_path)

print("=" * 60)
print("GLB Structure Inspection")
print("=" * 60)

print(f"\nType: {type(mesh)}")
print(f"Is Scene: {isinstance(mesh, trimesh.Scene)}")

# Check if it's a scene
if hasattr(mesh, 'nodes'):
    print(f"\n✓ Scene with {len(mesh.nodes)} nodes:")
    for i, node in enumerate(mesh.nodes):
        node_name = node.name if hasattr(node, 'name') else 'unnamed'
        geom = 'has geometry' if hasattr(node, 'geometry') and node.geometry is not None else 'no geometry'
        print(f"  [{i:2d}] {node_name:40s} ({geom})")

# Check geometry dict
print()
if hasattr(mesh, 'geometry'):
    print(f"✓ Geometry dict with {len(mesh.geometry)} entries:")
    for i, key in enumerate(list(mesh.geometry.keys())[:50]):
        print(f"  {key}")

# Try to load with force_mesh to see all geometries
print("\n" + "=" * 60)
print("Attempting force_mesh load...")
try:
    mesh2 = trimesh.load(glb_path, force='mesh')
    print(f"Force mesh result: {type(mesh2)}")
    if hasattr(mesh2, 'geometry'):
        print(f"Geometry count: {len(mesh2.geometry)}")
except Exception as e:
    print(f"Error: {e}")
