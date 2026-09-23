"""
Simplified single-vessel Constrained Constructive Optimization (CCO),
following Schreiner (1993) / Karch et al. (2000):
  - each new terminal is connected by bifurcating an existing segment
  - radii follow Murray's law: r_parent^3 = sum(r_child^3), calibrated
    to a real, measured root radius
  - candidate connection minimizes added intravascular volume
  - simple minimum-spacing + segment-segment proximity rules stand in
    for full geometric non-intersection constraints
This is a demonstration-scope implementation, not a production CCO solver.
"""
import numpy as np


class CCOTree:
    def __init__(self, root_pos, root_radius, rng):
        self.nodes = [np.array(root_pos, dtype=float)]
        self.radius = [root_radius]
        # edges: (parent_node_idx, child_node_idx, n_terminals_downstream)
        self.edges = []
        self.parent_edge = {}   # node_idx -> edge_idx (edge feeding this node)
        self.children = {0: []} # node_idx -> list of edge_idx
        self.rng = rng
        self.k_murray = None    # calibration constant r = k * flow^(1/3)

    def _add_node(self, pos):
        self.nodes.append(np.array(pos, dtype=float))
        self.radius.append(0.0)
        idx = len(self.nodes) - 1
        self.children[idx] = []
        return idx

    def _add_edge(self, a, b):
        eidx = len(self.edges)
        self.edges.append([a, b, 0])
        self.parent_edge[b] = eidx
        self.children[a].append(eidx)
        return eidx

    def _edge_length(self, e):
        a, b, _ = self.edges[e]
        return float(np.linalg.norm(self.nodes[a] - self.nodes[b]))

    def _propagate_flow(self, leaf_node):
        """Walk from a leaf up to the root, incrementing downstream terminal
        count on every ancestor edge and recomputing its Murray-law radius."""
        node = leaf_node
        while node in self.parent_edge:
            e = self.parent_edge[node]
            self.edges[e][2] += 1
            flow = self.edges[e][2]
            r = self.k_murray * (flow ** (1.0 / 3.0))
            self.radius[self.edges[e][1]] = r
            node = self.edges[e][0]

    def total_volume(self):
        vol = 0.0
        for a, b, flow in self.edges:
            r = self.k_murray * (flow ** (1.0 / 3.0))
            vol += np.pi * r * r * self._edge_length(self.edges.index([a, b, flow]))
        return vol

    def all_segment_endpoints(self):
        for a, b, flow in self.edges:
            yield self.nodes[a], self.nodes[b]

    def point_segment_distance(self, p, a, b):
        ab = b - a
        t = np.dot(p - a, ab) / (np.dot(ab, ab) + 1e-12)
        t = np.clip(t, 0.0, 1.0)
        proj = a + t * ab
        return np.linalg.norm(p - proj), t


def grow_cco_tree(root_pos, root_radius, n_terminal, domain_volume,
                   inside_fn, seed=0, max_tries_per_terminal=60,
                   candidates_per_try=12, bifurcation_fracs=(0.2, 0.35, 0.5, 0.65, 0.8)):
    rng = np.random.default_rng(seed)
    tree = CCOTree(root_pos, root_radius, rng)

    if n_terminal <= 0:
        return tree

    # calibrate Murray's law: root carries n_terminal units of flow
    tree.k_murray = root_radius / (n_terminal ** (1.0 / 3.0))

    # first terminal: random valid point, direct edge from root
    first = _sample_valid_point(root_pos, domain_volume, n_terminal, inside_fn, rng)
    if first is None:
        return tree
    n1 = tree._add_node(first)
    tree._add_edge(0, n1)
    tree._propagate_flow(n1)

    placed = 1
    d_min = (domain_volume / max(n_terminal, 1)) ** (1.0 / 3.0) * 0.6

    while placed < n_terminal:
        best = None  # (added_volume, candidate_pos, edge_idx, t)
        found_any_candidate = False
        for _try in range(max_tries_per_terminal):
            cand = _sample_valid_point(root_pos, domain_volume, n_terminal, inside_fn, rng,
                                        existing=tree.nodes, d_min=d_min)
            if cand is None:
                continue
            found_any_candidate = True
            local = _best_bifurcation(tree, cand, bifurcation_fracs)
            if local is not None:
                added_vol, eidx, t = local
                if best is None or added_vol < best[0]:
                    best = (added_vol, cand, eidx, t)
        if best is None:
            if not found_any_candidate:
                d_min *= 0.7
                if d_min < 1e-2:
                    break
                continue
            else:
                # candidates existed but none passed intersection checks
                d_min *= 0.85
                if d_min < 1e-2:
                    break
                continue

        _, cand, eidx, t = best
        a, b, old_flow = tree.edges[eidx]
        bp = tree.nodes[a] + t * (tree.nodes[b] - tree.nodes[a])
        bnode = tree._add_node(bp)
        # rewire: remove old edge a->b, add a->bnode, bnode->b (carry old subtree), bnode->new_terminal
        tree.edges[eidx] = [a, bnode, 0]
        tree.parent_edge[bnode] = eidx
        tree.children[a] = [ei if ei != eidx else eidx for ei in tree.children[a]]
        tree.children[bnode] = []
        e2 = tree._add_edge(bnode, b)
        tree.edges[e2][2] = old_flow  # subtree flow carried over
        tnode = tree._add_node(cand)
        tree._add_edge(bnode, tnode)

        # recompute flows cleanly via propagation from both new leaves upward
        _recompute_all_flows(tree)
        placed += 1

    return tree


