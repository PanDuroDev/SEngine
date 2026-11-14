"""Standard-library conformance checks for the proposed SEngine narrative contract.

This is a contract test harness, not the production Rust narrative runtime.
Run from the repository root with:
    python -m unittest discover -s tests/narrative -v
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/narrative/narrative-document.schema.json"
DOCUMENT_PATH = ROOT / "examples/narrative/first-contact.narrative.json"
SAVE_PATH = ROOT / "examples/narrative/first-contact.save.json"


def load_json(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def resolve_pointer(root, pointer: str):
    if not pointer.startswith("#/"):
        raise ValueError(f"Only local JSON Pointers are supported: {pointer}")
    value = root
    for token in pointer[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[token]
    return value


def walk_schema_refs(value, root):
    if isinstance(value, dict):
        if "$ref" in value:
            resolve_pointer(root, value["$ref"])
        for child in value.values():
            walk_schema_refs(child, root)
    elif isinstance(value, list):
        for child in value:
            walk_schema_refs(child, root)


def scalar_type(value):
    # bool is a subclass of int in Python; the order here is intentional.
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    return None


def index_by_id(items):
    result = {}
    for item in items:
        identifier = item["id"]
        if identifier in result:
            raise ValueError(f"duplicate_id:{identifier}")
        result[identifier] = item
    return result


def validate_condition(condition, variables):
    op = condition.get("op")
    if op == "compare":
        variable = variables.get(condition.get("variable_id"))
        if variable is None:
            raise ValueError("condition_variable_missing")
        if scalar_type(condition.get("value")) != variable["type"]:
            raise ValueError("condition_type_mismatch")
        comparison = condition.get("comparison")
        if comparison not in {"eq", "ne", "gt", "gte", "lt", "lte"}:
            raise ValueError("invalid_comparison")
        if comparison in {"gt", "gte", "lt", "lte"} and variable["type"] != "number":
            raise ValueError("condition_type_mismatch")
    elif op in {"all", "any"}:
        children = condition.get("conditions", [])
        if not children:
            raise ValueError("empty_condition_group")
        for child in children:
            validate_condition(child, variables)
    elif op == "not":
        validate_condition(condition["condition"], variables)
    else:
        raise ValueError("invalid_condition")


def evaluate_condition(condition, values):
    op = condition["op"]
    if op == "compare":
        variable_id = condition["variable_id"]
        if variable_id not in values:
            raise ValueError("condition_variable_missing")
        left, right = values[variable_id], condition["value"]
        if scalar_type(left) != scalar_type(right):
            raise ValueError("condition_type_mismatch")
        return {
            "eq": lambda: left == right,
            "ne": lambda: left != right,
            "gt": lambda: left > right,
            "gte": lambda: left >= right,
            "lt": lambda: left < right,
            "lte": lambda: left <= right,
        }[condition["comparison"]]()
    if op == "all":
        return all(evaluate_condition(child, values) for child in condition["conditions"])
    if op == "any":
        return any(evaluate_condition(child, values) for child in condition["conditions"])
    if op == "not":
        return not evaluate_condition(condition["condition"], values)
    raise ValueError("invalid_condition")


def validate_document(document):
    if document.get("kind") != "sengine.narrative-document" or document.get("schema_version") != 1:
        raise ValueError("unsupported_document")
    variables = index_by_id(document["variables"])
    speakers = index_by_id(document["speakers"])
    events = index_by_id(document["event_types"])
    entry_points = index_by_id(document["entry_points"])
    graphs = index_by_id(document["graphs"])

    all_ids = {document["document_id"]}
    for collection in (variables, speakers, events, entry_points, graphs):
        for identifier in collection:
            if identifier in all_ids:
                raise ValueError(f"duplicate_id:{identifier}")
            all_ids.add(identifier)

    for event in events.values():
        field_ids = [field["id"] for field in event["payload_fields"]]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("duplicate_event_field_id")

    for entry in entry_points.values():
        if entry["graph_id"] not in graphs:
            raise ValueError("missing_reference")

    for graph in graphs.values():
        nodes = index_by_id(graph["nodes"])
        for node_id in nodes:
            if node_id in all_ids:
                raise ValueError(f"duplicate_id:{node_id}")
            all_ids.add(node_id)
        if graph["entry_node_id"] not in nodes:
            raise ValueError("missing_reference")
        edges = {node_id: [] for node_id in nodes}

        for node in nodes.values():
            if node["kind"] == "line":
                if node["speaker_id"] not in speakers or node["next_node_id"] not in nodes:
                    raise ValueError("missing_reference")
                edges[node["id"]].append(node["next_node_id"])
            elif node["kind"] == "choice":
                option_ids = set()
                for option in node["options"]:
                    if option["id"] in all_ids or option["id"] in option_ids:
                        raise ValueError(f"duplicate_id:{option['id']}")
                    option_ids.add(option["id"])
                    all_ids.add(option["id"])
                    if option["target_node_id"] not in nodes:
                        raise ValueError("missing_reference")
                    edges[node["id"]].append(option["target_node_id"])
                    if "availability" in option:
                        validate_condition(option["availability"], variables)

                    for effect in option.get("effects", []):
                        if effect["op"] in {"set_variable", "add_number"}:
                            variable = variables.get(effect["variable_id"])
                            if variable is None:
                                raise ValueError("missing_reference")
                            if effect["op"] == "set_variable" and scalar_type(effect["value"]) != variable["type"]:
                                raise ValueError("invalid_value_type")
                            if effect["op"] == "add_number" and variable["type"] != "number":
                                raise ValueError("invalid_value_type")
                        elif effect["op"] == "emit_event":
                            event = events.get(effect["event_type_id"])
                            if event is None:
                                raise ValueError("missing_reference")
                            fields = {field["id"]: field for field in event["payload_fields"]}
                            payload = effect["payload"]
                            if set(payload) - set(fields):
                                raise ValueError("invalid_event_payload")
                            for field_id, field in fields.items():
                                if field["required"] and field_id not in payload:
                                    raise ValueError("invalid_event_payload")
                                if field_id in payload and scalar_type(payload[field_id]) != field["type"]:
                                    raise ValueError("invalid_event_payload")
                        else:
                            raise ValueError("invalid_effect")
            elif node["kind"] != "end":
                raise ValueError("invalid_node_kind")

        reachable, pending = set(), [graph["entry_node_id"]]
        while pending:
            current = pending.pop()
            if current in reachable:
                continue
            reachable.add(current)
            pending.extend(edges[current])
        if reachable != set(nodes):
            raise ValueError("unreachable_node")
        if not any(nodes[node_id]["kind"] == "end" for node_id in reachable):
            raise ValueError("no_reachable_end")

    return variables, graphs, entry_points


def validate_save(save, document, variables, graphs, entry_points):
    if save.get("kind") != "sengine.player-save" or save.get("schema_version") != 1:
        raise ValueError("unsupported_save")
    if save.get("document_id") != document.get("document_id"):
        raise ValueError("save_document_mismatch")
    entry = entry_points.get(save.get("active_entry_point_id"))
    graph = graphs.get(save.get("active_graph_id"))
    if entry is None or graph is None or entry["graph_id"] != save["active_graph_id"]:
        raise ValueError("save_position_invalid")
    nodes = {node["id"] for node in graph["nodes"]}
    if save.get("active_node_id") not in nodes:
        raise ValueError("save_position_invalid")
    seen = set()
    for item in save.get("variable_values", []):
        variable_id = item.get("variable_id")
        if variable_id in seen or variable_id not in variables:
            raise ValueError("save_variable_invalid")
        seen.add(variable_id)
        if scalar_type(item.get("value")) != variables[variable_id]["type"]:
            raise ValueError("save_variable_type_mismatch")
    if seen != set(variables):
        raise ValueError("save_variable_missing")
    return True


def available_options(choice_node, values):
    result = []
    for option in choice_node["options"]:
        condition = option.get("availability")
        try:
            if condition is None or evaluate_condition(condition, values):
                result.append(option)
        except ValueError:
            # Invalid conditions fail closed, including when nested under NOT.
            continue
    return result


def select_choice(choice_node, option_id, variables, values):
    option = next((item for item in choice_node["options"] if item["id"] == option_id), None)
    if option is None:
        raise ValueError("choice_not_found")
    if option not in available_options(choice_node, values):
        raise ValueError("choice_unavailable")
    events = apply_choice(option, variables, values)
    return option["target_node_id"], events


def apply_choice(option, variables, values):
    staged = dict(values)
    queued_events = []
    for effect in option.get("effects", []):
        if effect["op"] == "set_variable":
            variable = variables[effect["variable_id"]]
            if scalar_type(effect["value"]) != variable["type"]:
                raise ValueError("invalid_value_type")
            staged[effect["variable_id"]] = effect["value"]
        elif effect["op"] == "add_number":
            variable = variables[effect["variable_id"]]
            if variable["type"] != "number":
                raise ValueError("invalid_value_type")
            staged[effect["variable_id"]] = staged[effect["variable_id"]] + effect["amount"]
        elif effect["op"] == "emit_event":
            queued_events.append({"event_type_id": effect["event_type_id"], "payload": effect["payload"]})
        else:
            raise ValueError("invalid_effect")
    values.clear()
    values.update(staged)
    return queued_events


class NarrativeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.document = load_json(DOCUMENT_PATH)
        cls.save = load_json(SAVE_PATH)
        cls.variables, cls.graphs, cls.entry_points = validate_document(cls.document)
        cls.graph = next(iter(cls.graphs.values()))
        cls.nodes = {node["id"]: node for node in cls.graph["nodes"]}
        cls.choice = next(node for node in cls.nodes.values() if node["kind"] == "choice")

    def test_schema_is_draft_2020_12_and_local_refs_resolve(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        walk_schema_refs(self.schema, self.schema)

    def test_authoring_fixture_is_semantically_valid(self):
        validate_document(self.document)

    def test_conditional_choice_is_hidden_and_shown(self):
        values = {key: variable["default"] for key, variable in self.variables.items()}
        self.assertEqual([item["id"] for item in available_options(self.choice, values)], ["choice.leave"])
        values["story.has_archive_key"] = True
        self.assertEqual(
            [item["id"] for item in available_options(self.choice, values)],
            ["choice.use_key", "choice.leave"],
        )

    def test_choice_commits_variable_and_queues_event_in_order(self):
        values = {key: variable["default"] for key, variable in self.variables.items()}
        values["story.has_archive_key"] = True
        option = next(item for item in self.choice["options"] if item["id"] == "choice.use_key")
        target, events = select_choice(self.choice, option["id"], self.variables, values)
        self.assertEqual(target, "node.ending")
        self.assertEqual(values["story.trust"], 1)
        self.assertEqual([event["event_type_id"] for event in events], ["event.timeline.play"])

    def test_stale_choice_is_rejected_without_mutating_state(self):
        values = {key: variable["default"] for key, variable in self.variables.items()}
        before = copy.deepcopy(values)
        with self.assertRaisesRegex(ValueError, "choice_unavailable"):
            select_choice(self.choice, "choice.use_key", self.variables, values)
        self.assertEqual(values, before)

    def test_invalid_effect_does_not_partially_commit(self):
        values = {key: variable["default"] for key, variable in self.variables.items()}
        option = {"effects": [
            {"op": "set_variable", "variable_id": "story.trust", "value": 7},
            {"op": "set_variable", "variable_id": "story.has_archive_key", "value": "not-a-boolean"},
        ]}
        before = copy.deepcopy(values)
        with self.assertRaisesRegex(ValueError, "invalid_value_type"):
            apply_choice(option, self.variables, values)
        self.assertEqual(values, before)

    def test_invalid_condition_is_not_made_true_by_not(self):
        condition = {"op": "not", "condition": {
            "op": "compare", "variable_id": "story.missing", "comparison": "eq", "value": True,
        }}
        with self.assertRaisesRegex(ValueError, "condition_variable_missing"):
            validate_condition(condition, self.variables)
        with self.assertRaisesRegex(ValueError, "condition_variable_missing"):
            evaluate_condition(condition, {})

    def test_save_references_valid_graph_position_and_typed_values(self):
        self.assertTrue(validate_save(
            self.save, self.document, self.variables, self.graphs, self.entry_points,
        ))

    def test_duplicate_ids_are_rejected(self):
        document = copy.deepcopy(self.document)
        document["variables"].append(copy.deepcopy(document["variables"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate_id"):
            validate_document(document)

    def test_missing_node_reference_is_rejected(self):
        document = copy.deepcopy(self.document)
        document["graphs"][0]["nodes"][0]["next_node_id"] = "node.does_not_exist"
        with self.assertRaisesRegex(ValueError, "missing_reference"):
            validate_document(document)

    def test_invalid_event_payload_is_rejected(self):
        document = copy.deepcopy(self.document)
        effect = document["graphs"][0]["nodes"][1]["options"][0]["effects"][1]
        effect["payload"] = {"unknown": "value"}
        with self.assertRaisesRegex(ValueError, "invalid_event_payload"):
            validate_document(document)

    def test_save_missing_variable_value_is_rejected(self):
        save = copy.deepcopy(self.save)
        save["variable_values"] = save["variable_values"][:-1]
        with self.assertRaisesRegex(ValueError, "save_variable_missing"):
            validate_save(save, self.document, self.variables, self.graphs, self.entry_points)

    def test_save_document_mismatch_is_rejected(self):
        save = copy.deepcopy(self.save)
        save["document_id"] = "story.other"
        with self.assertRaisesRegex(ValueError, "save_document_mismatch"):
            validate_save(save, self.document, self.variables, self.graphs, self.entry_points)


if __name__ == "__main__":
    unittest.main(verbosity=2)
