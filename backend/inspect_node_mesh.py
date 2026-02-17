"""Inspect which nodes reference which meshes in the GLB."""
from pygltflib import GLTF2

glb_path = r"C:\Users\Dylan\Desktop\Side\NeuralES\neurales-web\public\Casque&ele.glb"
gltf = GLTF2().load(glb_path)

print("=" * 60)
print("Node → Mesh Mapping")
print("=" * 60)

for i, node in enumerate(gltf.nodes):
    if 'Eholder' in node.name:
        mesh_idx = node.mesh if hasattr(node, 'mesh') else None
        if mesh_idx is not None:
            mesh_name = gltf.meshes[mesh_idx].name if mesh_idx < len(gltf.meshes) else f"unknown ({mesh_idx})"
            print(f"Node {i:2d}: {node.name:40s} → Mesh {mesh_idx}: {mesh_name}")
        else:
            print(f"Node {i:2d}: {node.name:40s} → NO MESH (only transform)")

print("\n" + "=" * 60)
print("All Meshes")
print("=" * 60)
for i, mesh in enumerate(gltf.meshes):
    print(f"Mesh {i}: {mesh.name}")

print("\n" + "=" * 60)
print("Primitives in Eholder mesh")
print("=" * 60)
for mesh in gltf.meshes:
    if 'Eholder' in mesh.name:
        print(f"\nMesh '{mesh.name}' has {len(mesh.primitives)} primitive(s)")
        for j, prim in enumerate(mesh.primitives):
            print(f"  Primitive {j}: indices={prim.indices}, mode={prim.mode}")
