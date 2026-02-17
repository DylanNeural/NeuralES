"""
Compute optimal spatial mapping between EEG electrode positions and physical Eholder positions.
Uses Hungarian algorithm to minimize total assignment distance.
"""

import json
import numpy as np
from scipy.optimize import linear_sum_assignment
import math

# Physical Eholder positions (extracted from GLB model)
eholders = [
    {"index": 0, "name": "M4_Hardware_09_Eholder", "pos": [-43.83, 63.71, -93.15]},
    {"index": 1, "name": "M4_Hardware_09_Eholder001", "pos": [-58.36, 88.38, -71.59]},
    {"index": 2, "name": "M4_Hardware_09_Eholder002", "pos": [-33.99, 34.93, -105.20]},
    {"index": 3, "name": "M4_Hardware_09_Eholder003", "pos": [-0.03, 75.54, -97.67]},
    {"index": 4, "name": "M4_Hardware_09_Eholder004", "pos": [-38.43, 128.41, -41.43]},
    {"index": 5, "name": "M4_Hardware_09_Eholder005", "pos": [-86.42, 70.44, -34.18]},
    {"index": 6, "name": "M4_Hardware_09_Eholder006", "pos": [-79.78, 34.27, -61.81]},
    {"index": 7, "name": "M4_Hardware_09_Eholder007", "pos": [0.56, 36.35, -112.82]},
    {"index": 8, "name": "M4_Hardware_09_Eholder008", "pos": [34.03, 35.22, -108.10]},
    {"index": 9, "name": "M4_Hardware_09_Eholder009", "pos": [45.47, 65.07, -95.75]},
    {"index": 10, "name": "M4_Hardware_09_Eholder010", "pos": [80.69, 33.81, -60.55]},
    {"index": 11, "name": "M4_Hardware_09_Eholder011", "pos": [93.58, 34.45, -0.26]},
    {"index": 12, "name": "M4_Hardware_09_Eholder012", "pos": [86.74, 70.24, -34.38]},
    {"index": 13, "name": "M4_Hardware_09_Eholder014", "pos": [79.58, 34.98, 60.48]},
    {"index": 14, "name": "M4_Hardware_09_Eholder015", "pos": [82.60, 69.35, 33.15]},
    {"index": 15, "name": "M4_Hardware_09_Eholder013", "pos": [44.63, 64.68, 95.10]},
    {"index": 16, "name": "M4_Hardware_09_Eholder016", "pos": [35.93, 35.01, 110.09]},
    {"index": 17, "name": "M4_Hardware_09_Eholder017", "pos": [0.24, 35.50, 116.92]},
    {"index": 18, "name": "M4_Hardware_09_Eholder018", "pos": [-34.43, 35.31, 109.71]},
    {"index": 19, "name": "M4_Hardware_09_Eholder019", "pos": [-45.03, 64.16, 96.04]},
    {"index": 20, "name": "M4_Hardware_09_Eholder020", "pos": [-56.59, 87.42, 70.65]},
    {"index": 21, "name": "M4_Hardware_09_Eholder021", "pos": [0.02, 78.66, 105.81]},
    {"index": 22, "name": "M4_Hardware_09_Eholder022", "pos": [-77.47, 34.80, 59.88]},
    {"index": 23, "name": "M4_Hardware_09_Eholder023", "pos": [-84.66, 70.14, 34.15]},
    {"index": 24, "name": "M4_Hardware_09_Eholder024", "pos": [-95.44, 33.61, -1.17]},
    {"index": 25, "name": "M4_Hardware_09_Eholder025", "pos": [-71.08, 106.31, 1.23]},
    {"index": 26, "name": "M4_Hardware_09_Eholder026", "pos": [-35.33, 121.48, 38.35]},
    {"index": 27, "name": "M4_Hardware_09_Eholder027", "pos": [0.83, 111.31, 76.46]},
    {"index": 28, "name": "M4_Hardware_09_Eholder028", "pos": [55.90, 87.26, 69.79]},
    {"index": 29, "name": "M4_Hardware_09_Eholder029", "pos": [0.24, 142.14, 0.84]},
    {"index": 30, "name": "M4_Hardware_09_Eholder030", "pos": [36.90, 122.83, 38.33]},
    {"index": 31, "name": "M4_Hardware_09_Eholder031", "pos": [39.53, 128.99, -40.65]},
    {"index": 32, "name": "M4_Hardware_09_Eholder032", "pos": [0.08, 114.24, -80.05]},
    {"index": 33, "name": "M4_Hardware_09_Eholder033", "pos": [59.66, 90.28, -73.93]},
    {"index": 34, "name": "M4_Hardware_09_Eholder034", "pos": [72.58, 108.09, 1.61]},
]

