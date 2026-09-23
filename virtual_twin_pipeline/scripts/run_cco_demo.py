import json, sys, time
import numpy as np
import trimesh
from scipy.spatial import cKDTree

sys.path.insert(0, '.')
import skeleton
from cco import grow_cco_tree

def load_segment(sid):
    d = json.load(open(f"{sid}.json"))
    pos = np.array(d['positions']).reshape(-1, 3)
    idx = np.array(d['indices']).reshape(-1, 3)
    return pos, idx

meshes = {}
for sid in ['S2', 'S3']:
    pos, idx = load_segment(sid)
    meshes[sid] = trimesh.Trimesh(vertices=pos, faces=idx, process=False)

def get_terminal_leaves(name, bridge_radius=4.0, trunk_ratio=1.8):
    sk = skeleton.build_skeleton_with_radius(name, bridge_radius=bridge_radius)
    deg = sk['degree']
    leaf_idx = np.where(deg == 1)[0]
    radii = sk['max_incident_radius'][leaf_idx]
    med = np.median(radii)
    is_trunk = radii > trunk_ratio * med
    terminal = leaf_idx[~is_trunk]
    return sk['node_pos'][terminal], sk['max_incident_radius'][leaf_idx][~is_trunk]

portal_terminal, portal_radius = get_terminal_leaves('vessel_portal.json')
seg_trees = {sid: cKDTree(meshes[sid].vertices) for sid in ['S2', 'S3']}
seeds = []
for p, r in zip(portal_terminal, portal_radius):
    d2 = seg_trees['S2'].query(p, k=1)[0]
    d3 = seg_trees['S3'].query(p, k=1)[0]
    if min(d2, d3) < 15:
        sid = 'S2' if d2 < d3 else 'S3'
        seeds.append({'pos': p, 'radius': r, 'segment': sid})

seed_pos = np.array([s['pos'] for s in seeds])
seed_tree = cKDTree(seed_pos)
n_seeds = len(seeds)
print(f"{n_seeds} demo seeds (S2+S3 left lateral lobe)")

allpts = np.vstack([meshes['S2'].vertices, meshes['S3'].vertices])
bbmin, bbmax = allpts.min(axis=0), allpts.max(axis=0)
bbox_vol = float(np.prod(bbmax - bbmin))

def inside_domain_batched(pts, batch=1500):
    out = np.zeros(len(pts), dtype=bool)
    for i in range(0, len(pts), batch):
        chunk = pts[i:i + batch]
        in2 = meshes['S2'].contains(chunk)
        in3 = meshes['S3'].contains(chunk)
        out[i:i + batch] = in2 | in3
    return out

print("sampling domain (one-time precompute of point pools)...")
t0 = time.time()
rng = np.random.default_rng(1)
N = 150000
samples = rng.uniform(bbmin, bbmax, size=(N, 3))
inside = inside_domain_batched(samples)
inside_pts = samples[inside]
total_vol_mc = inside.mean() * bbox_vol
print(f"  {time.time()-t0:.1f}s, inside={inside.sum()}, MC volume={total_vol_mc:,.0f}")

_, nearest_seed = seed_tree.query(inside_pts, k=1)
territory_vol = np.bincount(nearest_seed, minlength=n_seeds) / N * bbox_vol

pools = [inside_pts[nearest_seed == i] for i in range(n_seeds)]
for i, s in enumerate(seeds):
    print(f"  territory {i} ({s['segment']}) r={s['radius']:.2f} vol~{territory_vol[i]:,.0f}mm^3 pool={len(pools[i])}pts")

TARGET_TERMINAL_VOL = 1500.0  # mm^3 per synthetic terminal -- the "meso-unit" bridging resolution
results = []
grand_t0 = time.time()
for i, s in enumerate(seeds):
    pool = pools[i]
    n_term = max(1, min(30, round(territory_vol[i] / TARGET_TERMINAL_VOL)))

    def make_inside_fn(pool):
        def inside_fn(batch):
            if len(pool) == 0:
                return np.zeros((0, 3))
            idx = np.random.randint(0, len(pool), size=min(batch, max(len(pool), 1)))
            return pool[idx]
        return inside_fn

    t0 = time.time()
    tree = grow_cco_tree(s['pos'], s['radius'], n_term, territory_vol[i],
                          make_inside_fn(pool), seed=100 + i)
    dt = time.time() - t0
    n_placed = len(tree.nodes) - 1 if len(tree.edges) else 0
    n_leaf_terminals = sum(1 for n in range(len(tree.nodes)) if len(tree.children.get(n, [])) == 0 and n in tree.parent_edge)
    total_len = sum(tree._edge_length(e) for e in range(len(tree.edges)))
    print(f"territory {i} ({s['segment']}): target={n_term} terminals, got {n_leaf_terminals}, "
          f"{len(tree.edges)} segments, total_length={total_len:,.0f}mm, {dt:.1f}s")
    results.append({
        'territory': i, 'segment': s['segment'], 'root_pos': s['pos'].tolist(),
        'root_radius': s['radius'], 'target_terminal': n_term, 'terminal_volume_mm3': TARGET_TERMINAL_VOL,
        'territory_volume_mm3': float(territory_vol[i]),
        'nodes': [n.tolist() for n in tree.nodes],
        'edges': [[int(a), int(b), int(flow), float(tree.k_murray*(max(flow,1)**(1/3)))] for a,b,flow in tree.edges],
    })

print(f"\ntotal CCO growth time: {time.time()-grand_t0:.1f}s")
json.dump(results, open('cco_demo_s2s3.json', 'w'))
print("saved cco_demo_s2s3.json")
