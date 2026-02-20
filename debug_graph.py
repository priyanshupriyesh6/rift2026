import sys
sys.path.insert(0, r'c:\Users\priya\Desktop\rift2026\backend')

import pandas as pd
from detector import MoneyMulingDetector
import networkx as nx

# Create test data matching what we sent
data = {
    'transaction_id': ['CIRC_001', 'CIRC_002', 'CIRC_003', 'SMURF_001', 'SMURF_002', 'SMURF_003', 'SMURF_004', 'SMURF_005', 'NORMAL_001', 'NORMAL_002'],
    'from_account': ['ACC_A', 'ACC_B', 'ACC_C', 'SMURF_SOURCE', 'SMURF_SOURCE', 'SMURF_SOURCE', 'SMURF_SOURCE', 'SMURF_SOURCE', 'USER_1', 'USER_2'],
    'to_account': ['ACC_B', 'ACC_C', 'ACC_A', 'ACC_D', 'ACC_E', 'ACC_F', 'ACC_G', 'ACC_H', 'USER_2', 'USER_3'],
    'amount': [10000.00, 9500.00, 9000.00, 2000.00, 2100.00, 2050.00, 2150.00, 2000.00, 500.00, 600.00],
    'timestamp': pd.to_datetime([
        '2026-02-15 10:00:00', '2026-02-15 10:05:00', '2026-02-15 10:10:00',
        '2026-02-16 09:00:00', '2026-02-16 09:05:00', '2026-02-16 09:10:00', '2026-02-16 09:15:00', '2026-02-16 09:20:00',
        '2026-02-14 08:00:00', '2026-02-14 09:00:00'
    ])
}

df = pd.DataFrame(data)

# Create detector and load
detector = MoneyMulingDetector()
detector.load_transactions(df)

print("=" * 60)
print("GRAPH STRUCTURE DEBUG")
print("=" * 60)
print(f"\nNodes in graph: {list(detector.graph.nodes())}")
print(f"Edges in graph: {list(detector.graph.edges())}")
print(f"\nEdge data:")
for edge in detector.graph.edges():
    edge_data = detector.graph.get_edge_data(edge[0], edge[1])
    print(f"  {edge[0]} -> {edge[1]}: {edge_data}")

print(f"\n\nFinding cycles...")
simple_cycles = list(nx.simple_cycles(detector.graph))
print(f"Found {len(simple_cycles)} cycles:")
for i, cycle in enumerate(simple_cycles):
    print(f"  Cycle {i+1}: {cycle}")

print(f"\n\nRunning full detection...")
results = detector.run_full_detection()
print(f"Detection results keys: {results.keys()}")
print(f"Number of rings detected: {len(detector.rings)}")
for ring_id, ring_data in detector.rings.items():
    print(f"\n  {ring_id}:")
    print(f"    Type: {ring_data['type']}")
    print(f"    Members: {ring_data['members']}")
    print(f"    Total Amount: ${ring_data['total_amount']}")

print(f"\n\nCircular routing results:")
print(f"  Type of circular_routing: {type(results.get('circular_routing'))}")
print(f"  Content: {results.get('circular_routing')}")
