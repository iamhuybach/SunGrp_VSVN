import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINES = {
    "FL_00": ROOT / "pipelines" / "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00" / "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json",
    "ENR": ROOT / "pipelines" / "PL_VV_TRANS_SLV_TO_ENR_15M" / "PL_VV_TRANS_SLV_TO_ENR_15M.json",
    "GLD": ROOT / "pipelines" / "PL_VV_TRANS_SLV_TO_GLD_30M" / "PL_VV_TRANS_SLV_TO_GLD_30M.json",
}
NOTEBOOKS = {
    "NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK": "NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb",
    "NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV": "NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb",
    "NB_EXTRACT_CMS_CDC_BRZ_TO_SLV": "NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb",
    "NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV": "NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb",
    "NB_00_ORCHES_SLV_TO_ENR_15P": "NB_00_ORCHES_SLV_TO_ENR.ipynb",
    "NB_00_ORCHES_SLV_TO_GLD_30M": "NB_00_ORCHES_SLV_TO_GLD.ipynb",
}
CHILD_LISTS = ("activities", "ifTrueActivities", "ifFalseActivities")
SOURCES = {
    "If_Run_PARTNER": "partner_raw_data",
    "If_Run_3P": "brz_3rd_crawler_poi_stream",
    "If_Run_CMS": "cms_raw_data",
    "If_Run_ENRICH": "brz_enrichment_result",
}
PARTNER_ID = "2baecfc9-a8a3-4905-965f-f16eb6244fee"
GUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


def _load(key: str) -> dict:
    return json.loads(PIPELINES[key].read_text(encoding="utf-8"))


def _props(doc: dict) -> dict:
    return doc["resources"][0]["properties"]


def _walk(activities: list, in_true: bool = False):
    names = [item.get("name") for item in activities]
    for activity in activities:
        yield activity, in_true, names
        props = activity.get("typeProperties") or {}
        for key in CHILD_LISTS:
            if key in props:
                yield from _walk(props[key], in_true or key == "ifTrueActivities")


def _notebooks(doc: dict):
    for activity, in_true, _names in _walk(_props(doc)["activities"]):
        if activity.get("type") == "TridentNotebook":
            yield activity, in_true


def _by_name(doc: dict, name: str) -> dict:
    found = [activity for activity, _in_true, _names in _walk(_props(doc)["activities"]) if activity.get("name") == name]
    assert len(found) == 1, name
    return found[0]


def _parameter_source(notebook_file: str) -> str:
    nb = json.loads((ROOT / "notebooks" / notebook_file).read_text(encoding="utf-8"))
    cells = [
        cell for cell in nb["cells"]
        if "parameters" in ((cell.get("metadata") or {}).get("tags") or [])
    ]
    assert len(cells) == 1, notebook_file
    return "".join(cells[0]["source"])


def _timeout_minutes(value: str) -> int:
    day, clock = value.split(".")
    hours, minutes, _seconds = clock.split(":")
    return int(day) * 24 * 60 + int(hours) * 60 + int(minutes)


def test_no_switch_and_unique_activity_names():
    names = []
    for key in PIPELINES:
        doc = _load(key)
        for activity, _in_true, _names in _walk(_props(doc)["activities"]):
            assert activity.get("type") != "Switch"
            names.append(activity["name"])
    assert len(names) == len(set(names))


def test_depends_on_same_scope_and_succeeded_only():
    for key in PIPELINES:
        for activity, _in_true, names in _walk(_load(key)["resources"][0]["properties"]["activities"]):
            for dep in activity.get("dependsOn") or []:
                assert dep["activity"] in names
                conditions = dep["dependencyConditions"]
                if conditions == ["Completed"]:
                    assert activity["name"].startswith("Wave_") or activity["name"] == "If_Any_Failed"
                    assert dep["activity"].startswith("Wave_")
                elif conditions == ["Failed"]:
                    assert activity["name"].startswith("Set_Failed_")
                    assert dep["activity"].startswith(("Get_Config_", "ForEach_"))
                else:
                    assert conditions == ["Succeeded"]


def test_notebooks_only_in_true_branch():
    for key in PIPELINES:
        found = list(_notebooks(_load(key)))
        assert found
        for activity, in_true in found:
            assert in_true, activity["name"]


def test_notebook_policy_and_declared_params():
    for key in PIPELINES:
        for activity, _in_true in _notebooks(_load(key)):
            assert activity["policy"]["timeout"]
            assert activity["policy"]["retry"] == 0
            params = activity["typeProperties"]["parameters"]
            assert params
            source = _parameter_source(NOTEBOOKS[activity["name"]])
            for name in params:
                assert re.search(rf"(?m)^\s*{re.escape(name)}\s*=", source), (activity["name"], name)


