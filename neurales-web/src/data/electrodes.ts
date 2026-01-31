export type Electrode = {
  id: string;
  // Position on a unit sphere (approximate 10-20 layout).
  x: number;
  y: number;
  z: number;
};

// 16-channel 10-20-ish layout. Adjust with real coordinates when you have them.
export const ELECTRODES_16: Electrode[] = [
  { id: "Fp1", x: -0.45, y: 0.9, z: 0.15 },
  { id: "Fp2", x: 0.45, y: 0.9, z: 0.15 },
  { id: "F7", x: -0.9, y: 0.45, z: 0.05 },
  { id: "F3", x: -0.35, y: 0.55, z: 0.35 },
  { id: "F4", x: 0.35, y: 0.55, z: 0.35 },
  { id: "F8", x: 0.9, y: 0.45, z: 0.05 },
  { id: "T7", x: -1.0, y: 0.05, z: 0.0 },
  { id: "C3", x: -0.45, y: 0.05, z: 0.6 },
  { id: "C4", x: 0.45, y: 0.05, z: 0.6 },
  { id: "T8", x: 1.0, y: 0.05, z: 0.0 },
  { id: "P7", x: -0.9, y: -0.45, z: 0.05 },
  { id: "P3", x: -0.35, y: -0.35, z: 0.45 },
  { id: "P4", x: 0.35, y: -0.35, z: 0.45 },
  { id: "P8", x: 0.9, y: -0.45, z: 0.05 },
  { id: "O1", x: -0.35, y: -0.9, z: 0.1 },
  { id: "O2", x: 0.35, y: -0.9, z: 0.1 },
];
