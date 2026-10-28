"""wanda_health_v1 1.0 (health check static report): structure, code-list joins and the 29/10 rulings."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPES = {"ref", "text", "code", "date", "datetime", "time", "number", "int", "bool", "list", "json"}
KINDS = {"model_health", "dma_health", "dma_items", "pipe_list", "valve_list", "hydrant_list", "meter_list",
         "pump_list", "site_list", "regulator_list", "data_quality", "id_defects"}


def _doc():
    return json.loads((ROOT / "Schema" / "wanda_health_v1.json").read_text(encoding="utf-8"))


def _code_list(name):
    return json.loads((ROOT / "Code_Lists" / f"{name}.json").read_text(encoding="utf-8"))


def test_kinds_files_and_field_types():
    d = _doc()
    assert (d["schema"], d["version"]) == ("wanda_health_v1", "1.0.0")
    assert set(d["kinds"]) == KINDS
    assert d["container"]["files"] == {k: f"{k}.csv" for k in KINDS}
    for k, kind in d["kinds"].items():
        names = [f["name"] for f in kind["fields"]]
        assert len(names) == len(set(names)), k
        assert all(f["type"] in TYPES and f.get("description") for f in kind["fields"]), k
        for key in kind["unique"]:
            assert set(key) <= set(names), (k, key)
        if k != "data_quality":
            assert names[0] == "model_name", k


def test_code_lists_exist_and_flag_fields_are_gone():
    d = _doc()
    used = {f["code_list"] for kind in d["kinds"].values() for f in kind["fields"] if f.get("code_list")}
    for name in used:
        assert _code_list(name)["codes"] is not None, name
    assert all(f["type"] == "code" for kind in d["kinds"].values() for f in kind["fields"] if f.get("code_list"))
    gone = {"config_differs", "flag_reasons", "dmas_flagged", "band", "missing_length_max_pct", "change",
            "changed_fields", "prev_set", "valves_differ"}
    for kind in d["kinds"].values():
        assert not gone & {f["name"] for f in kind["fields"]}
    assert "flag_rules" not in d and "missing_length_max_pct" not in d["rules"]
    assert not (ROOT / "Code_Lists" / "health_band.json").exists()
    assert not (ROOT / "Code_Lists" / "health_change.json").exists()


def test_outcome_rule_only_engineer_review_proposed():
    cl = _code_list("health_outcome")
    assert [c["code"] for c in cl["codes"] if c["proposed_by_tool"]] == ["engineer_review"]
    assert {c["code"] for c in cl["codes"]} == {"ok", "ok_with_warnings", "engineer_review", "needs_new_model"}


def test_design_columns_present():
    k = {n: [f["name"] for f in v["fields"]] for n, v in _doc()["kinds"].items()}
    for col in ("length_unit", "model_length_m", "model_valves_shut", "control_valves", "hydrant_labels", "pumps",
                "tanks", "regulators", "shut_differences", "id_defects", "shares_pipes_with", "proposed_outcome"):
        assert col in k["model_health"], col
    for col in ("polygon_key", "area_ha", "covering_models", "gis_length_in_model_m", "abandoned_in_model",
                "valves_gis_shut_model_open", "valves_gis_open_model_shut", "valves_not_compared", "boundary_valves",
                "customers_properties", "customers_gis", "hydrants_in_model", "meters_network", "checked_at"):
        assert col in k["dma_health"], col
    assert {"dma_refs", "boundary", "placed_by", "compare", "operation_mode", "initial_position"} <= set(k["valve_list"])
    assert {"source", "link_method", "diameter", "diameter_units", "model_diameter", "model_length_m"} <= \
        set(k["pipe_list"])


def test_boundary_rule_is_node_first_polygon_only_without_node():
    r = _doc()["rules"]
    assert "node_ref" in r["boundary"] and "blank" in r["boundary"] and r["polygon_distance_m"] == "1.0"
    assert "attribute shut" in r["gis_shut"]


def test_no_client_names_or_machine_paths():
    text = (ROOT / "Schema" / "wanda_health_v1.json").read_text(encoding="utf-8")
    for bad in ("D:\\\\", "C:\\\\", "PLDR\\UU", "Synergi_", "United", "Severn", "Southern"):
        assert bad not in text, bad
