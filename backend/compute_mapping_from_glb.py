"""
Extract real Eholder positions from GLB and compute optimal electrode mapping.
Uses the actual 3D positions from the Casque&ele.glb model.
"""

import json
import numpy as np
from pathlib import Path
from scipy.optimize import linear_sum_assignment
from pygltflib import GLTF2


# 30-electrode Ultracortex Mark IV positions (10-20/10-10 system, normalized to unit sphere)
ELECTRODE_POSITIONS = {
    "Fp1": np.array([-0.308, 0.951, -0.0]),
    "Fpz": np.array([0.0, 1.0, 0.0]),
    "Fp2": np.array([0.308, 0.951, -0.0]),
    "AF3": np.array([-0.588, 0.809, -0.0]),
    "AF4": np.array([0.588, 0.809, -0.0]),
    "F7": np.array([-0.951, 0.309, -0.0]),
    "F5": np.array([-0.809, 0.588, -0.0]),
    "F3": np.array([-0.588, 0.809, 0.0]),
    "F1": np.array([-0.309, 0.951, 0.0]),
    "Fz": np.array([0.0, 1.0, 0.0]),
    "F2": np.array([0.309, 0.951, 0.0]),
    "F4": np.array([0.588, 0.809, 0.0]),
    "F6": np.array([0.809, 0.588, -0.0]),
    "F8": np.array([0.951, 0.309, -0.0]),
    "T9": np.array([-1.0, 0.0, 0.0]),
    "T7": np.array([-0.951, 0.0, 0.309]),
    "C5": np.array([-0.809, 0.0, 0.588]),
    "C3": np.array([-0.588, 0.0, 0.809]),
    "C1": np.array([-0.309, 0.0, 0.951]),
    "Cz": np.array([0.0, 0.0, 1.0]),
    "C2": np.array([0.309, 0.0, 0.951]),
    "C4": np.array([0.588, 0.0, 0.809]),
    "C6": np.array([0.809, 0.0, 0.588]),
    "T8": np.array([0.951, 0.0, 0.309]),
    "T10": np.array([1.0, 0.0, 0.0]),
    "P7": np.array([-0.951, -0.309, -0.0]),
    "P5": np.array([-0.809, -0.588, -0.0]),
    "P3": np.array([-0.588, -0.809, 0.0]),
    "P1": np.array([-0.309, -0.951, 0.0]),
    "Pz": np.array([0.0, -1.0, 0.0]),
    "P2": np.array([0.309, -0.951, 0.0]),
    "P4": np.array([0.588, -0.809, 0.0]),
    "P6": np.array([0.809, -0.588, -0.0]),
    "P8": np.array([0.951, -0.309, -0.0]),
    "O1": np.array([-0.588, -0.809, -0.0]),
    "Oz": np.array([0.0, -1.0, 0.0]),
    "O2": np.array([0.588, -0.809, -0.0]),
}


def extract_eholders_from_glb(glb_path):
    """
    Extract Eholder positions from GLB file using GLTF structure.
    Returns dict of {eholder_name: np.array([x, y, z])}
    """
    gltf = GLTF2().load(glb_path)
    
    eholders = {}
    
    # Extract positions from each Eholder node
    for node in gltf.nodes:
        if 'Eholder' in node.name:
            # Get the world position from node transform
            position = np.array([0, 0, 0], dtype=np.float32)
            
            # GLTF nodes can have translation, rotation, scale
            if node.translation:
                position = np.array(node.translation, dtype=np.float32)
            
            eholders[node.name] = position
    
    return eholders


def normalize_positions(positions_dict):
    """Normalize positions to have mean at origin and unit std."""
    positions = np.array(list(positions_dict.values()))
    
    # Center at origin
    mean = positions.mean(axis=0)
    positions = positions - mean
    
    # Normalize to unit scale
    scale = np.linalg.norm(positions, axis=1).max()
    if scale > 0:
        positions = positions / scale
    
    return {name: positions[i] for i, name in enumerate(positions_dict.keys())}, mean, scale


