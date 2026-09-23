import sys
sys.path.insert(0, '.')
import numpy as np
from run_opencco import parse_opencco_xml

node_pos, edges = parse_opencco_xml('territory_0.xml')

# find node 1's parent edge and a child edge of node 1
parent_edge = [e for e in edges if e[1] == 1][0]
child_edges = [e for e in edges if e[0] == 1]
print("parent_edge (from,to,r):", parent_edge)
print("child_edges (from,to,r):", child_edges[:3])

VOXEL = 1.5
local_bbmin_mm = np.array([0.0, 0.0, 0.0])  # doesn't matter for a relative comparison

def transform(nid):
    return local_bbmin_mm + np.array(node_pos[nid]) * VOXEL

# parent edge's "to" should be node 1; child edge's "from" should also be node 1
print("\nnode1 pos (raw):", node_pos[1])
print("parent_edge.to  -> transform(1):", transform(parent_edge[1]))
print("child_edge.from -> transform(1):", transform(child_edges[0][0]))
print("are they the same object/value?", transform(parent_edge[1]) is transform(child_edges[0][0]),
      np.array_equal(transform(parent_edge[1]), transform(child_edges[0][0])))
