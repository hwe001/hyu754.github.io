import json, time
import numpy as np
import trimesh
import sys
sys.path.insert(0, '.')
from write_vol import write_vol

def load_segment(sid):
    d = json.load(open(f"{sid}.json"))
    pos = np.array(d['positions']).reshape(-1, 3)
    idx = np.array(d['indices']).reshape(-1, 3)
    return pos, idx

meshes = {}
for sid in ['S2', 'S3']:
    pos, idx = load_segment(sid)
    meshes[sid] = trimesh.Trimesh(vertices=pos, faces=idx, process=False)

allpts = np.vstack([meshes['S2'].vertices, meshes['S3'].vertices])
bbmin, bbmax = allpts.min(axis=0) - 3, allpts.max(axis=0) + 3  # 3mm padding
VOXEL = 1.5
dims = np.ceil((bbmax - bbmin) / VOXEL).astype(int)
print("voxel grid dims (X,Y,Z):", dims, "-> ", np.prod(dims), "voxels")

xs = bbmin[0] + (np.arange(dims[0]) + 0.5) * VOXEL
ys = bbmin[1] + (np.arange(dims[1]) + 0.5) * VOXEL
zs = bbmin[2] + (np.arange(dims[2]) + 0.5) * VOXEL
gx, gy, gz = np.meshgrid(xs, ys, zs, indexing='ij')
grid_pts = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
print("total query points:", len(grid_pts))

def inside_batched(pts, batch=2000):
    out = np.zeros(len(pts), dtype=bool)
    for i in range(0, len(pts), batch):
        chunk = pts[i:i+batch]
        in2 = meshes['S2'].contains(chunk)
        in3 = meshes['S3'].contains(chunk)
        out[i:i+batch] = in2 | in3
        if i % 40000 == 0:
            print(f"  {i}/{len(pts)}  {time.time()-t0:.0f}s")
    return out

t0 = time.time()
inside = inside_batched(grid_pts)
print(f"done in {time.time()-t0:.0f}s, inside={inside.sum()}/{len(inside)}")

volume = np.zeros(dims, dtype=np.uint8)
volume[inside.reshape(dims)] = 255

np.savez('s2s3_voxel_meta.npz', bbmin=bbmin, voxel_size=VOXEL, dims=dims)
write_vol('s2s3_domain.vol', volume, center=(0, 0, 0), voxel_size=1)
print("wrote s2s3_domain.vol")
