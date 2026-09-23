"""Topology-based identification of the real portal-tree terminal branches
that supply segments II and III, replacing pure spatial-proximity filtering.
"""
import sys, json, collections
sys.path.insert(0, '.')
import numpy as np
import skeleton
from scipy.spatial import cKDTree


def find_s2s3_roots(bridge_radius=6.0, dist_thresh=15.0):
    sk = skeleton.build_skeleton_with_radius('vessel_portal.json', bridge_radius=bridge_radius)
    node_pos = sk['node_pos']; degree = sk['degree']; edges = sk['edges']
    adj = collections.defaultdict(list)
    for a, b, rad in edges:
        adj[a].append((b, rad)); adj[b].append((a, rad))

    leaf_idx = np.where(degree == 1)[0]
    leaf_radius = np.array([max([rr for _, rr in adj[L]], default=0) for L in leaf_idx])
    root = leaf_idx[np.argmax(leaf_radius)]  # main portal trunk stump (excluded)

    parent = {root: None}
    q = collections.deque([root])
    while q:
        u = q.popleft()
        for v, rad in adj[u]:
            if v not in parent:
                parent[v] = u
                q.append(v)

    def load_segment(sid):
        d = json.load(open(f"{sid}.json"))
        return np.array(d['positions']).reshape(-1, 3)
    seg_pts = {sid: load_segment(sid) for sid in [f"S{i}" for i in range(1, 9)]}
    seg_trees = {sid: cKDTree(p) for sid, p in seg_pts.items()}

    leaves = leaf_idx[leaf_idx != root]
    leaf_seg = {}
    for L in leaves:
        p = node_pos[L]
        dists = {sid: t.query(p, k=1)[0] for sid, t in seg_trees.items()}
        best = min(dists, key=dists.get)
        leaf_seg[L] = (best, dists[best])

    s23_leaves = [L for L, (sid, d) in leaf_seg.items() if sid in ('S2', 'S3') and d < dist_thresh]

    def path_to_root(node):
        path = [node]
        while parent[path[-1]] is not None:
            path.append(parent[path[-1]])
        return path[::-1]

    paths = {L: path_to_root(L) for L in s23_leaves}
    common = set(paths[s23_leaves[0]])
    for L in s23_leaves[1:]:
        common &= set(paths[L])

    def depth_of(n):
        d = 0
        while parent[n] is not None:
            n = parent[n]; d += 1
        return d

    left_portal_ancestor = max(common, key=depth_of)

    # incident radius at each confirmed root (for reporting/validation only --
    # OpenCCO computes its own root radius from aPerf/nTerm/gamma)
    roots = []
    for L in s23_leaves:
        seg, dist = leaf_seg[L]
        r = max([rr for _, rr in adj[L]], default=0)
        roots.append({
            'node': int(L), 'pos': node_pos[L].tolist(), 'segment': seg,
            'dist_to_segment': float(dist), 'measured_radius': float(r),
        })
    return {
        'trunk_node': int(root), 'trunk_pos': node_pos[root].tolist(),
        'left_portal_ancestor_node': int(left_portal_ancestor),
        'left_portal_ancestor_pos': node_pos[left_portal_ancestor].tolist(),
        'roots': roots,
    }


if __name__ == '__main__':
    result = find_s2s3_roots()
    print(f"trunk (excluded): node {result['trunk_node']} at {result['trunk_pos']}")
    print(f"left-portal common ancestor: node {result['left_portal_ancestor_node']} at {result['left_portal_ancestor_pos']}")
    print(f"\n{len(result['roots'])} topology-confirmed S2/S3 roots:")
    for r in result['roots']:
        print(f"  node={r['node']:3d} seg={r['segment']} dist={r['dist_to_segment']:.1f}mm "
              f"measured_r={r['measured_radius']:.2f}mm pos={[round(x,1) for x in r['pos']]}")
    json.dump(result, open('s2s3_roots.json', 'w'), indent=1)
