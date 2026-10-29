# WANDa (WI) schema v1 - performance data and network GIS

Status: network 1.3.0 DRAFT 29/10/2026 awaiting sign-off (`..\Signoff\std-2026.10.29-DRAFT.md`; 1.2.1 frozen in `..\_frozen\network_1.2.1\`). Last signed: standard std-2026.10.16 SIGNED by James 16/10/2026 (wanda_network_v1 1.2.1, wanda_performance_v1 1.0.0, valve_type 1.3.2); std-2026.10.14 signed 15/10 (network 1.2.0); sign-offs in `..\Signoff\`; v1.1.0 and network 1.2.0 frozen in `..\_frozen\`.
Generic: no client names, layouts or codes.
Machine-readable files are the source; this page only explains them.

| File | What |
|---|---|
| `Schema/wanda_performance_v1.json` | Performance data kinds `contacts`, `network_events`, `wq_samples`, `flush_records` (v1.0.0) |
| `Schema/wanda_network_v1.json` | Network GIS, 18 layers + 2 attribute tables (v1.3.0, below; change log at the end) + ref rules + row flags + the WI app rules R1-R11 |
| `Code_Lists/*.json` | 29 code lists (network: `asset_type`, `material`, `status`, `pipe_function`, `water_type`, `units`, `lining`, `valve_type`, `normal_position`, `hydrant_type`, `hydrant_class`, `outlet_arrangement`, `meter_function`, `area_type`, `control_type`, `customer_type`, `non_household_type`, `site_type`, `value_source`, `ownership`, `monitoring_role`, `prv_control_mode`; telemetry (lists only, the telemetry schema follows): `telemetry_system`, `measure`, `measure_units`, `reading_quality`; performance: `contact_category`, `event_type`, `determinand`) |

Each field: `name`, `type`, `required`, optional `code_list`, `units`, `ref_to` + `ref_check`, `app` (the PLDR project
column it feeds), `description`. Types (`types` block): `ref` (text exactly as delivered - never changed; a float id
`12345.0` is written `12345`, leading zeros kept), `text`, `code` (from the field's code list), `date` / `datetime`
(ISO 8601, held as text), `time` (hh:mm), `number`, `int`, `bool` (`1` = yes, blank = not said), `list` (`;`
separated refs), `json` (v1.2: a JSON object as text - the `extra` bag).

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

## Network GIS (`wanda_network_v1` v1.3.0)

One GeoPackage `wanda_network.gpkg`, EPSG:27700, metres; layer name = kind name; `dma_subs`, `meter_loggers` and `prv_settings` are attribute tables (no
geometry); polygon layers are MultiPolygon (Polygon rows accepted). Plus `wanda_delivery.json` (schema version,
mapping id / version / sha256, converter, row counts per layer, rows dropped by code, source layer -> WI layer).
The converter changes only layer names, field names and the delivery's own codes; values as delivered. Node
building, snapping, linking, DMA assignment and status filtering stay in the apps - driven by the rules below, never
by per-client tables.

| Layer | Geometry | App table | Required | Optional |
|---|---|---|---|---|
| `pipes` | Line (MultiLineString only when flagged `multipart`) | gis_pipes | pipe_ref, pipe_function, diameter, diameter_units, material | from_node_ref, to_node_ref, length_m, status, water_type, dma_ref, dma_sub_ref, dma_sub_type, wqz_ref, control_group_ref, sub_region_ref, region_ref, model_area_ref, installed_date, lining_current / factory / previous, lining_date, multipart, from_node_source, to_node_source, dma_ref_source, material_source, diameter_source, installed_date_source, ownership |
| `nodes` | Point | gis_nodes | node_ref | elevation_m |
| `elevation_points` | Point | WDA pipe elevation (nearest point) | elevation_m | point_ref |
| `valves` | Point | gis_valves | valve_ref, valve_type | regulator_type, node_ref, normal_position, status, dma_ref, elevation_m, installed_date, pipe_ref, node_ref_source, pipe_ref_source, dma_ref_source, dma_boundary_refs |
| `hydrants` | Point | gis_hydrants | hydrant_ref | hydrant_type, hydrant_class, outlet_arrangement, node_ref, status, dma_ref, control_group_ref, elevation_m, installed_date, pipe_ref, node_ref_source, pipe_ref_source, dma_ref_source, dma_boundary_refs |
| `meters` | Point | gis_meters | meter_ref, meter_function | node_ref, pipe_ref, site_ref, dma_ref, dma_from_ref, control_group_ref, meter_type, status, diameter, diameter_units, meter_function_delivered, node_ref_source, pipe_ref_source, dma_ref_source, dma_boundary_refs |
| `properties` | Point | gis_properties | property_ref | pipe_ref, dma_ref, customer_type, non_household_type, building_no, sub_building, building_name, street, locality, town, postcode, ground_level_m, model_area_ref, dma_ref_source; `organisation` is a restricted placeholder, never filled (v1.3) |
| `dma_areas` | Polygon | gis_dma_polygons + dma_hierarchy | dma_ref, area_type | dma_name, control_group_ref, wqz_ref, sub_region_ref, region_ref, model_area_ref, customer_count |
| `dma_subs` | - | gis_pipes.dma_subzone_ref / _type | dma_sub_ref, dma_ref | dma_sub_type, control_type, control_asset_refs |
| `supply_zones` | Polygon | dma_info.zone | wqz_ref | name, source |
| `control_groups` | Polygon | dma_hierarchy.control_zone | control_group_ref | name, region_ref |
| `sub_regions` | Polygon | (open point 2) | sub_region_ref | region_ref |
| `regions` | Polygon | dma_hierarchy.region | region_ref | - |
| `model_areas` | Polygon | (model registry) | model_area_ref | model_name, model_no |
| `pumps` | Point | - | pump_ref | node_ref, node_ref_source |
| `sites` | Point | - | site_ref, site_type | node_ref, status, node_ref_source |
| `assets` | Point | - (v1.2; all apps by asset_type) | asset_ref, asset_type | asset_type_delivered, status, node_ref, pipe_ref, dma_ref, elevation_m, installed_date, node_ref_source, pipe_ref_source, dma_ref_source, dma_boundary_refs |
| `monitoring_points` | Point | - (display only; PLDR does not use it for flushing or scores) | monitoring_ref | monitoring_role, measure, asset_layer, asset_ref, node_ref, node_ref_source, ground_level_m, ground_level_source, dma_ref, dma_ref_source, dma_boundary_refs, logger_ref, valid_from, valid_to, status |
| `meter_loggers` | - (attribute table) | - | meter_ref, system, logger_ref | channel, measure, valid_from, valid_to, source |
| `prv_settings` | - (attribute table, dated) | - | prv_ref | valve_ref, control_mode, inlet_setting, outlet_setting, modulation_setting, diameter, diameter_units, make, model, controller_ref, dma_ref, dma_from_ref, dma_sub_ref, meter_ref, cp_refs, installed_date, valid_from, status |

v1.2 adds to every layer the converter-set row flags `confirm` and `extra` (last two fields, never mapped); to
`nodes` node_type, status; to `properties` property_type, business_type, sub_region_ref and the restricted placeholder
sensitive_customer; to `pumps` / `sites` status.

### v1.3 (29/10/2026, draft) - additive

- **Where a value came from.** Fields `*_source` (code list `value_source`: gis, derived_coincident, derived_own, derived_connection, derived_boundary, derived_polygon, client_inferred) say whether a node, pipe or area ref, a material, a diameter or an installed date was delivered or filled by the import. The import writes them; no mapping sets them. A value that is not `gis` is a derived or inferred value the apps may count and report, never re-derive.
- **Node refs filled once.** Where a delivery left a pipe end or point asset without a node ref the import fills it from the geometry (ends and points within 1 cm share one ref). A derived ref is `c:<x>_<y>` (metres, 3 decimal places, the cluster's lowest end point). No node rows are added. Blank area refs are filled once (connected network first, then polygon); a point on a boundary keeps `dma_ref` blank and lists both areas in `dma_boundary_refs`.
- **Pipes** gain `ownership` (company / private / unknown; blank = not said). **Valves and hydrants** gain `pipe_ref`. **Meters** gain `diameter`, `diameter_units` and `meter_function_delivered` (the delivered value(s) behind `meter_function`, written by the converter). **Monitoring locations** that are not meters (critical points, low level, DG2, PRV inlet / outlet, pump suction / delivery, DMA inlet) are rows of the new point layer `monitoring_points` (`monitoring_role`, optional asset link, node, ground level as delivered); meter logger links stay in `meter_loggers`.
- **`properties.organisation` is restricted**: a placeholder, never filled (as `sensitive_customer`); business use is carried by `business_type` / `non_household_type`.
- **New attribute tables** `meter_loggers` (meter to logger / SCADA reference; blank `logger_ref` skipped and counted) and `prv_settings` (PRV settings and control mode, dated, text as delivered).
- **Meter function** gains `source`, `reservoir_inlet`, `reservoir_outlet`, `pump` (network) and `process` (not on the supply network). "Waste meter" is not a synonym of any code (its UK meaning varies); a delivery maps it through its own `codes.confirm`. **Pipe function** `trunk`: `serves_customers` is null (the module decides; client property links are kept as delivered).
- **Telemetry code lists** `telemetry_system`, `measure`, `measure_units` (group + factor to the WI unit), `reading_quality` are defined here; the telemetry schema itself is a later version.
- New import mapping keys that go with this version (documented with the import): `inferred` (fallback columns, writes `<field>_source`), `units_in_value`, `only_new_against`, `xy` (easting / northing columns of a CSV).

### James's standing rules (13/10/2026) - v1.2

1. **One import, all apps.** Every clean-water layer and field of a delivery comes in: abandoned / proposed /
   mothballed assets kept with `status` (R1), raw / non-potable / service pipes with `pipe_function` (communication =
   company side, supply = customer side, other = washout / emptying / fire mains), customer meters with
   `meter_function` (R6), fittings / joints / junctions as `nodes` (node_type, status), other point assets in
   `assets` (asset_type). Source fields with no WI field go in the row's `extra` bag (the mapping's `extra: [cols]` or
   `"*rest"`). Waste-water layers stay out (declared excluded); the converter reports any delivered layer neither
   mapped nor excluded. Apps take what they need by the rules - the same rules for every client.
2. **Accept all GIS whatever its quality.** Only structural faults stop an import (a layer the converter cannot read,
   no geometry where required, refs not text, an impossible CRS); quality issues are warnings with rate bands - never
   a block, never silent (unmapped codes are counted and reported).
3. **Personal data never imported** - people's names, phone numbers, e-mail addresses (the loader refuses a mapping
   that names such a column; free text loses them). Addresses and business / property types ARE imported (WI names:
   property_type, business_type, address fields); organisation names are not (v1.3: restricted placeholder). Sensitive customers only through the restricted
   placeholder `properties.sensitive_customer` (special sign-in in WI; never filled by the converter).
4. **Uncertain classes flagged.** A code whose code-list `confirm` attribute is true (pipe_function unknown:
   serves_customers false - "probably not, but confirm"), a delivered value with no mapping, or a value the mapping
   lists in `codes.confirm` puts the field in the row's `confirm` (R11). The row keeps its own ref, so staff confirm it
   against the client key outside AI (pick / key tool) or a new WI value is added the normal way.
5. **Sub-region** (`sub_region_ref` on pipes / properties / dma_areas) = an extra area level: operational split,
   team or county - the delivery's own.
6. **Code-list labels are the reporting lookups**: every code's `label` is its display / report name (WI names), the
   same for every client; the codes stay the stable keys.

Area levels (WI): DMA -> dma_sub (attribute only, below the DMA); DMA -> WQ zone -> sub-region -> region; DMA ->
control group; DMA -> model area. Each level has its own layer; `dma_areas` names a DMA's place in each.

Ref rules: refs are text exactly as delivered; `ref_to` names the layer.field a ref points at (a list = any of them -
a node ref may name a junction, a pipe end or a point asset that is its own network node, as a valve in a UK
geometric network); `must_exist` = an error when the target layer is delivered, `should_exist` = counted and
reported; `unique` is each layer's key (never blank, except the optional key parts of `meter_loggers` (channel) and `prv_settings` (valid_from), which are compared as blank). Hydrant and meter refs: duplicates are reported (warn), the
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
| R2 | pipe_function.serves_customers | a property snaps only to such a pipe; a delivered pipe_ref is kept; null (trunk) = the module decides |
| R3 | pipe_function.potable_network | raw / non-potable mains kept, not analysed |
| R4 | valve_type.isolates (+ list-level blank_isolates) | stops an isolation trace (is_gate_valve); isolation valves only - sluice, butterfly, boundary, district, motorised. A BLANK valve_type isolates (`blank_isolates: true`); `other` does not (valve_type 1.3.2, James 14/10) |
| R5 | normal_position.shut | closed = boundary as delivered; throttled / unknown = open |
| R6 | meter_function.network | only network meters into gis_meters: district, bulk, reservoir, reservoir_inlet, reservoir_outlet, trunk, supply, source, pump; process, customer, commercial and other are not network meters |
| R7 | area_type.is_dma | only DMA areas become DMA polygons |
| R8 | material.band | discolouration risk band (unknown = 3) |
| R9 | hydrant_class.supply_tier | FB / FJ / TB first tier, LJ second, unclassified not used |
| R10 | units.factor | diameter x factor = mm per row (pipes, meters, PRVs); coordinates metres BNG |
| R11 | *.confirm | an uncertain class: the field is listed in the row's confirm (v1.2) |

Not in the schema on purpose: personal fields of any kind (no people's names, phones, e-mails; priority-service /
medical flags only through the restricted placeholder sensitive_customer, never filled by the converter); empty
vendor-template fields (they may ride in `extra`).

WI writes this schema itself: `04_Generator\src\wanda_network.py` (region_gis `--wanda-network`; wi_build runs it
into `Skins\_preimport_gis\wanda_network\`). Its identity proof rebuilds the Truth GIS from the gpkg exactly (every
value and coordinate) - the WWI identity skin.

## Open points for James

1. Spun iron: one WI code `SCI` for any delivered spun iron (no auto synonym for the short code "SI" - it goes to the
   pick list); its band / WQ risk is James's to set (sources disagree). Also to set: bands of PC, FRC, GF, BR (meanings
   settled in v1.1.0); hydrant class TB supply tier (1 by meaning). (pipe_function.unknown answered 13/10: false +
   confirm.)
2. Sub-region in the apps: PLDR has no sub-region column; proposal `area_extra_1_ref` typed `sub_region`.
3. Customer meters are imported (v1.2, meter_function customer, network = false, rule R6); gis_meters keeps network
   meters only unless the app says otherwise - one rule for every client.
10. (v1.2) One PLDR pipe set for every client: communication pipes are potable_network true (as v1.1) - one delivery
    carries them in its mains layer, others now import their service-pipe layers. Keep them in the analysed network
    or take them out (false) for every client?
11. (v1.2) Stop taps: valve_type `stop_tap`, isolates false (customer-side; never cuts a mains trace). Confirm.
12. (v1.2) A source column whose meaning may be sensitive but is not caught by the generic words is left out by the
    mapping's `extra_omit` (one delivery: a customer-department indicator) - James to decide each.
4. Hydrant bore / jumper class FB / FJ / LJ is its own list `hydrant_class` (supply_tier); `hydrant_type` is the
   function (fire / washout). One list instead?
5. Air valves sit in `valves` (valve_type air, isolates false) - gis_valves then holds them (non-isolating); or a
   layer of their own? (Valve rule: 13/10 "every valve except non-return and air" reverted 14/10 - isolation valves only, valve_type 1.3.1; blank type isolates, valve_type 1.3.2.)
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

| network 1.2.0 | 13/10/2026 | Every layer: `confirm` (list) + `extra` (json) row flags, set by the converter; type `json`; `row_flags` block; container `scope` (clean water only) | James 13/10: one import, all apps |
| network 1.2.0 | 13/10/2026 | New layer `assets` (asset_type code list 1.0.0); nodes node_type + status; pumps / sites status; properties property_type, business_type, sub_region_ref, sensitive_customer (restricted placeholder) | James 13/10: every clean-water layer / field; B2 sub-region |
| network 1.2.0 | 13/10/2026 | R1 applies to nodes / pumps / sites / assets; R2 / R3 / R6 wording; new R11 (confirm) | James 13/10 |
| pipe_function 1.2.0 | 13/10/2026 | unknown: serves_customers false + confirm; new codes supply (customer side) and other (washout / emptying / fire); communication synonyms service / lateral | James 13/10 "probably not, but confirm"; service-pipe layers imported |
| valve_type 1.3.0 | 13/10/2026 | New code stop_tap (isolates false - James to confirm) | stop taps imported, no longer dropped |
| valve_type 1.3.1 | 14/10/2026 | **Reverts the 1.2.0 isolates rule.** isolates true only for isolation valves: sluice, butterfly, boundary, district, motorised. false for prv, psv, frv, pbv, float, nrv, washout, air, stop_tap, other (blank = unknown = false). Codes unchanged (patch) | James 14/10: PRV / PSV / FCV are not isolation valves (water passes backwards; type often unknown); an NRV is no reliable reverse isolation; only isolation valves isolate, for mains repairs and analysis. GIS isolation must match the Synergi isolation scripts MM runs (they close Synergi VL valves only) and the legacy readers (gate valves only) |
| valve_type 1.3.2 | 14/10/2026 | List-level `blank_isolates: true` (+ `blank_isolates_reason`): a BLANK valve_type isolates; `other` still does not. Codes and per-code isolates unchanged (patch). 1.3.1 kept in `..\_frozen\valve_type_1.3.1\` | James 14/10: an unrecorded type is far more likely an ordinary isolation valve than a PRV; aligns every app (PLDR already did this; WDA aligned; PLDR drift check reads the flag) |
| network 1.2.1 | 16/10/2026 | text only: every filed area polygon valid; converter repairs invalid polygons (make_valid structure) and records geometry_repaired; validator refuses an unrepaired one (NW-INVALID); no field / layer / code change, 1.2.0 sets still read | James 16/10 |
| network 1.3.0 | 29/10/2026 | DRAFT, additive: `*_source` provenance fields (value_source) on pipes, valves, hydrants, meters, assets, pumps, sites, properties; pipes ownership; valves + hydrants pipe_ref; `dma_boundary_refs`; meters diameter, diameter_units, meter_function_delivered; new point layer monitoring_points (monitoring_role; non-meter logger / monitoring locations); new attribute tables meter_loggers and prv_settings | import rework: derived values recorded, meter size / function, monitoring points, PRV settings |
| network 1.3.0 | 29/10/2026 | `properties.organisation` marked restricted (never filled); text: node and area refs filled once by the import (ref_rules), meter inlet / export rule, R2 null = module decides, R6 / R10 wording | names never imported; one place for the derivation rules |
| meter_function 1.2.0 | 29/10/2026 | New codes source, reservoir_inlet, reservoir_outlet, pump (network) and process (not network); labels of reservoir and district clarified; "waste meter" deliberately not a synonym | source / reservoir / pump meters were not distinguishable; UK meaning of waste meter varies |
| pipe_function 1.3.0 | 29/10/2026 | trunk: serves_customers null (module decides) with a note; nothing else changes | property links on trunk mains are kept as delivered |
| value_source, ownership, monitoring_role, prv_control_mode 1.0.0 | 29/10/2026 | New code lists | fields above |
| telemetry_system, measure, measure_units, reading_quality 1.0.0 | 29/10/2026 | New code lists (units with group and factor to the WI unit); the telemetry schema follows in a later version | logger / telemetry references and readings |

All v1.2.0 changes are additive for a reader of the WI set (new optional fields at the end of each layer, a new layer,
new codes) except pipe_function.unknown serves_customers (true -> false). All v1.1.0 changes are additive (new optional fields, a new optional layer, new codes) or label / attribute
corrections; a v1.0.0 set still reads. Network 1.2.1 is text only: a 1.2.0 set still reads. Network 1.3.0 is additive: a 1.2.x set still reads (new fields blank); consumers must accept the new meter codes and a null trunk serves_customers before a 1.3.0 set is filed. Sign-offs: `..\Signoff\`.

- material code list 1.2.1 (13/10/2026): bands aligned with the decided WRc banding - AK 3 -> 1 (black alkathene, PE family), FRC 3 -> 2 (like AC; James 13/10).
