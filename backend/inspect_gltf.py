"""Inspect GLTF structure more deeply using pygltflib."""

try:
    from pygltflib import GLTF2
    HAS_PYGLTF = True
except ImportError:
    HAS_PYGLTF = False

if HAS_PYGLTF:
    glb_path = r"C:\Users\Dylan\Desktop\Side\NeuralES\neurales-web\public\Casque&ele.glb"
    
    gltf = GLTF2().load(glb_path)
    
    print("=" * 60)
    print("GLTF Structure")
    print("=" * 60)
    
    if gltf.nodes:
        print(f"\nNodes ({len(gltf.nodes)} total):")
        for i, node in enumerate(gltf.nodes):
            print(f"  [{i:2d}] {node.name}")
    
    if gltf.meshes:
        print(f"\nMeshes ({len(gltf.meshes)} total):")
        for i, mesh in enumerate(gltf.meshes):
            print(f"  [{i:2d}] {mesh.name}")
    
    if gltf.scenes:
        print(f"\nScenes ({len(gltf.scenes)} total):")
        for i, scene in enumerate(gltf.scenes):
            print(f"  [{i}] {scene.name if scene.name else 'unnamed'}")
            if scene.nodes:
                for node_idx in scene.nodes:
                    node = gltf.nodes[node_idx]
                    print(f"     └─ {node.name}")

else:
    print("pygltflib not installed. Installing...")
    import subprocess
    subprocess.run([r"C:/Users/Dylan/Desktop/Side/NeuralES/.venv/Scripts/python.exe", "-m", "pip", "install", "pygltflib"])