# Theoretical EEG electrode positions (from electrodes.ts, normalized to unit sphere)
electrodes = [
    {"id": "Fp1", "pos": [-0.308, 0.951, -0.0]},
    {"id": "Fp2", "pos": [0.308, 0.951, -0.0]},
    {"id": "AF3", "pos": [-0.238, 0.901, 0.361]},
    {"id": "AF4", "pos": [0.238, 0.901, 0.361]},
    {"id": "F7", "pos": [-0.669, 0.669, 0.316]},
    {"id": "F3", "pos": [-0.559, 0.669, 0.488]},
    {"id": "Fz", "pos": [-0.0, 0.669, 0.743]},
    {"id": "F4", "pos": [0.559, 0.669, 0.488]},
    {"id": "F8", "pos": [0.669, 0.669, 0.316]},
    {"id": "FC5", "pos": [-0.743, 0.488, 0.469]},
    {"id": "FC1", "pos": [-0.361, 0.488, 0.788]},
    {"id": "FC2", "pos": [0.361, 0.488, 0.788]},
    {"id": "FC6", "pos": [0.743, 0.488, 0.469]},
    {"id": "T7", "pos": [-1.0, 0.0, 0.0]},
    {"id": "C3", "pos": [-0.809, 0.0, 0.588]},
    {"id": "Cz", "pos": [-0.0, 0.0, 1.0]},
    {"id": "C4", "pos": [0.809, 0.0, 0.588]},
    {"id": "T8", "pos": [1.0, 0.0, 0.0]},
    {"id": "CP5", "pos": [-0.743, -0.488, 0.469]},
    {"id": "CP1", "pos": [-0.361, -0.488, 0.788]},
    {"id": "CP2", "pos": [0.361, -0.488, 0.788]},
    {"id": "CP6", "pos": [0.743, -0.488, 0.469]},
    {"id": "P7", "pos": [-0.669, -0.669, 0.316]},
    {"id": "P3", "pos": [-0.559, -0.669, 0.488]},
    {"id": "Pz", "pos": [-0.0, -0.669, 0.743]},
    {"id": "P4", "pos": [0.559, -0.669, 0.488]},
    {"id": "P8", "pos": [0.669, -0.669, 0.316]},
    {"id": "O1", "pos": [-0.238, -0.901, 0.361]},
    {"id": "Oz", "pos": [-0.0, -0.951, 0.0]},
    {"id": "O2", "pos": [0.238, -0.901, 0.361]},
]

def normalize_eholder_positions(eholders):
    """
    Normalize Eholder positions into a consistent reference frame.
    - Center: find centroid
    - Scale: normalize to same magnitude as EEG positions
    """
    positions = np.array([eh["pos"] for eh in eholders])
    
    # Center at origin
    centroid = positions.mean(axis=0)
    positions_centered = positions - centroid
    
    # Find radius (average distance from origin)
    radii = np.linalg.norm(positions_centered, axis=1)
    avg_radius = radii.mean()
    
    # Normalize to unit magnitude
    positions_normalized = positions_centered / avg_radius if avg_radius > 0 else positions_centered
    
    print(f"Eholder normalization:")
    print(f"  Centroid: {centroid}")
    print(f"  Average radius: {avg_radius:.2f}")
    print(f"  Normalized radius range: [{positions_normalized.min():.3f}, {positions_normalized.max():.3f}]")
    
    return positions_normalized

def normalize_electrode_positions(electrodes):
    """
    EEG positions are already normalized to unit sphere.
    Just convert to numpy array.
    """
    positions = np.array([el["pos"] for el in electrodes])
    print(f"Electrode positions already normalized (unit sphere)")
    return positions

