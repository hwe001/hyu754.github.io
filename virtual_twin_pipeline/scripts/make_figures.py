"""
Generate static publication figures for PAPER_DRAFT.md from the real
pipeline data in virtual_twin_pipeline/data/. Run from the scripts/
directory: python3 make_figures.py
Outputs PNGs into ../figures/.
"""
import json
import os
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.linewidth": 0.6,
})

SEGMENT_COLORS = {
    "S1": "#9e9e9e", "S2": "#4e79a7", "S3": "#f28e2b", "S4": "#e15759",
    "S5": "#76b7b2", "S6": "#59a14f", "S7": "#edc948", "S8": "#b07aa1",
}


def load_mesh(name, target_faces=3000):
    d = json.load(open(os.path.join(DATA, f"{name}.json")))
    v = np.array(d["positions"]).reshape(-1, 3)
    f = np.array(d["indices"]).reshape(-1, 3)
    m = trimesh.Trimesh(vertices=v, faces=f, process=False)
    if len(m.faces) > target_faces:
        m = m.simplify_quadric_decimation(face_count=target_faces)
    return m


def add_mesh_to_ax(ax, mesh, color, alpha=0.55, edgecolor="none", lw=0.0):
    tris = mesh.vertices[mesh.faces]
    pc = Poly3DCollection(tris, facecolor=color, alpha=alpha,
                           edgecolor=edgecolor, linewidths=lw)
    ax.add_collection3d(pc)


def set_equal_aspect(ax, all_verts):
    pts = np.vstack(all_verts)
    mins, maxs = pts.min(0), pts.max(0)
    ctr = (mins + maxs) / 2
    r = (maxs - mins).max() / 2 * 1.05
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)


# ---------------------------------------------------------------------
# Figure 0: full original atlas -- liver segments + all four vessel trees
# ---------------------------------------------------------------------
def fig0_atlas():
    fig = plt.figure(figsize=(7.5, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    all_v = []

    for s in ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]:
        m = load_mesh(s, target_faces=1500)
        add_mesh_to_ax(ax, m, SEGMENT_COLORS[s], alpha=0.12, edgecolor="none")
        all_v.append(m.vertices)

    trees = {
        "vessel_portal": ("Portal vein", "#377eb8"),
        "vessel_arterial": ("Hepatic artery", "#e41a1c"),
        "vessel_hepatic": ("Hepatic vein", "#4a2377"),
        "vessel_bile": ("Biliary tree", "#2c8a3d"),
    }
    handles = []
    for fname, (label, color) in trees.items():
        d = json.load(open(os.path.join(DATA, f"{fname}.json")))
        v = np.array(d["positions"]).reshape(-1, 3)
        f = np.array(d["indices"]).reshape(-1, 3)
        m = trimesh.Trimesh(vertices=v, faces=f, process=False)
        add_mesh_to_ax(ax, m, color, alpha=0.95, edgecolor="none")
        all_v.append(m.vertices)
        handles.append(plt.Line2D([0], [0], color=color, lw=4, label=label))

    handles += [plt.Line2D([0], [0], marker="s", color="w",
                            markerfacecolor="gray", alpha=0.3, markersize=10,
                            label="Couinaud segments\n(translucent)")]

    set_equal_aspect(ax, all_v)
    ax.view_init(elev=15, azim=-60)
    ax.set_axis_off()
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.0, 0.5),
              frameon=False, fontsize=9)
    ax.set_title("Full source atlas: whole-liver segmentation with all\nfour patient-specific vascular/biliary tree structures",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig0_atlas_overview.png"), dpi=300,
                bbox_inches="tight")
    plt.close(fig)
    print("fig0 done")


# ---------------------------------------------------------------------
# Figure 1: whole-liver 8-segment model
# ---------------------------------------------------------------------
def fig1_segments():
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    all_v = []
    meshes = {}
    for s in ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]:
        m = load_mesh(s, target_faces=2500)
        meshes[s] = m
        add_mesh_to_ax(ax, m, SEGMENT_COLORS[s], alpha=0.85)
        all_v.append(m.vertices)
    set_equal_aspect(ax, all_v)
    ax.view_init(elev=15, azim=-60)
    ax.set_axis_off()
    handles = [plt.Line2D([0], [0], marker="s", color="w",
                           markerfacecolor=SEGMENT_COLORS[s], markersize=10,
                           label=f"Segment {s[1:]}") for s in SEGMENT_COLORS]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.0, 0.5),
               frameon=False, fontsize=9)
    ax.set_title("Whole-liver Couinaud segmentation (8 segments,\npost Segment I/IX merge)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_couinaud_segments.png"), dpi=300,
                bbox_inches="tight")
    plt.close(fig)
    print("fig1 done")


