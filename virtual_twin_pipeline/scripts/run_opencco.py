import json, subprocess, sys
import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, '.')
from write_vol import write_vol, read_vol


def parse_opencco_xml(path):
    """OpenCCO's -e/.txt exporter has a real bug: it looks up each segment's
    parent coordinate by indexing myVectSegments[myVectParent[idx]] as a raw
    array position, which does not reliably track the parent's actual
    identity as the tree grows via bifurcation -- this fragments the
    exported tree into hundreds of disconnected mini-clusters. The -x/.xml
    exporter is architected correctly: every node is referenced by an
    explicit id, and edges carry from/to ids resolved through that id table.
    Parse the XML instead; it round-trips as a single connected tree."""
    root = ET.parse(path).getroot()
    graph = root.find('graph')
    node_pos = {}
    for node in graph.findall('node'):
        nid = int(node.get('id')[1:])
        floats = node.find(".//attr[@name=' position']/tup").findall('float')
        node_pos[nid] = tuple(float(f.text) for f in floats)
    edges = []
    for edge in graph.findall('edge'):
        eid = int(edge.get('id')[1:])
        to_id = int(edge.get('to')[1:])
        from_id = int(edge.get('from')[1:])
        radius = float(edge.find(".//attr[@name=' radius']/float").text)
        edges.append((from_id, to_id, radius))
    return node_pos, edges

OPENCCO_BIN = '/tmp/OpenCCO/build/bin/generateTree3D'
TARGET_TERMINAL_VOL = 50.0  # mm^3 per synthetic terminal -- pushed dense for 10+ generation trees

meta = np.load('s2s3_voxel_meta.npz')
bbmin = meta['bbmin']
VOXEL = float(meta['voxel_size'])
dims = meta['dims']

volume, header = read_vol('s2s3_domain.vol')
inside_mask = volume > 128
print(f"domain grid dims={dims} voxel={VOXEL}mm total_inside={inside_mask.sum()}")

roots_data = json.load(open('s2s3_roots.json'))
roots = roots_data['roots']
root_pos = np.array([r['pos'] for r in roots])
n_roots = len(root_pos)
root_tree = cKDTree(root_pos)

# voxel centers (real mm) for every inside voxel
ix, iy, iz = np.where(inside_mask)
centers_mm = bbmin + (np.stack([ix, iy, iz], axis=1) + 0.5) * VOXEL
_, nearest_root = root_tree.query(centers_mm, k=1)

territory_voxel_count = np.bincount(nearest_root, minlength=n_roots)
territory_volume_mm3 = territory_voxel_count * (VOXEL ** 3)
for i, r in enumerate(roots):
    print(f"  root {i} ({r['segment']}, node {r['node']}): "
          f"voxels={territory_voxel_count[i]} volume={territory_volume_mm3[i]:,.0f}mm^3")

results = []
for i, r in enumerate(roots):
    sel = (nearest_root == i)
    if sel.sum() < 5:
        print(f"root {i}: too few voxels ({sel.sum()}), skipping")
        continue
    vox_idx = np.stack([ix[sel], iy[sel], iz[sel]], axis=1)
    local_min = vox_idx.min(axis=0)
    local_max = vox_idx.max(axis=0)
    pad = 2
    local_dims = (local_max - local_min) + 1 + 2 * pad
    local_vol = np.zeros(tuple(local_dims), dtype=np.uint8)
    shifted = vox_idx - local_min + pad
    local_vol[shifted[:, 0], shifted[:, 1], shifted[:, 2]] = 255

    local_bbmin_mm = bbmin + (local_min - pad) * VOXEL
    vol_path = f'territory_{i}.vol'
    # DGtal's VolReader places the domain's first point at
    # Center - (dim-1)//2, NOT at index (0,0,0), for whatever Center is
    # given. To make index (0,0,0) land exactly at local_bbmin_mm (as the
    # rest of this script assumes), Center must be set to (dim-1)//2.
    vol_center = tuple(((np.array(local_dims) - 1) // 2).tolist())
    write_vol(vol_path, local_vol, center=vol_center, voxel_size=1)

    root_mm = np.array(r['pos'])
    root_idx = np.round((root_mm - local_bbmin_mm) / VOXEL).astype(int)
    root_idx = np.clip(root_idx, [0, 0, 0], np.array(local_dims) - 1)
    if local_vol[root_idx[0], root_idx[1], root_idx[2]] < 128:
        # snap to nearest inside voxel
        d = np.linalg.norm(shifted - root_idx, axis=1)
        nn = shifted[np.argmin(d)]
        root_idx = nn

    territory_vol_voxels = int(sel.sum())
    n_term = max(2, min(2000, round(territory_volume_mm3[i] / TARGET_TERMINAL_VOL)))

    xml_path = f'territory_{i}.xml'
    off_path = f'territory_{i}.off'
    cmd = [OPENCCO_BIN, '-n', str(n_term), '-a', str(territory_vol_voxels),
           '-d', vol_path, '-m', '1',
           '-p', str(root_idx[0]), str(root_idx[1]), str(root_idx[2]),
           '-o', off_path, '-x', xml_path]
    print(f"\nroot {i} ({r['segment']}): n_term={n_term} aPerf={territory_vol_voxels} "
          f"root_idx={root_idx.tolist()} domain_dims={local_dims.tolist()}")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(f"  exit={proc.returncode} stderr={proc.stderr[-200:] if proc.stderr else ''}")

    try:
        node_pos, xml_edges = parse_opencco_xml(xml_path)
    except FileNotFoundError:
        print(f"  WARNING: no output for root {i}")
        continue

    edges_mm = []
    for from_id, to_id, rad in xml_edges:
        distal_mm = local_bbmin_mm + np.array(node_pos[to_id]) * VOXEL
        proximal_mm = local_bbmin_mm + np.array(node_pos[from_id]) * VOXEL
        edges_mm.append([distal_mm.tolist(), proximal_mm.tolist(), rad * VOXEL])

    # node 0 is OpenCCO's own internal root point, which it may snap a
    # little from the requested -p for domain/border validity. Bridge the
    # (usually sub-mm to few-mm) gap between that and our real measured
    # terminal with a connector edge, using the measured root radius.
    if edges_mm and 0 in node_pos:
        n0_mm = local_bbmin_mm + np.array(node_pos[0]) * VOXEL
        if np.linalg.norm(n0_mm - root_mm) > 0.5:
            edges_mm.append([n0_mm.tolist(), root_mm.tolist(), r['measured_radius']])

    print(f"  parsed {len(edges_mm)} segments from OpenCCO XML output (incl. root connector)")
    results.append({
        'territory': i, 'segment': r['segment'], 'root_pos': r['pos'],
        'measured_root_radius': r['measured_radius'],
        'target_terminal': n_term, 'territory_volume_mm3': float(territory_volume_mm3[i]),
        'edges_mm': edges_mm,
    })

json.dump(results, open('opencco_s2s3.json', 'w'))
print(f"\nsaved opencco_s2s3.json with {len(results)} territories")
