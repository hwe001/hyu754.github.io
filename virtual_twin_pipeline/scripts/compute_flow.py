"""
Flow/pressure solve on the real+synthetic S2/S3 portal network.

OpenCCO's own XML carries flow/pressure/resistance attributes, but they are
literally the tool's coronary-artery demo defaults (my_pPerf=13300,
my_pTerm=8400, my_qPerf=8330 -- unchanged regardless of -a/-n input, visible
verbatim in CoronaryArteryTree.h), not physically meaningful for a portal
venous liver network. So: keep OpenCCO's geometrically-optimized radii
(those ARE real, Poiseuille/Murray's-law-consistent), but independently
assign flow and solve pressure using real portal-vein physiology:

  - each territory's root gets an inlet flow proportional to its share of
    total liver volume (uniform-perfusion-per-volume assumption, absent
    perfusion imaging), out of a literature total portal flow
  - flow splits equally across a territory's own terminals (the standard
    CCO/Kamiya assumption -- same one OpenCCO itself uses internally)
  - resistance per segment via the standard Poiseuille law using each
    segment's REAL mm length/radius and a literature blood viscosity
  - pressure integrated top-down from a literature portal pressure at the
    root: P(child) = P(parent) - Q_segment * R_segment
"""
import json, sys
import numpy as np
sys.path.insert(0, '.')
from xml_helpers import parse_opencco_xml

# --- literature physiological parameters (flag: verify/cite before publication) ---
TOTAL_PORTAL_FLOW_ML_MIN = 1100.0     # typical resting adult portal venous flow
PORTAL_PRESSURE_MMHG = 7.0            # typical normal portal venous pressure
BLOOD_VISCOSITY_PAS = 3.6e-3          # Pa.s -- same value OpenCCO itself uses internally

MMHG_TO_PA = 133.322
ML_MIN_TO_M3_S = 1e-6 / 60.0

meta = np.load('s2s3_voxel_meta.npz')
bbmin = meta['bbmin']
VOXEL = float(meta['voxel_size'])

roots_data = json.load(open('s2s3_roots.json'))
roots = roots_data['roots']

# total liver volume (all 8 Couinaud segments), computed once for the flow allocation
total_liver_vol = 0.0
for i in range(1, 9):
    d = json.load(open(f"S{i}.json"))
    pos = np.array(d['positions']).reshape(-1, 3)
    idx = np.array(d['indices']).reshape(-1, 3)
    v0, v1, v2 = pos[idx[:, 0]], pos[idx[:, 1]], pos[idx[:, 2]]
    total_liver_vol += abs(np.sum(np.einsum('ij,ij->i', v0, np.cross(v1, v2))) / 6.0)
print(f"total liver volume: {total_liver_vol:,.0f} mm^3")

# recompute per-territory volumes and local_bbmin_mm exactly as run_opencco.py did
from scipy.spatial import cKDTree
volume, header = None, None
from write_vol import read_vol
vol_arr, _ = read_vol('s2s3_domain.vol')
inside_mask = vol_arr > 128
ix, iy, iz = np.where(inside_mask)
centers_mm = bbmin + (np.stack([ix, iy, iz], axis=1) + 0.5) * VOXEL
root_pos = np.array([r['pos'] for r in roots])
root_tree = cKDTree(root_pos)
_, nearest_root = root_tree.query(centers_mm, k=1)
n_roots = len(roots)
territory_voxel_count = np.bincount(nearest_root, minlength=n_roots)
territory_volume_mm3 = territory_voxel_count * (VOXEL ** 3)

results = []
terminal_summary = []