def test_fl00_sources_and_dispatch():
    doc = _load("FL_00")
    props = _props(doc)
    assert props["concurrency"] == 1
    chain = ["PARTNER", "3P", "CMS", "ENRICH"]
    for suffix, source in zip(chain, SOURCES.values(), strict=True):
        query = _by_name(doc, f"Get_Config_{suffix}")["typeProperties"]["scripts"][0]["text"]["value"]
        assert "src_schema = 'lh_vv_bronze.dbo'" in query
        assert f"src_tbl = '{source}'" in query
        for other in SOURCES.values():
            if other != source:
                assert f"src_tbl = '{other}'" not in query
        foreach = _by_name(doc, f"ForEach_{suffix}")
        assert foreach["typeProperties"]["isSequential"] is True
        has_work = _by_name(doc, f"If_HasWork_{suffix}")
        expression = has_work["typeProperties"]["expression"]["value"]
        assert expression.startswith("@")
        assert [item["name"] for item in has_work["typeProperties"]["ifFalseActivities"]] == [f"Set_Msg_Skip_{suffix}"]
        dispatched = _by_name(doc, f"If_Run_{suffix}")
        assert dispatched["typeProperties"]["expression"]["value"] == (
            f"@and(equals(item().src_tbl, '{source}'), {expression[1:]})"
        )
        notebooks = dispatched["typeProperties"]["ifTrueActivities"]
        assert len(notebooks) == 1
        assert notebooks[0]["typeProperties"]["parameters"]["src_tbl"]["value"] == source
        assert notebooks[0]["typeProperties"]["parameters"]["pl_name"]["value"] == "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"
        assert foreach["dependsOn"] == [
            {"activity": f"Get_Config_{suffix}", "dependencyConditions": ["Succeeded"]},
        ]


def test_fl00_wave_failure_paths():
    doc = _load("FL_00")
    props = _props(doc)
    assert props["variables"]["v_any_failed"]["defaultValue"] == "false"
    chain = ["PARTNER", "3P", "CMS", "ENRICH"]
    names = [activity["name"] for activity, _in_true, _names in _walk(props["activities"])]
    assert not any(name.startswith("Fail_Source_") for name in names)
    for index, suffix in enumerate(chain):
        wave = _by_name(doc, f"Wave_{suffix}")
        inner = [item["name"] for item in wave["typeProperties"]["ifTrueActivities"]]
        assert inner[:2] == [f"Get_Config_{suffix}", f"ForEach_{suffix}"]
        config_flag = _by_name(doc, f"Set_Failed_Config_{suffix}")
        foreach_flag = _by_name(doc, f"Set_Failed_ForEach_{suffix}")
        assert config_flag["dependsOn"] == [
            {"activity": f"Get_Config_{suffix}", "dependencyConditions": ["Failed"]},
        ]
        assert foreach_flag["dependsOn"] == [
            {"activity": f"ForEach_{suffix}", "dependencyConditions": ["Failed"]},
        ]
        assert config_flag["typeProperties"]["variableName"] == "v_any_failed"
        assert foreach_flag["typeProperties"]["variableName"] == "v_any_failed"
        if index == 0:
            assert {"activity": "Validate_Extract_Binding", "dependencyConditions": ["Succeeded"]} in wave["dependsOn"]
        else:
            assert wave["dependsOn"] == [
                {"activity": f"Wave_{chain[index - 1]}", "dependencyConditions": ["Completed"]},
            ]
    final = _by_name(doc, "If_Any_Failed")
    assert final["dependsOn"] == [{"activity": "Wave_ENRICH", "dependencyConditions": ["Completed"]}]
    assert final["typeProperties"]["expression"]["value"] == "@equals(variables('v_any_failed'), 'true')"
    assert [item["name"] for item in final["typeProperties"]["ifTrueActivities"]] == ["Fail_Extract_Waves"]


def test_fl00_partner_activity_unchanged():
    raw = PIPELINES["FL_00"].read_text(encoding="utf-8")
    assert raw.count(PARTNER_ID) == 1
    baseline = json.loads(subprocess.check_output(
        ["git", "show", f"9a62b9f:{PIPELINES['FL_00'].relative_to(ROOT).as_posix()}"],
        cwd=ROOT, text=True, encoding="utf-8",
    ))
    old = _by_name(baseline, "NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK")
    new = _by_name(_load("FL_00"), "NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK")
    assert new["dependsOn"] == []
    assert new["policy"] == old["policy"]
    assert new["typeProperties"]["parameters"] == old["typeProperties"]["parameters"]
    assert new["typeProperties"]["notebookId"] == old["typeProperties"]["notebookId"]
    assert new["typeProperties"]["workspaceId"] == old["typeProperties"]["workspaceId"]