def _sample_valid_point(root_pos, domain_volume, n_terminal, inside_fn, rng,
                         existing=None, d_min=None, batch=200):
    for _ in range(20):
        pts = rng.uniform(0, 1, size=(batch, 3))  # placeholder, replaced by caller-space sampling
        break
    # inside_fn handles its own bounding box sampling; ask for `batch` candidates at once
    pts = inside_fn(batch)
    if pts is None or len(pts) == 0:
        return None
    if existing is not None and d_min is not None and len(existing) > 0:
        ex = np.array(existing)
        for p in pts:
            d = np.linalg.norm(ex - p, axis=1).min()
            if d >= d_min:
                return p
        return None
    return pts[0]


def _best_bifurcation(tree, cand, fracs):
    best = None
    for eidx, (a, b, flow) in enumerate(tree.edges):
        pa, pb = tree.nodes[a], tree.nodes[b]
        for t in fracs:
            bp = pa + t * (pb - pa)
            # candidate segments: a-bp (old flow+1), bp-b (old flow), bp-cand (flow 1)
            len1 = np.linalg.norm(bp - pa)
            len2 = np.linalg.norm(pb - bp)
            len3 = np.linalg.norm(cand - bp)
            r1 = tree.k_murray * ((flow + 1) ** (1/3))
            r2 = tree.k_murray * (flow ** (1/3))
            r3 = tree.k_murray * (1 ** (1/3))
            vol = np.pi * (r1*r1*len1 + r2*r2*len2 + r3*r3*len3)
            # reject degenerate tiny segments (bifurcation point ~coincident with endpoint or candidate)
            if len1 < 1e-2 or len2 < 1e-2 or len3 < 1e-2:
                continue
            # simplified non-intersection: new candidate segment (bp->cand) must not pass
            # too close to unrelated existing segments
            if _intersects_others(tree, bp, cand, exclude_edge=eidx, min_clearance=r3*1.2):
                continue
            if best is None or vol < best[0]:
                best = (vol, eidx, t)
    return best


def _intersects_others(tree, p, q, exclude_edge, min_clearance):
    for eidx, (a, b, flow) in enumerate(tree.edges):
        if eidx == exclude_edge:
            continue
        pa, pb = tree.nodes[a], tree.nodes[b]
        d = _segment_segment_distance(p, q, pa, pb)
        if d < min_clearance:
            return True
    return False


def _segment_segment_distance(p1, p2, p3, p4):
    # standard closest-distance-between-segments (Ericson, "Real-Time Collision Detection")
    d1 = p2 - p1
    d2 = p4 - p3
    r = p1 - p3
    a = np.dot(d1, d1)
    e = np.dot(d2, d2)
    f = np.dot(d2, r)
    if a < 1e-12 and e < 1e-12:
        return np.linalg.norm(p1 - p3)
    if a < 1e-12:
        t = np.clip(f / e, 0, 1)
        s = 0.0
    else:
        c = np.dot(d1, r)
        if e < 1e-12:
            s = np.clip(-c / a, 0, 1)
            t = 0.0
        else:
            b = np.dot(d1, d2)
            denom = a * e - b * b
            s = np.clip((b * f - c * e) / denom, 0, 1) if abs(denom) > 1e-12 else 0.0
            t = (b * s + f) / e
            if t < 0:
                t = 0.0
                s = np.clip(-c / a, 0, 1)
            elif t > 1:
                t = 1.0
                s = np.clip((b - c) / a, 0, 1)
    c1 = p1 + s * d1
    c2 = p3 + t * d2
    return np.linalg.norm(c1 - c2)


def _recompute_all_flows(tree):
    for e in tree.edges:
        e[2] = 0
    for node_idx in range(len(tree.nodes)):
        if len(tree.children[node_idx]) == 0 and node_idx in tree.parent_edge:
            n = node_idx
            while n in tree.parent_edge:
                e = tree.parent_edge[n]
                tree.edges[e][2] += 1
                n = tree.edges[e][0]
    for eidx, (a, b, flow) in enumerate(tree.edges):
        r = tree.k_murray * (max(flow, 1) ** (1/3))
        tree.radius[b] = r
