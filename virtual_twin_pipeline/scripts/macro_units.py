import json
import numpy as np
from scipy.spatial import cKDTree
import sys
sys.path.insert(0,'.')
import skeleton

SEG_IDS = [f"S{i}" for i in range(1,9)]

def load_segment(sid):
    d = json.load(open(f"{sid}.json"))
    pos = np.array(d['positions']).reshape(-1,3)
    idx = np.array(d['indices']).reshape(-1,3)
    return pos, idx

def mesh_volume(pos, idx):
    v0 = pos[idx[:,0]]; v1 = pos[idx[:,1]]; v2 = pos[idx[:,2]]
    vol = np.sum(np.einsum('ij,ij->i', v0, np.cross(v1,v2))) / 6.0
    return abs(vol)

def get_terminal_leaves(name, bridge_radius=4.0, trunk_ratio=1.8):
    sk = skeleton.build_skeleton_with_radius(name, bridge_radius=bridge_radius)
    deg = sk['degree']
    leaf_idx = np.where(deg==1)[0]
    radii = sk['max_incident_radius'][leaf_idx]
    med = np.median(radii)
    is_trunk = radii > trunk_ratio*med
    terminal = leaf_idx[~is_trunk]
    trunk = leaf_idx[is_trunk]
    return sk['node_pos'][terminal], sk['node_pos'][trunk], sk['node_pos'][leaf_idx], radii

segments = {sid: load_segment(sid) for sid in SEG_IDS}
seg_volumes = {sid: mesh_volume(*segments[sid]) for sid in SEG_IDS}
seg_trees = {sid: cKDTree(segments[sid][0]) for sid in SEG_IDS}

print("Segment volumes (mm^3):")
for sid in SEG_IDS:
    print(f"  {sid}: {seg_volumes[sid]:,.0f}")

portal_terminal, portal_trunk, _, _ = get_terminal_leaves('vessel_portal.json')
arterial_terminal, arterial_trunk, _, _ = get_terminal_leaves('vessel_arterial.json')
hepatic_terminal, hepatic_trunk, _, _ = get_terminal_leaves('vessel_hepatic.json')

print(f"\nportal: {len(portal_terminal)} terminal leaves, {len(portal_trunk)} trunk-excluded")
print(f"arterial: {len(arterial_terminal)} terminal leaves, {len(arterial_trunk)} trunk-excluded")
print(f"hepatic vein: {len(hepatic_terminal)} terminal leaves, {len(hepatic_trunk)} trunk-excluded")

seg_of_seed = []
for p in portal_terminal:
    dists = {sid: seg_trees[sid].query(p, k=1)[0] for sid in SEG_IDS}
    best = min(dists, key=dists.get)
    seg_of_seed.append((best, dists[best]))

print("\nPortal seeds per segment:")
from collections import Counter
cnt = Counter(s for s,_ in seg_of_seed)
for sid in SEG_IDS:
    print(f"  {sid}: {cnt.get(sid,0)} seeds")

print("\nseed-to-segment distance stats:",
      "min", min(d for _,d in seg_of_seed),
      "median", np.median([d for _,d in seg_of_seed]),
      "max", max(d for _,d in seg_of_seed))