def test_fl00_binding_fails_closed():
    doc = _load("FL_00")
    expression = _by_name(doc, "Validate_Extract_Binding")["typeProperties"]["expression"]["value"]
    for name in ("nb_extract_3p_id", "nb_extract_cms_id", "nb_extract_enr_id", "workspace_id"):
        assert f"empty(pipeline().parameters.{name})" in expression
        assert f"contains(pipeline().parameters.{name}, 'PENDING')" in expression
    deps = [item["activity"] for item in _by_name(doc, "Wave_PARTNER")["dependsOn"]]
    assert "Validate_Extract_Binding" in deps
    for activity, _in_true in _notebooks(doc):
        if activity["name"] == "NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK":
            continue
        notebook_id = activity["typeProperties"]["notebookId"]
        assert notebook_id["type"] == "Expression"
        assert "pipeline().parameters." in notebook_id["value"]
        assert not GUID.search(notebook_id["value"])


def test_transform_gate_skips_only_on_no_data():
    reasons = ("FIRST_RUN", "LAST_RUN_NOT_OK", "UPSTREAM_CHANGED", "IDLE_BACKSTOP", "NO_DATA")
    for key, gate_name, if_name in (
        ("ENR", "Get_Flow_Gate_ENR", "If_HasWork_ENR"),
        ("GLD", "Get_Flow_Gate_GLD", "If_HasWork_GLD"),
    ):
        doc = _load(key)
        sql = _by_name(doc, gate_name)["typeProperties"]["scripts"][0]["text"]["value"]
        for reason in reasons:
            assert reason in sql
        assert "COALESCE(status, '') <> 'SKIPPED_CONCURRENT'" in sql
        assert "COALESCE(r.status, '') NOT IN ('NO_DATA', 'SKIPPED_CONCURRENT', 'RUNNING')" in sql
        assert "SKIPPED_CONCURRENT" in sql and "DRY_RUN" in sql and "RUNNING" in sql
        assert "NOT IN" in sql
        branch = _by_name(doc, if_name)
        expression = branch["typeProperties"]["expression"]["value"]
        assert "p_force_run" in expression and "'NO_DATA'" in expression
        assert [item["name"] for item in branch["typeProperties"]["ifFalseActivities"]][0].startswith("Set_Msg_Skip")
        assert any(item["type"] == "TridentNotebook" for item in branch["typeProperties"]["ifTrueActivities"])


def test_gld_pipeline_timeouts():
    doc = _load("GLD")
    raw = json.dumps(doc)
    assert not GUID.search(raw)
    assert doc["resources"][0]["name"] == "PL_VV_TRANS_SLV_TO_GLD_30M"
    props = _props(doc)
    assert props["concurrency"] == 1
    activity = _by_name(doc, "NB_00_ORCHES_SLV_TO_GLD_30M")
    assert activity["policy"]["timeout"] == "0.00:52:00"
    params = activity["typeProperties"]["parameters"]
    assert int(params["p_lock_timeout_min"]["value"]) > int(params["p_dag_timeout_min"]["value"]) + 5
    assert params["p_lock_timeout_min"]["value"] == "90"
    assert params["p_dag_timeout_min"]["value"] == "45"
    assert params["p_pl_name"]["value"]["value"] == "@pipeline().Pipeline"


def test_expression_calls_are_binary():
    def calls(text: str):
        found = []
        index = 0
        while index < len(text):
            match = re.search(r"\b(or|and)\(", text[index:])
            if not match:
                break
            start = index + match.end()
            depth = 1
            args = 1
            cursor = start
            while cursor < len(text) and depth:
                char = text[cursor]
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                elif char == "," and depth == 1:
                    args += 1
                cursor += 1
            found.append((match.group(1), args))
            index = start
        return found

    for key in PIPELINES:
        raw = PIPELINES[key].read_text(encoding="utf-8")
        for name, arity in calls(raw):
            assert arity == 2, (key, name, arity)


def test_lock_outlives_activity_timeout():
    doc = _load("FL_00")
    for name in (
        "NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV",
        "NB_EXTRACT_CMS_CDC_BRZ_TO_SLV",
        "NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV",
    ):
        activity = _by_name(doc, name)
        running = int(activity["typeProperties"]["parameters"]["running_timeout_minutes"]["value"])
        assert running == 60
        assert running > _timeout_minutes(activity["policy"]["timeout"])
