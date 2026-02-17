"""Verify the mapping JSON."""
import json

with open(r'c:\Users\Dylan\Desktop\Side\NeuralES\neurales-web\public\electrode_eholder_mapping.json') as f:
    mapping = json.load(f)

print(f"Total mappings: {len(mapping)}")
print(f"\nFirst 5:")
for k, v in list(mapping.items())[:5]:
    print(f"  {k} -> {v['electrode']} ({v['distance']:.3f})")

# Group by electrode
electrodes_used = {}
for holder, data in mapping.items():
    elec = data['electrode']
    if elec not in electrodes_used:
        electrodes_used[elec] = []
    electrodes_used[elec].append((holder, data['distance']))

print(f"\nElectrodes used: {len(electrodes_used)} (out of 30 expected)")
for elec in sorted(electrodes_used.keys())[:10]:
    holders = electrodes_used[elec]
    print(f"  {elec}: {len(holders)} mount(s) - {[h[0] for h in holders]}")