def compute_distance_matrix(electrode_positions, eholder_positions):
    """
    Compute distance matrix between electrode positions and Eholder positions.
    Returns matrix of shape (n_electrodes, n_eholders)
    """
    # Get normalized electrode positions
    electrode_names = list(electrode_positions.keys())
    electrode_coords = np.array([electrode_positions[name] for name in electrode_names])
    
    # Normalize electrode coordinates
    electrode_mean = electrode_coords.mean(axis=0)
    electrode_coords_norm = electrode_coords - electrode_mean
    electrode_scale = np.linalg.norm(electrode_coords_norm, axis=1).max()
    if electrode_scale > 0:
        electrode_coords_norm = electrode_coords_norm / electrode_scale
    
    # Get Eholder positions (already in 3D from GLB)
    eholder_names = list(eholder_positions.keys())
    eholder_coords = np.array([eholder_positions[name] for name in eholder_names])
    
    # Normalize Eholder coordinates
    eholder_mean = eholder_coords.mean(axis=0)
    eholder_coords_norm = eholder_coords - eholder_mean
    eholder_scale = np.linalg.norm(eholder_coords_norm, axis=1).max()
    if eholder_scale > 0:
        eholder_coords_norm = eholder_coords_norm / eholder_scale
    
    # Compute pairwise distances
    distances = np.zeros((len(electrode_names), len(eholder_names)))
    for i, e_coord in enumerate(electrode_coords_norm):
        for j, h_coord in enumerate(eholder_coords_norm):
            distances[i, j] = np.linalg.norm(e_coord - h_coord)
    
    return distances, electrode_names, eholder_names


def compute_mapping(electrode_positions, eholder_positions):
    """
    Compute optimal mapping between electrodes and Eholders using Hungarian algorithm.
    """
    distances, electrode_names, eholder_names = compute_distance_matrix(
        electrode_positions, eholder_positions
    )
    
    # Apply Hungarian algorithm
    electrode_indices, eholder_indices = linear_sum_assignment(distances)
    
    # Build mapping
    mapping = {}
    for e_idx, h_idx in zip(electrode_indices, eholder_indices):
        electrode_name = electrode_names[e_idx]
        eholder_name = eholder_names[h_idx]
        distance = distances[e_idx, h_idx]
        
        mapping[eholder_name] = {
            "electrode": electrode_name,
            "distance": float(distance),
        }
    
    return mapping, distances


def main():
    # Path to GLB file
    glb_path = Path(__file__).parent.parent / "neurales-web" / "public" / "Casque&ele.glb"
    
    if not glb_path.exists():
        print(f"Error: GLB file not found at {glb_path}")
        return
    
    print(f"Loading GLB from {glb_path}...")
    
    try:
        # Extract Eholder positions from GLB
        eholder_positions = extract_eholders_from_glb(str(glb_path))
        print(f"Found {len(eholder_positions)} Eholders in GLB")
        
        # Compute mapping
        print("Computing optimal electrode mapping...")
        mapping, distances = compute_mapping(ELECTRODE_POSITIONS, eholder_positions)
        
        # Save mapping
        output_path = Path(__file__).parent.parent / "neurales-web" / "public" / "electrode_eholder_mapping.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"Mapping saved to {output_path}")
        
        # Print summary
        print("\nMapping summary:")
        for eholder_name in sorted(mapping.keys())[:5]:
            info = mapping[eholder_name]
            print(f"  {eholder_name} → {info['electrode']} (distance: {info['distance']:.3f})")
        print(f"  ... and {len(mapping) - 5} more")
        
        # Statistics
        distances_array = np.array([info['distance'] for info in mapping.values()])
        print(f"\nDistance statistics:")
        print(f"  Mean: {distances_array.mean():.3f}")
        print(f"  Std: {distances_array.std():.3f}")
        print(f"  Min: {distances_array.min():.3f}")
        print(f"  Max: {distances_array.max():.3f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
