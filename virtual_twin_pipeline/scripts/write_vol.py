"""
Minimal writer for the DGtal ".vol" volumetric image format used by
OpenCCO's --organDomain option: ASCII header (key: value lines, terminated
by a line containing just "."), followed by zlib-compressed raw voxel
bytes in X-fastest, then Y, then Z order (row-major, matching DGtal's
default ImageContainerBySTLVector iteration for a Z3i::Domain).
"""
import zlib
import numpy as np


def write_vol(path, volume_u8, center=(0, 0, 0), voxel_size=1):
    """volume_u8: numpy array of shape (X, Y, Z), dtype uint8."""
    X, Y, Z = volume_u8.shape
    header = (
        f"Center-X: {center[0]}\n"
        f"Center-Y: {center[1]}\n"
        f"Center-Z: {center[2]}\n"
        f"X: {X}\n"
        f"Y: {Y}\n"
        f"Z: {Z}\n"
        f"Voxel-Size: {voxel_size}\n"
        f"Alpha-Color: 0\n"
        f"Voxel-Endian: 0\n"
        f"Int-Endian: 0123\n"
        f"Version: 3\n"
        f".\n"
    ).encode("ascii")
    # DGtal iterates domain points with X varying fastest (matches the
    # bunny sample: dims X=323,Y=320,Z=228 map to X-fastest raster order)
    raw = volume_u8.transpose(2, 1, 0).tobytes(order="C")  # Z,Y,X -> flat, X fastest
    compressed = zlib.compress(raw, level=6)
    with open(path, "wb") as f:
        f.write(header)
        f.write(compressed)


def read_vol(path):
    with open(path, "rb") as f:
        data = f.read()
    text, _, rest = data.partition(b".\n")
    header = {}
    for line in text.decode("ascii").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            header[k.strip()] = v.strip()
    X, Y, Z = int(header["X"]), int(header["Y"]), int(header["Z"])
    raw = zlib.decompress(rest)
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(Z, Y, X)
    return arr.transpose(2, 1, 0), header  # back to (X,Y,Z)


def read_vol_header(path):
    with open(path, "rb") as f:
        data = f.read(2048)
    text, _, rest = data.partition(b".\n")
    header = {}
    for line in text.decode("ascii").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            header[k.strip()] = v.strip()
    return header
