# Luxury Bathroom — Contest 2798513

Local coordinate-based concept package. No contest upload, message, deployment or Git commit has been made by this build.

**Current stage: primary visual direction awaiting approval.** The project rule requires approval of one 1200 px main preview before producing the remaining presentation sheets. The independent geometry and CAD preparation is complete; the three remaining raster images are not yet rendered or visually verified.

## Files

| File | Current result |
|---|---|
| `layout_geometry.json` | Exact supplied plan bounds, centimetre conversions, explicit height assumptions, storage calculations, option distinctions, change schedule and 12 coordination holds |
| `assets/cad_plan_option_a.png` | 2400 × 2600; generated and visually inspected |
| `review/cad_plan_option_a_1200.jpg` | Primary direction approval preview |
| `exports/Master_Bathroom_243sqft_Proposal.dxf` | R2010 / AC1024; inches; 79 native dimensions; zero audit errors and zero audit fixes after reopening |
| `exports/Master_Bathroom_243sqft_Proposal.dwg` | R2000 / AC1015 compatibility companion; dimensions and text converted to vector outlines; local placed-geometry roundtrip passes |
| `exports/geometry_validation.json` | Checks and explicit pending-image list |
| `exports/cad_validation.json` | DXF entity/layer inventory and audit result |
| `exports/dwg_validation.json` | DWG comparison scope, tolerance and compatibility limits |
| `assets/cad_plan_existing_vs_option_b.png` | Pending primary-direction approval; renderer prepared |
| `assets/cad_3d_cutaway_iso.png` | Pending primary-direction approval; renderer prepared, not visually validated |
| `assets/cad_4_elevations.png` | Pending primary-direction approval; renderer prepared |

The CAD contains all three plans at full size in inches, stacked vertically in the X=0..250 sheet band. Their drawing origins are `(68,40)`, `(68,340)`, `(68,640)`. Subtract these offsets to recover the local room coordinate system. The elevation/section sheet occupies X=300..700. East and West elevations cover 200 inches; the East vanity itself occupies Y=6..140, i.e. 134 inches on the 140-inch available wall. West is an **unfolded** elevation across the 50-inch room offset. North and South elevations cover 150 inches.

## Geometry and source interpretation

The latest supplied coordinates govern this concept. The two original sketches were visually opened and the 33.8-second walkthrough was reviewed through a timestamp-ordered contact sheet. They substantiate the general room arrangement and stepped tub deck but do not constitute a measured survey of all opening coordinates, wall build-ups or heights. The employer's written brief calls its dimensions preliminary and lists the WC as approximately 36 × 60 inches; the present model follows the user's later 50 × 60-inch instruction.

The polygon area is exactly **35,000 in² = 243.0556 ft² = 22.5806 m²**, before any interpretation of measured wall faces. Ceiling height is **assumed 96 inches**, matching the requested full-height towers. Window sill/head heights, door head heights and symbolic wall thicknesses are explicitly assumed. This is a coordinated concept study with unresolved design holds, not permit or fabrication documentation.

| Hold | Exact issue and treatment |
|---|---|
| C01 | Tub centre `(50,176)` and skylight centre `(60,150)` differ by `(-10,+26)` inches. Both supplied coordinates are retained; no centred-under-skylight claim. |
| C02 | North ledge Y=192..200 is 8 inches deep, not the stated 10. Its edge touches the tub envelope; installation/cleaning clearance remains unresolved. |
| C03 | The stated 102 × 138-inch circulation rectangle intersects the WC by 208 in² and entry door swings. Drawings state the 102-inch cabinet-front separation only. No NKBA-compliance claim is made. |
| C04 | A 28-inch WC pocket leaf has only 14 inches of wall to the east and 8 inches to the west. The opening is shown; a workable acoustic pocket mechanism is not asserted. |
| C05 | The supplied wet-zone window at X=0, Y=158..190 lies between the main room and the wing, overlapping proposed glass, S-03 and utility chase. A dashed reference marks the unresolved condition. |
| C06 | S-04 spans X=102..148, overlapping the north WC window X=110..140. With the assumed heights, they also conflict vertically. |
| C07 | S-05 is not defined. 142.4 ft³ cannot be substantiated without cabinet internals, hardware and equipment allowances. No balancing fictitious storage is added. |
| C08 | Tankless fuel/electrical capacity, temperature/flow sizing, venting, condensate, servicing and steam-generator location are unverified. Option A remains conditional. |
| C09 | The requested 6-inch shower niche extends beyond X=-50. Structural wall depth and external boundary conditions need verification. |
| C10 | The full S-01C tower reaches Y=140 and conflicts with a finite WC south partition. Construction build-up remains unresolved. |
| C11 | Original preliminary WC dimensions differ from the later user coordinate schedule. Source provenance is preserved. |
| C12 | Ceiling, window heights and wall thicknesses are assumptions, not measured existing conditions. |

