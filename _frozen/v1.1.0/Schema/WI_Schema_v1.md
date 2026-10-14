# WANDa (WI) schema v1 - performance data and network GIS

Status: performance v1.0.0 DRAFT, network v1.1.0 FOR JAMES'S SIGNATURE (13/10/2026; not signed - sign-off goes in
`..\Signoff\`). Generic: no client names, layouts or codes. Machine-readable files are the source; this page only
explains them.

| File | What |
|---|---|
| `Schema/wanda_performance_v1.json` | Performance data kinds `contacts`, `network_events`, `wq_samples`, `flush_records` (v1.0.0) |
| `Schema/wanda_network_v1.json` | Network GIS, 16 layers (v1.1.0, below; change log at the end) + ref rules + the WI app rules R1-R10 |
| `Code_Lists/*.json` | 20 code lists (network: `material`, `status`, `pipe_function`, `water_type`, `units`, `lining`, `valve_type`, `normal_position`, `hydrant_type`, `hydrant_class`, `outlet_arrangement`, `meter_function`, `area_type`, `control_type`, `customer_type`, `non_household_type`, `site_type`; performance: `contact_category`, `event_type`, `determinand`) |

Each field: `name`, `type`, `required`, optional `code_list`, `units`, `ref_to` + `ref_check`, `app` (the PLDR project
column it feeds), `description`. Types (`types` block): `ref` (text exactly as delivered - never changed; a float id
`12345.0` is written `12345`, leading zeros kept), `text`, `code` (from the field's code list), `date` / `datetime`
(ISO 8601, held as text), `time` (hh:mm), `number`, `int`, `bool` (`1` = yes, blank = not said), `list` (`;`
separated refs).

Each code: `code`, `label`, `synonyms` (generic UK industry wording only - the tier (a) vocabulary the mapper uses to
recognise a delivered code) and the attribute(s) that carry the ONE app rule for that code.

## Performance data (`wanda_performance_v1`)

One UTF-8 CSV per kind and source table (`{kind}__{table}.csv`), header = the field names in schema order, plus
`wanda_delivery.json`. The columns ARE the PLDR STANDARD template that every client can already import, so PLDR reads
the WI set with no change. Minimum record: a date + one location field (`location_fields`).

Rules kept from the template:
- `contacts.contact_type` is the client's wording (audit); `category` is the WI code.
- `network_events.event_type` is the WI code (the template derives the app category from it).
- `wq_samples.determinand` is the client's name (the app reads the WI determinand and "unflushed" from its words);
  `category` is the WI code; `units` as delivered (the app converts to the code list unit).
- `network_events.diameter` / `material` as delivered (the app normalises them).
- `flushed` / `udf`: `1` or blank only (the template reads any non-blank text as yes).
- Coordinates: x/y metres BNG (the only value the converter may convert: delivered decimetres etc. via the `units`
  code list factor), or lat/lon WGS84.
- Area levels (`dmz`, `manager_area`, `region`, `zone`) as delivered.

## Network GIS (`wanda_network_v1` v1.1.0)

One GeoPackage `wanda_network.gpkg`, EPSG:27700, metres; layer name = kind name; `dma_subs` is an attribute table (no
geometry); polygon layers are MultiPolygon (Polygon rows accepted). Plus `wanda_delivery.json` (schema version,
mapping id / version / sha256, converter, row counts per layer, rows dropped by code, source layer -> WI layer).
The converter changes only layer names, field names and the delivery's own codes; values as delivered. Node
building, snapping, linking, DMA assignment and status filtering stay in the apps - driven by the rules below, never
by per-client tables.

| Layer | Geometry | App table | Required | Optional |
|---|---|---|---|---|
| `pipes` | Line (MultiLineString only when flagged `multipart`) | gis_pipes | pipe_ref, pipe_function, diameter, diameter_units, material | from_node_ref, to_node_ref, length_m, status, water_type, dma_ref, dma_sub_ref, dma_sub_type, wqz_ref, control_group_ref, sub_region_ref, region_ref, model_area_ref, installed_date, lining_current / factory / previous, lining_date, multipart |
| `nodes` | Point | gis_nodes | node_ref | elevation_m |
| `elevation_points` | Point | WDA pipe elevation (nearest point) | elevation_m | point_ref |
| `valves` | Point | gis_valves | valve_ref, valve_type | regulator_type, node_ref, normal_position, status, dma_ref, elevation_m, installed_date |
| `hydrants` | Point | gis_hydrants | hydrant_ref | hydrant_type, hydrant_class, outlet_arrangement, node_ref, status, dma_ref, control_group_ref, elevation_m, installed_date |
| `meters` | Point | gis_meters | meter_ref, meter_function | node_ref, pipe_ref, site_ref, dma_ref, dma_from_ref, control_group_ref, meter_type, status |
| `properties` | Point | gis_properties | property_ref | pipe_ref, dma_ref, customer_type, non_household_type, building_no, sub_building, building_name, organisation, street, locality, town, postcode, ground_level_m, model_area_ref |
| `dma_areas` | Polygon | gis_dma_polygons + dma_hierarchy | dma_ref, area_type | dma_name, control_group_ref, wqz_ref, sub_region_ref, region_ref, model_area_ref, customer_count |
| `dma_subs` | - | gis_pipes.dma_subzone_ref / _type | dma_sub_ref, dma_ref | dma_sub_type, control_type, control_asset_refs |
| `supply_zones` | Polygon | dma_info.zone | wqz_ref | name, source |
| `control_groups` | Polygon | dma_hierarchy.control_zone | control_group_ref | name, region_ref |
| `sub_regions` | Polygon | (open point 2) | sub_region_ref | region_ref |
| `regions` | Polygon | dma_hierarchy.region | region_ref | - |
| `model_areas` | Polygon | (model registry) | model_area_ref | model_name, model_no |
| `pumps` | Point | - | pump_ref | node_ref |
| `sites` | Point | - | site_ref, site_type | node_ref |

Area levels (WI): DMA -> dma_sub (attribute only, below the DMA); DMA -> WQ zone -> sub-region -> region; DMA ->
control group; DMA -> model area. Each level has its own layer; `dma_areas` names a DMA's place in each.

Ref rules: refs are text exactly as delivered; `ref_to` names the layer.field a ref points at (a list = any of them -
a node ref may name a junction, a pipe end or a point asset that is its own network node, as a valve in a UK
geometric network); `must_exist` = an error when the target layer is delivered, `should_exist` = counted and
reported; `unique` is each layer's key (never blank). Hydrant and meter refs: duplicates are reported (warn), the
reader keeps the first. `dma_areas.dma_ref` is not unique (several polygons per DMA; the reader dissolves them).

Converter requirement (step 9): keep the source row order within each layer (first-wins readers depend on it).

Material: the list holds every code of the apps' band list (so bands survive the converter). Rule (James 13/10):
every delivered material -> one WI code; bands are WRc's, keyed by WI code; a missing band = default band 3; an unknown
short code is looked up in public UK water / sewer material code usage, else it stays its own code with the default
band (`band_status` "default"). Bands still "James to set": SCI, PC, FRC, GF, BR (meanings now settled - see the
change log).

Nodes (v1.1): pipe from / to node refs name junctions in `nodes` (fed from the delivery's fitting / joint / connection
/ junction / water-point layers - every point the source network treats as a node) or a point asset that is its own
node (valve, hydrant, meter, pump, site node_ref). The order of a pipe's from / to refs may follow flow rather than
digitising: the mapping says which in `app_options.pipe_node_order` ("digitised" default | "flow"); the converter
copies it into `wanda_delivery.json` and the validator then reports orientation as info. Topology comes from the refs,
never from the vertex order.

Multi-part pipes (v1.1): the converter merges a MultiLineString whose parts join (one part, or parts end to end) into
one LineString; parts that do not join are kept as MultiLineString in the `pipes` layer with `multipart` = 1 (the
validator reports them as NW-GEOM multipart, info). Nothing is dropped or split.

Elevation points (v1.1): an optional `elevation_points` layer (spot heights) for WDA's pipe elevation (nearest point),
for deliveries whose nodes carry no level. WI's own GIS carries the level on its nodes, so the WI skins write none.

WI app rules (one per code attribute, `rules` block):

| Rule | Code list . attribute | App behaviour |
|---|---|---|
| R1 | status.in_network | every asset kept; only in_network assets build the analysed network (blank = unknown = in) |
| R2 | pipe_function.serves_customers | a property snaps only to such a pipe; a delivered pipe_ref is kept |
| R3 | pipe_function.potable_network | raw / non-potable mains kept, not analysed |
| R4 | valve_type.isolates | stops an isolation trace (is_gate_valve); every valve except nrv / air (v1.1) |
| R5 | normal_position.shut | closed = boundary as delivered; throttled / unknown = open |
| R6 | meter_function.network | only network meters into gis_meters |
| R7 | area_type.is_dma | only DMA areas become DMA polygons |
| R8 | material.band | discolouration risk band (unknown = 3) |
| R9 | hydrant_class.supply_tier | FB / FJ / TB first tier, LJ second, unclassified not used |
| R10 | units.factor | diameter x factor = mm per row; coordinates metres BNG |

Not in the schema on purpose: personal fields of any kind (no people's names, phones, e-mails, priority-service /
medical flags); empty vendor-template fields.

WI writes this schema itself: `04_Generator\src\wanda_network.py` (region_gis `--wanda-network`; wi_build runs it
into `Skins\_preimport_gis\wanda_network\`). Its identity proof rebuilds the Truth GIS from the gpkg exactly (every
value and coordinate) - the WWI identity skin.

## Open points for James

1. Spun iron: one WI code `SCI` for any delivered spun iron (no auto synonym for the short code "SI" - it goes to the
   pick list); its band / WQ risk is James's to set (sources disagree). Also to set: bands of PC, FRC, GF, BR (meanings
   settled in v1.1.0); `pipe_function.unknown` serves_customers (default true); hydrant class TB supply tier (1 by
   meaning).
2. Sub-region in the apps: PLDR has no sub-region column; proposal `area_extra_1_ref` typed `sub_region`.
3. Customer meters (meter_function customer, network = false, rule R6) would leave gis_meters in the generic reader;
   today's WI FileGDB route loads them - keep R6 as is (a declared parity difference) or make customer meters network?
4. Hydrant bore / jumper class FB / FJ / LJ is its own list `hydrant_class` (supply_tier); `hydrant_type` is the
   function (fire / washout). One list instead?
5. Air valves sit in `valves` (valve_type air, isolates false) - gis_valves then holds them (non-isolating); or a
   layer of their own? (Valve rule answered 13/10: every valve isolates except non-return and air - v1.1.0.)
6. Sensitive non-household premises (schools, hospitals, care homes) come from `non_household_type`; priority-service /
   medical flags are excluded. Confirm.
7. Event `material` stays as delivered in performance v1 (the app normalises); a material code map can be added in a
   minor version.
8. `flushed` / `udf` booleans: the template cannot carry an explicit "no" (generic app fix candidate).
9. Code values: material / lining keep UK short codes (CI, EPX ...), the other lists lower-case words. Keep?

## Change log - network schema + code lists

| Version | Date | Change | Why |
|---|---|---|---|
| network 1.0.0 | 13/10/2026 | First version (15 layers, rules R1-R10) | master plan step 5 |
| network 1.1.0 | 13/10/2026 | `pipes.dma_sub_type` + `dma_subs.dma_sub_type` (text): the delivery's own kind of the sub-area | gap: a source's sub-zone kind had no field |
| network 1.1.0 | 13/10/2026 | `pipes.multipart` (bool) + `geometry_accepts`: joinable multi-part lines merged, the rest kept as MultiLineString flagged multipart = 1 | gap: sources deliver MultiLineString mains |
| network 1.1.0 | 13/10/2026 | `pipes.from_node_ref` / `to_node_ref` ref_to adds `hydrants.node_ref`, `meters.node_ref`; `nodes` described as fed from fitting / joint / connection / junction / water-point layers; pipe description: node-ref order may follow flow (`app_options.pipe_node_order`) | gap: node refs name junction layers and point assets; some sources order refs by flow |
| network 1.1.0 | 13/10/2026 | New layer `elevation_points` (Point; point_ref, elevation_m) | gap: WDA reads pipe elevation from a spot-height layer |
| material 1.2.0 | 13/10/2026 | Labels corrected by public UK water / sewer material code usage: BR = brick (not brass; band 2 -> default 3), PC = prestressed concrete (not a plastic; band 1 -> 3, concrete family), PSC = plastic / steel composite (not prestressed concrete), FRC = fibre reinforced concrete, CSU = concrete segments (unbolted), GF = glass fibre, MAC / MAR = masonry regular / random courses | wrong or unconfirmed meanings |
| material 1.2.0 | 13/10/2026 | Added CSB (concrete segments, bolted), GRC (glass reinforced concrete), PF (pitch fibre) with public meanings; BP, BAC, CPS kept as their own codes with the default band (meaning not confirmed in public usage) | codes the gold mappings need; James's rule "if no answer then default" |
| valve_type 1.2.0 | 13/10/2026 | Every valve isolates (washout, PRV, PSV, flow control, pressure breaking, other ...) except nrv and air; new code `float` (float / altitude valve) | James 13/10 "a valve is a valve"; a source float-valve subtype |
| hydrant_class 1.1.0 | 13/10/2026 | New code TB (throughbore, supply tier 1 - James to confirm) | a source hydrant jumper / bore class |
| outlet_arrangement 1.1.0 | 13/10/2026 | New codes `ball` (ball hydrant outlet), `valved` | source outlet codes with no WI code |
| control_type 1.1.0 | 13/10/2026 | `unknown` added; prv synonyms pressure managed / pressure area | sub-area control not always recorded |

All v1.1.0 changes are additive (new optional fields, a new optional layer, new codes) or label / attribute
corrections; a v1.0.0 set still reads. For James's signature with v1.0.0 (`..\Signoff\`).

- material code list 1.2.1 (13/10/2026): bands aligned with the decided WRc banding - AK 3 -> 1 (black alkathene, PE family), FRC 3 -> 2 (like AC; James 13/10).
