# Handoff: Liver Virtual Twin — CCO Meso-Unit Vasculature

**Date:** 2026-09-23
**Branch:** `claude/livermodels-repo-access-ks7sit`
**Target:** [Journal of Biomechanics special issue, "Virtual Twins of Human Organ Systems"](https://www.sciencedirect.com/special-issue/335590/virtual-twins-of-human-organ-systems) — submission deadline **31 Dec 2026**, article type "VSI: Virtual Twins". Guest editors: J. Weickenmeier (Oxford), A. Ní Annaidh (UCD), S. Budday (FAU Erlangen), M. Peirlinck (TU Delft), M. Genet (École Polytechnique). The CFP explicitly prioritizes **multiphysics modeling with adequate, reliable model validation** over pure geometric/visualization work — this shapes everything below.

## 1. The core concept (why any of this exists)

A "vascularly constrained functional macro-unit": bridge patient-scale anatomy (Couinaud segments, imaged vasculature — resolvable to maybe 40-90 branch generations) down toward the true functional scale of the liver (~10⁶ hepatic lobules, ~1.4mm³ each) **without** meshing every lobule individually. Three scales:

- **Macro**: the 8 Couinaud segments (done — real segmented geometry).
- **Meso**: portal perfusion territories, each fed by one real imaged terminal branch, extended by a synthetic vascular tree down toward lobule-cluster resolution. Each meso-unit's terminal flow/pressure becomes the boundary condition for a **micro**-scale representative-lobule model (not yet built).
- **Micro**: representative lobule physics (1D portal→central oxygen/zonation PDE) — not started.

This session's work is entirely on the **meso** layer, scoped to Couinaud segments II+III (the left lateral lobe — the standard adult-to-infant living-donor liver transplant graft, chosen as a tractable, clinically meaningful demo region).

## 2. What's built and working

### 2.1 Published artifacts (view these first)
- **[Couinaud Viewer](https://claude.ai/artifact/RKW5uv2ScCMMBzsNMaXavn)** — interactive 3D viewer, all 8 Couinaud segments (S1+S9 merged — see §2.2) plus the 4 real vascular/biliary trees (portal vein, hepatic artery, hepatic vein, bile duct).
- **[Meso-Unit Growth](https://claude.ai/artifact/8hFHERdZw233mhVbQmtVkE)** — the active work: segments II+III, the real portal tree, 6 confirmed real terminal branches, and their OpenCCO-grown synthetic extensions (~3,500 terminals). **This is where the open problem lives (§4).**

### 2.2 Anatomy pipeline
- Source data: `liverModels/` in this repo (legacy Zinc/three.js JSON format — vertex/face arrays with a bitmask face encoding, NOT modern glTF).
- `virtual_twin_pipeline/scripts/skeleton.py` — parses that legacy format into `{positions, indices}` compact JSON (used everywhere downstream) and reconstructs a **vessel skeleton graph** from the triangulated tube surface: each vessel mesh turns out to be ~40-90 disconnected "tubelet" mesh fragments (not one connected surface), so the script re-bridges them into a proper node/edge graph via endpoint clustering (tuned bridging radius, see the sweep logic in that file), giving node degree, branch points, and leaves.
- `scripts/macro_units.py` — Couinaud segment volumes (divergence-theorem mesh volume, cross-validated against `trimesh`), whole-liver total **1,433,320 mm³**.
- Segments **S1 and S9 were merged** (both instances) into one "Segment 1" — a genuine finding, not arbitrary: geodesic distance along the *portal vein surface graph* (not straight-line, which cuts through tissue) showed S9's portal entry is topologically closest to S1's (caudate lobe), consistent with S9 being a split-off caudate sub-region in this dataset. All later work uses the merged 8-segment set.

### 2.3 Topology-based perfusion-zone identification (`scripts/find_s2s3_roots.py`)
Do **not** re-derive segment→vessel-terminal assignment by nearest-vertex spatial distance alone — this was tried first and is unreliable (a terminal can be spatially close to a segment without actually being the branch that perfuses it). Instead: trace the portal vein skeleton graph from the main trunk (identified by an outlier vessel-radius test — trunk tubelets are much thicker than terminal tubelets), BFS out, find the deepest common ancestor node of all candidate leaves near S2/S3. This is what a real "left portal branch" should look like anatomically (it also serves a bit of S1/S4, which is anatomically correct — the true left portal branch feeds II+III+IV, not II+III in isolation).
Result: **6 real terminal branches** confirmed (1 in S2, 5 in S3), saved in `data/s2s3_roots.json`. This is the authoritative root set — don't recompute a naive proximity-based one.
**Independently verified** (point-in-mesh containment, not just distance) that all 6 are genuinely *inside* S2/S3 tissue, not merely nearby.

### 2.4 OpenCCO integration
Built from source (not a pip package — it's C++):
```bash
git clone --depth 1 https://github.com/DGtal-team/DGtal.git && cd DGtal
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF -DBUILD_DOC=OFF -DWITH_GMP=OFF -DWITH_QGLVIEWER=OFF -DWITH_ITK=OFF
make -j$(nproc)   # ~4 min

apt-get install -y libboost-dev libceres-dev zlib1g-dev libpng-dev

git clone --depth 1 https://github.com/OpenCCO-team/OpenCCO.git && cd OpenCCO
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DDGtal_DIR=<path-to-DGtal>/build
make -j$(nproc)   # ~1 min — binaries at build/bin/generateTree{2D,3D}
```
Also needs: `pip install numpy scipy trimesh` (Python side).

**Domain confinement**: OpenCCO's `--organDomain` takes a DGtal `.vol` voxel mask (custom binary format — see `scripts/write_vol.py` for the reader/writer, reverse-engineered since it's undocumented). Each of the 6 territories gets its own `.vol` file: the S2∪S3 volume tessellated by nearest-real-terminal (Voronoi), computed via `trimesh.contains()` point-in-mesh testing on a voxel grid (`scripts/voxelize_s2s3.py`, `scripts/run_opencco.py`).

**A real bug was found and fixed here**: DGtal's `.vol` reader places the domain's first voxel at `Center - (dim-1)/2`, *not* at index (0,0,0), regardless of what `Center` you specify — every territory `.vol` file was written with `Center=(0,0,0)`, silently placing the true domain origin ~half the domain's own size away from what the rest of the pipeline assumed. This caused synthetic trees to spill up to 60+mm outside the real mesh (83% of node endpoints outside, some by 60mm). **Fixed** in `run_opencco.py` (`vol_center = (dims-1)//2`). **Verified the fix**, don't just trust it: re-ran point-in-mesh containment testing after the fix — 97.5% of node endpoints now strictly inside the real S2/S3 mesh, remainder within 0.8mm of the surface (expected 1.5mm-voxel discretization noise, not a leak).

**Also fixed**: switched from OpenCCO's `-e`/`.txt` exporter (which resolves each segment's parent via a fragile `myVectSegments[myVectParent[idx]]` raw array-position lookup) to its `-x`/`.xml` exporter (explicit ID-referenced node/edge table — see `scripts/xml_helpers.py::parse_opencco_xml`). This is architecturally more robust and is now what the whole pipeline uses. **Important**: a rigorous re-investigation (ID-based BFS graph traversal from the root, not spatial-proximity clustering — see `scripts/check_id_bfs.py`) confirmed the tree topology was **fully connected in both the old and new exporters** — the earlier alarm about "disconnected floating subtrees" turned out to be a false positive from a flawed verification method (checking 3D spatial proximity is not the same as checking graph connectivity — two different, unconnected nodes can legitimately sit close together in space). The XML switch is still worth keeping (better architecture, eliminates a "guess the nearest node" heuristic for the root connector, replaced with OpenCCO's own definitive root point), but **it did not fix the visual issue the user is now describing** — see §4.

Current demo density: 50 mm³/terminal → **3,542 synthetic terminals, 7,084 segments** across the 6 territories (~10-12 branch generations). This density was cross-checked against an independent, closely-related published paper (see §5) and lands in the same ballpark (~15-35 lobules represented per terminal in both).

### 2.5 Flow/pressure solve (`scripts/compute_flow.py`)
**Important finding**: OpenCCO's own internal flow/pressure/resistance bookkeeping (`my_pPerf=13300`, `my_pTerm=8400`, `my_qPerf=8330`, visible in its XML `info_graph` and in `CoronaryArteryTree.h` source) are literally its **unmodified coronary-artery demo defaults** — hardcoded constants, not derived from our `-a`/`-n` inputs at all. Do not use them. OpenCCO's per-segment **radius** *is* trustworthy (genuinely computed via its own Poiseuille/Murray's-law/volume-minimization optimization) — keep using that.

What's implemented instead: an independent Poiseuille resistance-network solve using real geometry (mm-converted segment length/radius from the XML) and literature portal-vein physiology:
- Total portal venous flow: 1100 mL/min (literature-typical, **citation needed before publication**)
- Portal pressure at root: 7 mmHg (literature-typical, **citation needed**)
- Blood viscosity: 3.6×10⁻³ Pa·s (matches OpenCCO's own internal choice, reasonable standard value)
- Each territory's inlet flow ∝ its volume fraction of total liver volume (uniform-perfusion-per-volume assumption, absent real perfusion imaging)
- Flow splits equally across a territory's own terminals (standard CCO/Kamiya assumption)
- Resistance per segment via standard Poiseuille law; pressure integrated top-down from the root

Output: `data/opencco_s2s3_flow.json` (full network, every segment carries `flow_ml_min`, `pressure_distal_mmHg`, `pressure_proximal_mmHg`) and `data/meso_unit_terminals.json` (**3,542 rows, one per meso-unit — this is the literal macro→meso boundary-condition table**: position, radius, flow, pressure per terminal). Current result: terminal flow is very uniform (~0.0383-0.0384 mL/min) — this is a direct mathematical consequence of both terminal-count *and* flow both being assigned proportional to territory volume, not an independently emergent finding; worth stating honestly in the paper. Pressure drop across the resolved tree is small (6.6-6.95 mmHg from a 7 mmHg root) — physiologically plausible, since most real portal-to-hepatic-vein pressure drop (~7→2-3 mmHg) is expected at the sinusoidal bed, which is *downstream* of everything resolved so far (inside the unmodeled micro/lobule layer).

**In progress, not finished**: viewer color-coding by pressure/flow (`InstancedMesh.setColorAt`, confirmed supported in three.js r0.128.0 despite being a newer API) — the JS edits are partially applied to `viewers/meso_unit_viewer/viewer.html` but **not fully wired up or tested** (button click handlers not yet connected to `applyColorMode()`, stats footer not yet updated with flow/pressure summary). Check this file's current state before assuming it works.

## 3. The open problem (why a teammate is needed)

User's own words: *"OpenCCO tree usually has one inlet, then protrude into a surface to generate branches. In this case, we've to design it more strategically. In segment II and III, use real tree to create perfusion zones, then in each perfusion zone, we've the perfusion branch generate the sub-OpenCCO tree, only in this way can we perform flow simulations."*

To be precise about what's already true vs. what's missing:
- ✅ Real tree → perfusion zones: **already implemented** (§2.3, §2.4 — 6 real terminals, Voronoi territories, confined growth).
- ✅ Perfusion branch generates its own sub-tree: **already implemented** (one OpenCCO call per territory, rooted at the real terminal).
- ❌ **What's still wrong**: visually, each territory's tree looks like a "starburst"/"sea urchin" radiating symmetrically outward from one point, not like a directionally-continuous extension of the real incoming vessel. Confirmed via screenshot review this is a real aesthetic/anatomical-plausibility problem, not the (already-resolved) connectivity bug. The user's concern is that this also threatens flow-simulation validity: a real vessel entering tissue continues in a consistent direction and progressively ramifies; a symmetric burst from a single point (with no directional constraint) doesn't and may not be physically appropriate for assigning boundary conditions.
- **Not yet root-caused or fixed.** Last message before handoff was requesting user clarification on this exact point; a follow-up answer arrived (quoted above) clarifying the flow-simulation angle, but the geometric/directional-continuity fix itself was not attempted.

### Leads worth trying (not yet explored)
1. **Directional bias at the domain root**: OpenCCO's `generateTree3D` only takes a root *position* (`-p X Y Z`), no direction. Check `src/helpers/GeomHelpers.h` and `ExpandTreeHelpers.h` for whether the candidate-point sampling or first-segment placement can be biased/masked (e.g., restricting the domain mask itself, for the region very close to the root, to only the forward half-space along the real vessel's local tangent direction — computable from the portal skeleton graph, which already has the parent-edge direction at each of the 6 roots).
2. **Two-stage/hierarchical growth**: grow a short, small-n "directional extension" first (root + a few terminals placed explicitly along the real vessel's tangent), then use *that* sub-tree's outer nodes as multiple new roots for a second, larger OpenCCO call to fill the rest of the territory — mimics how real vessels continue before ramifying, avoids the single-point symmetric burst.
3. **Reconsider territory shape**: current territories are pure nearest-neighbor Voronoi cells from only 6 seed points — quite large and irregularly shaped, which may itself be *why* OpenCCO's fill pattern looks unnatural (it has to reach far in multiple directions from one entry point to cover an oddly-shaped large cell). Finer/more anatomically-informed sub-territories (e.g., informed by the real tree's own further sub-branching, if any exists below what was used for the 6-terminal identification) might produce more natural-looking, smaller local growth domains.
4. Check whether OpenCCO's `GeomHelpers::Kamiya` optimization function or the candidate-sampling function accepts *any* directionality/weighting parameter not exposed via CLI — may require a small source patch and rebuild (toolchain is proven fast to rebuild, ~5 min total).

## 4. What NOT to re-investigate (already ruled out, would waste time)
- Tree topology/connectivity — verified fully connected via ID-based BFS at every scale tested, including the real 3,542-terminal trees. The "floating subtree" appearance is a rendering/perspective effect of tree density + a genuine "starburst" growth-pattern issue (§3), **not missing or broken parent-child links**.
- Geometric confinement to S2/S3 — fixed and verified (97.5% strict containment, residual is voxel discretization, not a leak).
- The 6 real root terminals' validity — verified both topologically (portal skeleton BFS from trunk) and geometrically (point-in-mesh containment) to be genuinely real, in-tissue portal branches specific to segments II/III.
- OpenCCO's radius computation — trustworthy, keep using it (it's the one part of OpenCCO's internal physics that isn't a leftover coronary-artery placeholder).

## 5. Relevant literature (found via live search this session, not from memory — verify before citing)
- **["Multiscale modeling of drug-induced liver injury from organ to lobule," npj Digital Medicine, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12185720/)** — closest prior art. Patient-specific MRI portal geometry → **CCO bridging 1.5mm vessels to 50µm outlets** → lobule-scale drug-injury physics. ~100,000 outlets for ~1.5M real lobules (~15 lobules/outlet — same order of magnitude as our own 25-35/unit, independently arrived at). Their acknowledged limitation: simplified **2D** capillary geometry — our full 3D trees are a genuine differentiator.
- **["Dual continuum upscaling of liver lobule flow and metabolism to the full organ scale," Frontiers in Systems Biology, 2022](https://www.frontiersin.org/journals/systems-biology/articles/10.3389/fsysb.2022.926923/full)** — different strategy: continuum homogenization (no discrete vessel geometry at all), ~1.4M lobule-scale grid blocks at 1mm³.
- Lobule geometry figures used in our own N_i estimates: ~10⁶ lobules in an adult human liver, ~1-1.5mm³ average volume, ~1-2mm diameter (multiple literature sources, ranges vary — see search results, worth pinning down one authoritative citation for the paper).

## 6. How to pick this up
1. `git clone` this repo, checkout `claude/livermodels-repo-access-ks7sit`, everything needed is under `virtual_twin_pipeline/` (scripts, compact geometry, current results, both viewer sources).
2. Rebuild DGtal+OpenCCO per §2.4 (fast, ~5 min total, standard Ubuntu packages).
3. Re-run order: `find_s2s3_roots.py` → `voxelize_s2s3.py` → `run_opencco.py` → `compute_flow.py`. Each writes its output JSON into the working directory; copy into `viewers/meso_unit_viewer/data/` to update the live viewer, then republish via the Artifact tool (see the two published links in §2.1 — republish to the *same* URL by passing it back in, don't create new ones).
4. The immediate task: solve §3. Everything else in this document is context, not blockers.
