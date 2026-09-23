import json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

def load(name):
    d = json.load(open(name))
    pos = np.array(d['positions']).reshape(-1,3)
    idx = np.array(d['indices']).reshape(-1,3)
    return pos, idx

def tubelet_components(pos, idx):
    n = len(pos)
    rows, cols = [], []
    for tri in idx:
        for a,b in [(0,1),(1,2),(2,0)]:
            rows.append(tri[a]); cols.append(tri[b])
            rows.append(tri[b]); cols.append(tri[a])
    g = coo_matrix((np.ones(len(rows)),(rows,cols)), shape=(n,n)).tocsr()
    ncomp, labels = connected_components(g, directed=False)
    comps = [[] for _ in range(ncomp)]
    for i,l in enumerate(labels):
        comps[l].append(i)
    return comps

def tubelet_endpoints(pts, band=25):
    centroid = pts.mean(axis=0)
    u,s,vt = np.linalg.svd(pts - centroid)
    axis = vt[0]
    proj = (pts - centroid) @ axis
    lo, hi = np.percentile(proj, [band, 100-band])
    endA = pts[proj <= lo].mean(axis=0)
    endB = pts[proj >= hi].mean(axis=0)
    return endA, endB

def build_skeleton(name, bridge_radius=1.5):
    pos, idx = load(name)
    comps = tubelet_components(pos, idx)
    endpoints = []   # list of 3D points, 2 per tubelet
    edge_tubelet_idx = []  # (endpointA_global_idx, endpointB_global_idx)
    for c in comps:
        pts = pos[np.array(c)]
        a,b = tubelet_endpoints(pts)
        ia = len(endpoints); endpoints.append(a)
        ib = len(endpoints); endpoints.append(b)
        edge_tubelet_idx.append((ia, ib))
    endpoints = np.array(endpoints)

    tree = cKDTree(endpoints)
    pairs = tree.query_pairs(r=bridge_radius)
    m = len(endpoints)
    rows, cols = [], []
    for i,j in pairs:
        rows.append(i); cols.append(j)
        rows.append(j); cols.append(i)
    gcoo = coo_matrix((np.ones(len(rows)) if rows else [], (rows, cols)), shape=(m,m)).tocsr() if rows else coo_matrix((m,m)).tocsr()
    ncomp, labels = connected_components(gcoo, directed=False)

    node_pos = np.zeros((ncomp,3))
    counts = np.zeros(ncomp)
    for i in range(m):
        node_pos[labels[i]] += endpoints[i]
        counts[labels[i]] += 1
    node_pos /= counts[:,None]

    edges = set()
    for ia, ib in edge_tubelet_idx:
        na, nb = labels[ia], labels[ib]
        if na != nb:
            edges.add((min(na,nb), max(na,nb)))
    degree = np.zeros(ncomp, dtype=int)
    for a,b in edges:
        degree[a]+=1; degree[b]+=1

    return {
        'node_pos': node_pos,
        'edges': list(edges),
        'degree': degree,
        'n_tubelets': len(comps),
    }

if __name__ == '__main__':
    for name in ['vessel_portal.json','vessel_arterial.json','vessel_hepatic.json','vessel_bile.json']:
        sk = build_skeleton(name)
        deg = sk['degree']
        print(name, 'tubelets=', sk['n_tubelets'], 'nodes=', len(deg), 'leaves(deg1)=', int((deg==1).sum()),
              'deg2=', int((deg==2).sum()), 'branch(deg>=3)=', int((deg>=3).sum()), 'deg0(isolated)=', int((deg==0).sum()))

def build_skeleton_with_radius(name, bridge_radius=4.0):
    pos, idx = load(name)
    comps = tubelet_components(pos, idx)
    endpoints = []
    edge_tubelet_idx = []
    tubelet_radius = []
    for c in comps:
        pts = pos[np.array(c)]
        a,b = tubelet_endpoints(pts)
        centroid = pts.mean(axis=0)
        u,s,vt = np.linalg.svd(pts-centroid)
        axis = vt[0]
        proj = (pts-centroid)@axis
        perp = pts - centroid - np.outer(proj, axis)
        radial = np.linalg.norm(perp,axis=1).mean()
        ia = len(endpoints); endpoints.append(a)
        ib = len(endpoints); endpoints.append(b)
        edge_tubelet_idx.append((ia, ib))
        tubelet_radius.append(radial)
    endpoints = np.array(endpoints)
    tubelet_radius = np.array(tubelet_radius)

    tree = cKDTree(endpoints)
    pairs = tree.query_pairs(r=bridge_radius)
    m = len(endpoints)
    rows, cols = [], []
    for i,j in pairs:
        rows.append(i); cols.append(j)
        rows.append(j); cols.append(i)
    gcoo = coo_matrix((np.ones(len(rows)) if rows else [], (rows, cols)), shape=(m,m)).tocsr() if rows else coo_matrix((m,m)).tocsr()
    ncomp, labels = connected_components(gcoo, directed=False)

    node_pos = np.zeros((ncomp,3))
    counts = np.zeros(ncomp)
    for i in range(m):
        node_pos[labels[i]] += endpoints[i]
        counts[labels[i]] += 1
    node_pos /= counts[:,None]

    edges = []
    for (ia, ib), rad in zip(edge_tubelet_idx, tubelet_radius):
        na, nb = labels[ia], labels[ib]
        if na != nb:
            edges.append((na, nb, rad))
    degree = np.zeros(ncomp, dtype=int)
    max_incident_radius = np.zeros(ncomp)
    for a,b,rad in edges:
        degree[a]+=1; degree[b]+=1
        max_incident_radius[a] = max(max_incident_radius[a], rad)
        max_incident_radius[b] = max(max_incident_radius[b], rad)

    return {
        'node_pos': node_pos,
        'edges': edges,
        'degree': degree,
        'max_incident_radius': max_incident_radius,
        'n_tubelets': len(comps),
    }