for i, r in enumerate(roots):
    xml_path = f'territory_{i}.xml'
    node_pos, xml_edges = parse_opencco_xml(xml_path)

    sel = (nearest_root == i)
    vox_idx = np.stack([ix[sel], iy[sel], iz[sel]], axis=1)
    local_min = vox_idx.min(axis=0)
    pad = 2
    local_bbmin_mm = bbmin + (local_min - pad) * VOXEL

    # real mm position per node id
    pos_mm = {nid: (local_bbmin_mm + np.array(p) * VOXEL) for nid, p in node_pos.items()}

    children = {}
    parent_of = {}
    radius_mm = {}
    for from_id, to_id, rad in xml_edges:
        children.setdefault(from_id, []).append(to_id)
        parent_of[to_id] = from_id
        radius_mm[to_id] = rad * VOXEL

    all_ids = set(node_pos.keys())
    terminal_ids = sorted(nid for nid in all_ids if nid not in children and nid in parent_of)
    n_term = len(terminal_ids)

    Q_root = TOTAL_PORTAL_FLOW_ML_MIN * (territory_volume_mm3[i] / total_liver_vol)
    q_term = Q_root / n_term
    print(f"territory {i} ({r['segment']}): n_term={n_term} Q_root={Q_root:.3f} mL/min "
          f"q_term={q_term:.5f} mL/min/terminal")

    # bottom-up: count terminal descendants per node (post-order via iterative stack)
    n_desc = {}
    def count_descendants(nid):
        if nid not in children:
            n_desc[nid] = 1
            return 1
        total = sum(count_descendants(c) for c in children[nid])
        n_desc[nid] = total
        return total
    sys.setrecursionlimit(20000)
    count_descendants(0)

    # flow and resistance per edge (edge identified by its "to" node id)
    flow_ml_min = {}
    resistance_pa_s_m3 = {}
    for from_id, to_id, rad in xml_edges:
        flow_ml_min[to_id] = q_term * n_desc[to_id]
        L_m = np.linalg.norm(pos_mm[to_id] - pos_mm[from_id]) * 1e-3
        r_m = max(radius_mm[to_id], 1e-3) * 1e-3
        resistance_pa_s_m3[to_id] = 8.0 * BLOOD_VISCOSITY_PAS * L_m / (np.pi * r_m ** 4)

    # pressure top-down from root
    pressure_pa = {0: PORTAL_PRESSURE_MMHG * MMHG_TO_PA}
    order = [0]
    qi = 0
    while qi < len(order):
        nid = order[qi]; qi += 1
        for c in children.get(nid, []):
            Q_m3s = flow_ml_min[c] * ML_MIN_TO_M3_S
            dP = Q_m3s * resistance_pa_s_m3[c]
            pressure_pa[c] = pressure_pa[nid] - dP
            order.append(c)

    edges_out = []
    for from_id, to_id, rad in xml_edges:
        edges_out.append({
            'distal_mm': pos_mm[to_id].tolist(),
            'proximal_mm': pos_mm[from_id].tolist(),
            'radius_mm': radius_mm[to_id],
            'flow_ml_min': flow_ml_min[to_id],
            'pressure_distal_mmHg': pressure_pa[to_id] / MMHG_TO_PA,
            'pressure_proximal_mmHg': pressure_pa[from_id] / MMHG_TO_PA,
        })

    # root connector (real measured terminal -> OpenCCO's own node 0)
    root_mm = np.array(r['pos'])
    n0_mm = pos_mm[0]
    if np.linalg.norm(n0_mm - root_mm) > 0.5:
        edges_out.append({
            'distal_mm': n0_mm.tolist(), 'proximal_mm': root_mm.tolist(),
            'radius_mm': r['measured_radius'],
            'flow_ml_min': Q_root,
            'pressure_distal_mmHg': pressure_pa[0] / MMHG_TO_PA,
            'pressure_proximal_mmHg': pressure_pa[0] / MMHG_TO_PA,
        })

    for tid in terminal_ids:
        terminal_summary.append({
            'territory': i, 'segment': r['segment'], 'node_id': tid,
            'pos_mm': pos_mm[tid].tolist(),
            'radius_mm': radius_mm[tid],
            'flow_ml_min': flow_ml_min[tid],
            'pressure_mmHg': pressure_pa[tid] / MMHG_TO_PA,
        })

    results.append({
        'territory': i, 'segment': r['segment'], 'root_pos': r['pos'],
        'measured_root_radius': r['measured_radius'],
        'target_terminal': n_term, 'territory_volume_mm3': float(territory_volume_mm3[i]),
        'Q_root_ml_min': Q_root, 'P_root_mmHg': PORTAL_PRESSURE_MMHG,
        'edges': edges_out,
    })

json.dump(results, open('opencco_s2s3_flow.json', 'w'))
json.dump(terminal_summary, open('meso_unit_terminals.json', 'w'), indent=1)
print(f"\nsaved opencco_s2s3_flow.json ({sum(len(t['edges']) for t in results)} edges) "
      f"and meso_unit_terminals.json ({len(terminal_summary)} meso-unit boundary conditions)")

qs = np.array([t['flow_ml_min'] for t in terminal_summary])
ps = np.array([t['pressure_mmHg'] for t in terminal_summary])
print(f"\nmeso-unit terminal flow: min={qs.min():.5f} median={np.median(qs):.5f} max={qs.max():.5f} mL/min")
print(f"meso-unit terminal pressure: min={ps.min():.3f} median={np.median(ps):.3f} max={ps.max():.3f} mmHg")