def compute_distance_matrix(electrodes_pos, eholders_pos):
    """
    Compute Euclidean distance matrix between electrodes and eholders.
    Shape: (num_electrodes, num_eholders)
    """
    distances = np.zeros((electrodes_pos.shape[0], eholders_pos.shape[0]))
    for i, el_pos in enumerate(electrodes_pos):
        for j, eh_pos in enumerate(eholders_pos):
            distances[i, j] = np.linalg.norm(el_pos - eh_pos)
    return distances

def solve_assignment(distance_matrix):
    """
    Solve the linear assignment problem using Hungarian algorithm.
    Returns: (electrode_indices, eholder_indices, total_cost)
    """
    row_ind, col_ind = linear_sum_assignment(distance_matrix)
    total_cost = distance_matrix[row_ind, col_ind].sum()
    return row_ind, col_ind, total_cost

def build_mapping(electrodes, eholders, electrode_indices, eholder_indices, distance_matrix):
    """
    Build a mapping dict and list of unused eholders.
    """
    mapping = {}
    used_eholder_indices = set(int(idx) for idx in eholder_indices)
    unused_eholders = []
    
    for el_idx, eh_idx in zip(electrode_indices, eholder_indices):
        electrode_id = electrodes[int(el_idx)]["id"]
        eholder_name = eholders[int(eh_idx)]["name"]
        distance = float(distance_matrix[int(el_idx), int(eh_idx)])
        
        mapping[electrode_id] = {
            "eholder_name": eholder_name,
            "eholder_index": int(eh_idx),
            "distance": distance,
        }
    
    for i, eh in enumerate(eholders):
        if i not in used_eholder_indices:
            unused_eholders.append({
                "index": i,
                "name": eh["name"],
                "pos": [float(x) for x in eh["pos"]]
            })
    
    return mapping, unused_eholders

def main():
    print("=" * 80)
    print("Computing Optimal EEG-to-Eholder Mapping")
    print("=" * 80)
    
    # Normalize coordinate systems
    print("\n1. Normalizing coordinates...")
    eholders_normalized = normalize_eholder_positions(eholders)
    electrodes_normalized = normalize_electrode_positions(electrodes)
    
    # Compute distance matrix
    print("\n2. Computing distance matrix...")
    distance_matrix = compute_distance_matrix(electrodes_normalized, eholders_normalized)
    print(f"   Distance matrix shape: {distance_matrix.shape}")
    print(f"   Distance range: [{distance_matrix.min():.3f}, {distance_matrix.max():.3f}]")
    
    # Solve assignment problem
    print("\n3. Solving linear assignment problem (Hungarian algorithm)...")
    el_indices, eh_indices, total_cost = solve_assignment(distance_matrix)
    print(f"   Total assignment cost: {total_cost:.3f}")
    print(f"   Average distance per electrode: {total_cost / len(electrodes):.3f}")
    
    # Build mapping
    print("\n4. Building mapping...")
    mapping, unused = build_mapping(electrodes, eholders, el_indices, eh_indices, distance_matrix)
    
    # Print results
    print("\n" + "=" * 80)
    print("MAPPING RESULTS")
    print("=" * 80)
    print(f"\n✓ Successfully mapped {len(mapping)} electrodes to Eholders")
    print(f"ℹ Unused Eholders: {len(unused)}")
    
    print("\nElectrode → Eholder mapping:")
    for el_id in sorted(mapping.keys()):
        m = mapping[el_id]
        print(f"  {el_id:>3} → {m['eholder_name']:>30} (distance: {m['distance']:.3f})")
    
    if unused:
        print(f"\nUnused Eholders ({len(unused)}):")
        for eh in unused:
            print(f"  [{eh['index']:2d}] {eh['name']}")
    
    # Write output
    output = {
        "timestamp": str(np.datetime64('now')),
        "num_electrodes_mapped": int(len(mapping)),
        "num_eholders_total": int(len(eholders)),
        "num_eholders_unused": int(len(unused)),
        "total_assignment_cost": float(total_cost),
        "average_distance_per_electrode": float(total_cost / len(electrodes)),
        "mapping": mapping,
        "unused_eholders": [
            {"index": int(eh["index"]), "name": str(eh["name"]), "pos": [float(x) for x in eh["pos"]]}
            for eh in unused
        ],
    }
    
    output_file = "electrode_eholder_mapping.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Mapping saved to: {output_file}")
    return output

if __name__ == "__main__":
    main()