The shower pivot is hinged on the **south jamb**, opening into the main room. Its 30-inch sweep was checked against the actual 68 × 32-inch elliptical tub outline. The north-jamb swing would intersect the tub and is not used. WIC pocket travel is diagrammatic pending wall construction verification.

Option B retains the 50 × 40-inch mechanical footprint and 50 × 60-inch shower zone. It omits S-03. Retention of the footprint does not certify existing utility access or service clearances. S-01, S-02 and S-04 match Option A.

## Storage calculation

This is an **assumed internal-envelope estimate before shelves, runners, plumbing/equipment and loading allowances**. It is not manufacturer-rated net storage. Drawer envelopes explicitly deduct a central plumbing notch. Tall cabinets use explicit proposed internal dimensions stored in JSON. No claim that 24 bath sheets have been physically fitted is made.

| Group | Calculation basis | A, ft³ | B, ft³ |
|---|---|---:|---:|
| S-01 | Two 16 × 22 × 88-inch tall interiors; four 32 × 20 × 9-inch drawers less 12 × 10 × 9-inch notches; 24 × 12 × 56-inch grooming interior | 56.02 | 56.02 |
| S-02 | 16 × 22 × 88-inch utility; 28 × 22 × 30-inch hamper; 28 × 22 × 54-inch linen; 14 × 18 × 88-inch robe interior | 60.70 | 60.70 |
| S-03 | 20 × 14 × 76-inch heated-cabinet interior | 12.31 | — |
| S-04 | 44 × 8 × 38-inch interior, subject to C06 | 7.74 | 7.74 |
| S-05 | Undefined; no capacity counted | — | — |
| **Total** | Full-precision arithmetic, prior to rounding individual groups | **136.78** | **124.46** |

The requested **142.4 ft³** is retained as a target, equivalent to **4,032.31895 L**. It is not labelled achieved. The difference between A and B is 12.3148 ft³ from S-03.

## CAD compatibility and verification

The DXF is the authoritative editable drawing. Required architectural layers are present, plus `A-COORD-HOLD` for unresolved conditions. Dimension entities retain inch measurements, with centimetre annotations on `A-DIMS-MET`. Cabinet patterns use a 2-inch perpendicular hatch spacing suited to monochrome CAD plotting.

LibreDWG 0.14 failed to preserve TEXT alignment, MTEXT height and vertical native-dimension angles in a direct conversion. The delivered companion DWG therefore expands dimensions and converts all text to vector outlines with a maximum curve approximation of 0.002 inches. Placed coordinates, paths, hatch patterns and primitives were compared after DWG→DXF roundtrip at a 0.00001-inch numeric tolerance. The DWG retains inch units and drawing layers; it does **not** retain editable semantic text/dimension entities. Unreferenced library blocks are excluded from the placed-geometry comparison.

LibreDWG still emits metadata/handle/HATCH warnings; counts and scope are retained in `exports/dwg_validation.json` and logs in `review/`. **No Autodesk AutoCAD open/save test has been performed.** Local roundtrip proof must not be described as native AutoCAD acceptance. Use the R2010 DXF to edit annotations and regenerate the compatibility DWG.

Actual CAD A-plan render proofs are in `review/dxf_plan_proof.png` and `review/dwg_plan_proof.png`. These are readback checks, separate from the presentation PNG.

Failed conversion probes, temporary source/quarter-size previews and Python bytecode caches have been removed. The approval preview, final CAD proofs, conversion logs and roundtrip data remain in `review/`; cleanup is recorded in the local cleanup ledger.

## Rebuild and next step

Existing local packages used: Python, ezdxf, shapely, matplotlib, NumPy and Pillow; CLI `dxf2dwg` / `dwg2dxf`. No packages were installed. Font files are copied from the project's existing architectural font assets: Space Grotesk, IBM Plex Sans and JetBrains Mono.

```sh
python3 scripts/build_package.py
python3 scripts/cad_proof.py
```

After explicit approval of the primary visual direction:

```sh
python3 scripts/build_package.py --approved-direction
```

Then inspect all three new 1200 px previews, fix any visual defects, rerun affected checks, and update this status plus the project PROGRESS entry. The remaining renderers have been prepared but their output has not yet been generated, so they are not counted as delivered. The specified user-coordinate conflicts remain design decisions even after visual approval.

The employer's full contest brief additionally calls for two 3D views, a short design explanation and a material palette. The four-image technical asset scope requested in this task is a component of that submission; it is not represented as a complete contest entry.

## Primary-image design check

- White engineering sheet, thin black frame and bottom title strip; no banners, pills, dashboard cards or floating note bubbles.
- One dominant plan; pale warm stone joints recede behind black geometry and walnut hatching.
- Purpose-selected architectural fonts; monospaced imperial/metric dimension strings.
- Source photographs and generated fantasy interiors are not used as substitute geometry.
- Performance, capacity and compliance claims are limited to measured script results and disclosed assumptions.
- 1200 px preview and actual DXF/DWG readback checked. The final competition upload size and remaining artwork are not approved at this stage.