# ---------------------------------------------------------------------
# Figure 2: portal vessel tree with trunk / S2-S3 roots highlighted
# ---------------------------------------------------------------------
def fig2_portal_tree():
    d = json.load(open(os.path.join(DATA, "vessel_portal.json")))
    v = np.array(d["positions"]).reshape(-1, 3)
    f = np.array(d["indices"]).reshape(-1, 3)
    m = trimesh.Trimesh(vertices=v, faces=f, process=False)
    if len(m.faces) > 6000:
        m = m.simplify_quadric_decimation(face_count=6000)

    roots = json.load(open(os.path.join(DATA, "s2s3_roots.json")))

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh_to_ax(ax, m, "#8c2d24", alpha=0.9, edgecolor="none")

    trunk = np.array(roots["trunk_pos"])
    ancestor = np.array(roots["left_portal_ancestor_pos"])
    root_pts = np.array([r["pos"] for r in roots["roots"]])

    ax.scatter(*trunk, color="black", s=90, marker="*",
               label="Main portal trunk", depthshade=False)
    ax.scatter(*ancestor, color="#1b9e77", s=70, marker="D",
               label="Left portal branch\n(common ancestor)", depthshade=False)
    ax.scatter(root_pts[:, 0], root_pts[:, 1], root_pts[:, 2],
               color="#377eb8", s=60, marker="o",
               label="Confirmed S2/S3 terminal\nroots (n=6)", depthshade=False)

    set_equal_aspect(ax, [m.vertices, root_pts[None, :, 0].reshape(-1,3) if False else root_pts])
    ax.view_init(elev=15, azim=-60)
    ax.set_axis_off()
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=9)
    ax.set_title("Real portal vein tree: topology-based identification\nof segment II/III terminal roots",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_portal_tree_roots.png"), dpi=300,
                bbox_inches="tight")
    plt.close(fig)
    print("fig2 done")


# ---------------------------------------------------------------------
# Figure 3: S2/S3 domain with roots + Voronoi territory assignment
# ---------------------------------------------------------------------
def fig3_territories():
    flow = json.load(open(os.path.join(DATA, "opencco_s2s3_flow.json")))
    roots = json.load(open(os.path.join(DATA, "s2s3_roots.json")))["roots"]

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")

    m2 = load_mesh("S2", target_faces=2000)
    m3 = load_mesh("S3", target_faces=2000)
    add_mesh_to_ax(ax, m2, SEGMENT_COLORS["S2"], alpha=0.15)
    add_mesh_to_ax(ax, m3, SEGMENT_COLORS["S3"], alpha=0.15)

    palette = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628"]
    all_v = [m2.vertices, m3.vertices]
    for i, terr in enumerate(flow):
        edges = terr["edges"]
        segs = np.array([[e["proximal_mm"], e["distal_mm"]] for e in edges])
        for seg in segs:
            ax.plot(seg[:, 0], seg[:, 1], seg[:, 2], color=palette[i % 6],
                    linewidth=0.4, alpha=0.6)
        all_v.append(segs.reshape(-1, 3))
        rp = np.array(terr["root_pos"])
        ax.scatter(*rp, color=palette[i % 6], s=70, marker="o",
                   edgecolor="black", linewidth=0.5, zorder=5)

    set_equal_aspect(ax, all_v)
    ax.view_init(elev=15, azim=-60)
    ax.set_axis_off()
    handles = [plt.Line2D([0], [0], color=palette[i % 6], lw=2,
                           label=f"Territory {i} ({flow[i]['segment']}, "
                                 f"{flow[i]['target_terminal']} terminals)")
               for i in range(len(flow))]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.0, 0.5),
               frameon=False, fontsize=8)
    ax.set_title("Six Voronoi perfusion territories seeded from the\nconfirmed real S2/S3 terminal roots",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig3_territories.png"), dpi=300,
                bbox_inches="tight")
    plt.close(fig)
    print("fig3 done")


