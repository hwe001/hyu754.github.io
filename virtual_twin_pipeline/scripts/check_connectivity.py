import json, sys
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

data = json.load(open('opencco_s2s3.json'))

for t in data:
    pts = []
    for distal, proximal, r in t['edges_mm']:
        pts.append(distal)
        pts.append(proximal)
    pts = np.array(pts)
    n = len(pts)
    tree = cKDTree(pts)
    pairs = tree.query_pairs(r=0.05)
    print(f"territory {t['territory']}: n_points={n} n_pairs_found={len(pairs)}", end=" ")
    rows, cols = [], []
    for i, j in pairs:
        rows.append(i); rows.append(j)
        cols.append(j); cols.append(i)
    if rows:
        g = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n)).tocsr()
    else:
        g = coo_matrix((n, n))
    ncomp, labels = connected_components(g, directed=False)
    sizes = np.bincount(labels)
    print(f"-> ncomp={ncomp} largest={sizes.max()}")
