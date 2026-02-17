export type Electrode = {
  id: string;
  // Position on a unit sphere (approximate 10-20 layout).
  x: number;
  y: number;
  z: number;
};

// Ultracortex Mark IV (41 electrodes) standard 10-20/10-10 layout.
// Coordinates match the actual 3D model positions.
export const ELECTRODES_ULTRACORTEX_MARK_IV: Electrode[] = [
  // Frontal pole
  { id: "Fp1", x: -0.308, y: 0.951, z: 0.0 },
  { id: "Fpz", x: 0.0, y: 1.0, z: 0.0 },
  { id: "Fp2", x: 0.308, y: 0.951, z: 0.0 },
  
  // Anterior-Frontal
  { id: "AF3", x: -0.588, y: 0.809, z: 0.0 },
  { id: "AF4", x: 0.588, y: 0.809, z: 0.0 },
  
  // Frontal
  { id: "F7", x: -0.951, y: 0.309, z: 0.0 },
  { id: "F5", x: -0.809, y: 0.588, z: 0.0 },
  { id: "F3", x: -0.588, y: 0.809, z: 0.0 },
  { id: "F1", x: -0.309, y: 0.951, z: 0.0 },
  { id: "Fz", x: 0.0, y: 1.0, z: 0.0 },
  { id: "F2", x: 0.309, y: 0.951, z: 0.0 },
  { id: "F4", x: 0.588, y: 0.809, z: 0.0 },
  { id: "F6", x: 0.809, y: 0.588, z: 0.0 },
  { id: "F8", x: 0.951, y: 0.309, z: 0.0 },
  
  // Temporal/Central
  { id: "T9", x: -1.0, y: 0.0, z: 0.0 },
  { id: "T7", x: -0.951, y: 0.0, z: 0.309 },
  { id: "C5", x: -0.809, y: 0.0, z: 0.588 },
  { id: "C3", x: -0.588, y: 0.0, z: 0.809 },
  { id: "C1", x: -0.309, y: 0.0, z: 0.951 },
  { id: "Cz", x: 0.0, y: 0.0, z: 1.0 },
  { id: "C2", x: 0.309, y: 0.0, z: 0.951 },
  { id: "C4", x: 0.588, y: 0.0, z: 0.809 },
  { id: "C6", x: 0.809, y: 0.0, z: 0.588 },
  { id: "T8", x: 0.951, y: 0.0, z: 0.309 },
  { id: "T10", x: 1.0, y: 0.0, z: 0.0 },
  
  // Parietal
  { id: "P7", x: -0.951, y: -0.309, z: 0.0 },
  { id: "P5", x: -0.809, y: -0.588, z: 0.0 },
  { id: "P3", x: -0.588, y: -0.809, z: 0.0 },
  { id: "P1", x: -0.309, y: -0.951, z: 0.0 },
  { id: "Pz", x: 0.0, y: -1.0, z: 0.0 },
  { id: "P2", x: 0.309, y: -0.951, z: 0.0 },
  { id: "P4", x: 0.588, y: -0.809, z: 0.0 },
  { id: "P6", x: 0.809, y: -0.588, z: 0.0 },
  { id: "P8", x: 0.951, y: -0.309, z: 0.0 },
  
  // Occipital
  { id: "O1", x: -0.588, y: -0.809, z: 0.0 },
  { id: "Oz", x: 0.0, y: -1.0, z: 0.0 },
  { id: "O2", x: 0.588, y: -0.809, z: 0.0 },
];