# ---------------------------------------------------------------------
# Figure 4: dense OpenCCO synthetic trees, real trunk overlay
# ---------------------------------------------------------------------
def fig4_synthetic_trees():
    flow = json.load(open(os.path.join(DATA, "opencco_s2s3_flow.json")))

    fig = plt.figure(figsize=(7.5, 6.5))
    ax = fig.add_subplot(111, projection="3d")

    m2 = load_mesh("S2", target_faces=1500)
    m3 = load_mesh("S3", target_faces=1500)
    add_mesh_to_ax(ax, m2, SEGMENT_COLORS["S2"], alpha=0.08)
    add_mesh_to_ax(ax, m3, SEGMENT_COLORS["S3"], alpha=0.08)

    all_v = [m2.vertices, m3.vertices]
    palette = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628"]
    total_terms = 0
    total_segs = 0
    for i, terr in enumerate(flow):
        edges = terr["edges"]
        total_segs += len(edges)
        radii = np.array([e["radius_mm"] for e in edges])
        lw = np.clip(radii * 3.0, 0.15, 3.0)
        for e, w in zip(edges, lw):
            p, dpt = np.array(e["proximal_mm"]), np.array(e["distal_mm"])
            ax.plot([p[0], dpt[0]], [p[1], dpt[1]], [p[2], dpt[2]],
                    color=palette[i % 6], linewidth=w, alpha=0.85)
        all_v.append(np.array([e["distal_mm"] for e in edges]))

    set_equal_aspect(ax, all_v)
    ax.view_init(elev=12, azim=-55)
    ax.set_axis_off()
    n_terms = sum(t["target_terminal"] for t in flow)
    ax.set_title(f"Dense OpenCCO synthetic vasculature grown from 6 real\n"
                 f"terminal roots ({n_terms:,} synthetic terminals, {total_segs:,} vascular segments)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig4_opencco_synthetic_trees.png"), dpi=300,
                bbox_inches="tight")
    plt.close(fig)
    print("fig4 done")


# ---------------------------------------------------------------------
# Figure 5: flow / pressure summary
# ---------------------------------------------------------------------
def fig5_flow_pressure():
    flow = json.load(open(os.path.join(DATA, "opencco_s2s3_flow.json")))

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))

    labels = [f"T{t['territory']}\n({t['segment']})" for t in flow]
    q = [t["Q_root_ml_min"] for t in flow]
    vol = [t["territory_volume_mm3"] for t in flow]
    palette = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628"]

    ax = axes[0]
    ax.bar(labels, q, color=palette)
    ax.set_ylabel("Root inlet flow (mL min$^{-1}$)")
    ax.set_title("(a) Territory inlet flow")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    all_p = []
    for i, t in enumerate(flow):
        p_term = [e["pressure_distal_mmHg"] for e in t["edges"]]
        all_p.append(p_term)
    bp = ax.boxplot(all_p, tick_labels=[f"T{t['territory']}" for t in flow],
                     showfliers=False, patch_artist=True)
    for patch, c in zip(bp["boxes"], palette):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)
    ax.axhline(7.0, color="black", linestyle="--", linewidth=0.8,
               label="Root pressure (7 mmHg)")
    ax.set_ylabel("Distal segment pressure (mmHg)")
    ax.set_title("(b) Pressure distribution")
    ax.legend(fontsize=7, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[2]
    ax.scatter(vol, q, color=palette, s=70, edgecolor="black", linewidth=0.5)
    for i, t in enumerate(flow):
        ax.annotate(f"T{t['territory']}", (vol[i], q[i]), fontsize=7,
                    xytext=(4, 4), textcoords="offset points")
    # regression line through origin (flow proportional to volume)
    vol_arr, q_arr = np.array(vol), np.array(q)
    k = (vol_arr * q_arr).sum() / (vol_arr * vol_arr).sum()
    xs = np.linspace(0, max(vol) * 1.05, 10)
    ax.plot(xs, k * xs, color="gray", linestyle="--", linewidth=0.8,
            label="volume-proportional fit")
    ax.set_xlabel("Territory volume (mm$^3$)")
    ax.set_ylabel("Root inlet flow (mL min$^{-1}$)")
    ax.set_title("(c) Flow vs. territory volume")
    ax.legend(fontsize=7, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig5_flow_pressure.png"), dpi=300,
                bbox_inches="tight")
    plt.close(fig)
    print("fig5 done")


if __name__ == "__main__":
    fig0_atlas()
    fig1_segments()
    fig2_portal_tree()
    fig3_territories()
    fig4_synthetic_trees()
    fig5_flow_pressure()
    print("All figures written to", OUT)
