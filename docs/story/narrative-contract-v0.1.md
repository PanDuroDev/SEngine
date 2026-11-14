# Narrative Document Contract v0.1

- **Status:** Proposed interface for cross-stream review; not an accepted public API.
- **Schema version:** 1
- **Owner:** Story and editor authoring
- **Scope:** Narrative authoring data and player narrative save data only.

This contract gives the Story/Editor and Runtime streams a concrete shape to review before either side commits to an implementation. It is deliberately separate from the future project manifest, scene format, renderer, and gameplay-logic graph. It does not select a runtime foundation or add a dependency.

## Files

- `schemas/narrative/narrative-document.schema.json` is the machine-readable shape for both document kinds.
- `examples/narrative/first-contact.narrative.json` is a small authoring document for an archive-door interaction.
- `examples/narrative/first-contact.save.json` is a separate player save snapshot.

The JSON Schema validates structural shape. It cannot validate all cross-references or execution semantics; those are normative rules below and must be enforced by a semantic validator/runtime.

## 1. Ownership and separation

A **Narrative Document** is project authoring data. It defines variable declarations and defaults, speakers, event payload contracts, entry points, and dialogue graphs.

A **Player Save** is mutable player state. It stores the Narrative Document ID, current narrative position, and current variable values. It does not copy speaker definitions, dialogue text, node definitions, or editor layout.

The following must never be serialized into either document as authoritative game data:

- selected node, selected asset, active panel, zoom, pan, window geometry, or other editor widget state;
- renderer handles, GPU resources, ECS entity indices, pointers, or process-local object addresses;
- array indices used as persistent identifiers.

Editor-only graph layout may be stored later in a separate sidecar format with its own version. Runtime and project APIs must not depend on any UI framework types.

## 2. Identity and versioning

- IDs are opaque, case-sensitive strings matching the schema pattern. Use stable, namespaced IDs such as `node.archive.choice` or `story.has_archive_key`.
- Document, entity, graph, node, and option IDs must be unique across the Narrative Document. Payload field IDs are unique within their event type; payload keys use those field IDs.
- Reordering an array must not change identity or behavior. Array order is presentation order only where explicitly stated.
- Never recycle an ID for a different object. Renames preserve IDs.
- `schema_version: 1` identifies this contract's structural version. It is not the application's release version.
- Unknown schema versions must fail closed with an actionable diagnostic. Do not guess a newer format.
- A migration must be explicit, deterministic, preserve IDs where the logical object survives, and include before/after fixtures. No migration may silently discard player state.

## 3. Dialogue graph model

This version defines a **Dialogue Graph**, not a generic graph language.

Supported node kinds:

| Kind | Required data | Behavior |
|---|---|---|
| `line` | `speaker_id`, `text_key`, `next_node_id` | Resolve the speaker and localized text, display the line, then advance to the referenced node. |
| `choice` | ordered `options` | Evaluate availability for every option and expose available options in authored order. |
| `end` | node ID | Complete the dialogue graph. |

Each option has its own stable ID, text key, target node, optional availability condition, and ordered effects. A choice selection is sent by **option ID**, never by its visible row index.

A graph's `entry_node_id` must reference a node in that graph. Every line's `next_node_id` and every option's `target_node_id` must also resolve within the same graph. Speakers, variables, and event types must resolve in the containing document.

The editor may share canvas, selection, zoom, and connection-drawing infrastructure with other tools. It must not erase the distinct Dialogue Graph semantics or serialize generic untyped pins as a substitute for the option/line model.

## 4. Conditions and value typing

Variables support only `boolean`, `number`, and `string` in version 1. The declared type is authoritative.

Conditions are typed expression trees:

- `compare`: compare one declared variable with a scalar literal using `eq`, `ne`, `gt`, `gte`, `lt`, or `lte`;
- `all`: logical AND over one or more child conditions;
- `any`: logical OR over one or more child conditions;
- `not`: logical NOT over one child condition.

No implicit coercion is allowed. Boolean, number, and string values are not interchangeable. Ordered comparisons (`gt`, `gte`, `lt`, `lte`) are valid only for numeric variables in version 1; equality/inequality require an exact matching scalar type.

Evaluation is fail-closed. A missing variable, unknown variable ID, mismatched literal type, or unsupported comparison makes the containing condition invalid and unavailable, not true. The evaluator emits a structured diagnostic explaining the invalid reference/type. A `not` node must not turn an invalid child into an available choice.

An option without `availability` is always available. An option with a valid condition is available only when the result is true. If no options are available, the runtime returns an explicit `no_available_choices` result and a diagnostic; it must not auto-select an option or silently end the graph.

## 5. Effects, ordering, and event delivery

Version 1 supports three choice effects:

- `set_variable`: assign a scalar to a declared variable of the exact declared type;
- `add_number`: add a number to a declared numeric variable;
- `emit_event`: emit an event declared in `event_types`, with a payload conforming to that event's field definitions.

Effects execute in their authored array order. Before committing a selected option, the runtime validates the option ID, re-evaluates its availability against the current state, validates every effect and event payload, and stages all variable changes. The choice is atomic: if any effect is invalid, none of its variable changes are committed and no event is emitted.

After successful validation, staged variable changes are committed and emitted events are appended to a FIFO queue in effect order. The narrative layer returns those events to the host; it does not directly manipulate scenes, timelines, rendering, or editor objects. The host owns event consumption and maps event IDs such as `event.scene.transition` or `event.timeline.play` to its own systems.

A stale option selection (for example, a UI action from an earlier state) is rejected after re-evaluation. The runtime returns a `choice_unavailable` diagnostic and leaves state unchanged.

## 6. Entry points and integration boundary

An `entry_point` maps an external stable trigger ID to a Dialogue Graph ID. In the sample, `interaction.archive_door` is expected to be raised by a world-interaction system owned outside this contract.

This is an integration seam, not an implementation of Gameplay Logic Graph. Gameplay Logic Graph must have its own typed node definitions, validation, and execution semantics. It may emit the entry-point trigger, but it must not be represented as a Dialogue Graph or forced into this dialogue-specific node set.

The Runtime stream owns the project manifest, scene/asset identity resolution, application lifecycle, and host event dispatch. This contract only requires stable IDs at those boundaries. A future shared project manifest may own scene and asset references; it must not duplicate or silently redefine the IDs here.

## 7. Player save and restore

A Player Save references its Narrative Document by `document_id` and stores:

- a stable `save_id`;
- the active entry point, graph, and node IDs;
- the current values of declared variables, keyed by `variable_id` in the serialized list.

The save's `variable_values` must contain at most one value per variable ID. Each value must match the variable's declared type. Restore must validate the document ID, schema version, graph/node/entry-point references, variable IDs, and value types before changing live state.

A document mismatch or invalid save must produce an explicit restore error. Do not silently apply values to similarly named variables, fall back to array positions, or partially restore a save. Project defaults are used only when creating a new player state, not to conceal a corrupt existing save.

## 8. Static validation and diagnostics

A semantic validator must check at least:

- duplicate IDs across the document;
- missing graph, node, speaker, variable, event-type, and entry-point references;
- event payloads with missing required fields, unknown fields, or incorrect types;
- effects whose assigned variable type does not match the declared type;
- numeric addition against a non-numeric variable;
- invalid comparison types and missing variables;
- unreachable dialogue nodes from the graph entry;
- graphs with no reachable `end` node;
- cycles that cannot reach an `end` node;
- player saves whose document, graph position, or variable values do not match the authoring document.

Diagnostics are data, not UI state. Each diagnostic should include a stable code, severity, document ID, object ID when known, and a human-readable explanation. The editor can render a clickable diagnostic and navigate to its object, while headless tests can assert on the same code and IDs.

Recommended initial diagnostic codes include `duplicate_id`, `missing_reference`, `invalid_value_type`, `invalid_event_payload`, `condition_variable_missing`, `condition_type_mismatch`, `choice_unavailable`, `no_available_choices`, `unreachable_node`, `no_reachable_end`, `non_terminating_cycle`, `save_document_mismatch`, and `save_position_invalid`.

A reachable cycle is not automatically invalid; intentional loops may be useful. A cycle with no possible path to an `end` node must be reported. A node that cannot be reached from the entry node must be reported as unreachable.

## 9. Conformance cases for the first runtime implementation

These are acceptance cases for the future headless runtime, not claims that an interpreter already exists.

| Case | Input / action | Expected result |
|---|---|---|
| Valid sample | Load `first-contact.narrative.json` | Structural and semantic validation succeeds. |
| Conditional choice hidden | Default `story.has_archive_key=false` | `choice.use_key` is unavailable; `choice.leave` remains available. |
| Conditional choice shown | Set `story.has_archive_key=true` | `choice.use_key` becomes available. |
| Choice executes effects | Select `choice.use_key` | Trust becomes 1; one `event.timeline.play` is queued; position advances to `node.ending`. |
| Event order | Emit two events in one option | Queue preserves their order in the effects array. |
| Invalid event payload | Omit a required field or provide an unknown/wrongly typed field | Reject the option atomically with `invalid_event_payload`. |
| Atomic effect failure | Put a valid variable update before an invalid effect | No variable change is committed and no event is emitted. |
| Stale choice | Select an option after its condition becomes false | Reject with `choice_unavailable`; state is unchanged. |
| Duplicate ID | Reuse a node, option, speaker, variable, or event ID | Reject with `duplicate_id`; payload field IDs are checked within their event type. |
| Missing variable | Reference an undeclared variable in a condition | Condition is invalid and false; diagnostic identifies the option/condition. |
| Type mismatch | Compare a number variable with a string or add to a boolean | Validation/evaluation fails closed with `invalid_value_type`. |
| Unreachable node | Add a node not reachable from the entry | Report `unreachable_node`. |
| Dead end | Reference a missing target or provide no reachable end | Report the missing reference or `no_reachable_end`. |
| Non-terminating cycle | Create a reachable cycle with no path to an end | Report `non_terminating_cycle`. |
| Save round-trip | Save and restore the active node and variable values | IDs and values are preserved exactly. |
| Save mismatch | Restore a save whose `document_id` differs | Reject atomically with `save_document_mismatch`. |
| Migration | Load an older supported save through an explicit migration | Preserve surviving IDs and values; report any explicit migration decision. |

## 10. Deliberate exclusions

This proposal does not define:

- the project manifest or scene/asset file formats;
- Gameplay Logic Graph nodes or execution;
- timeline track authoring or timing semantics;
- a scripting language or plugin API;
- localization catalogs or actual text assets;
- renderer, physics, audio, editor widget, or export APIs.

Those boundaries remain owned by their respective streams. Do not add Rhai, Lua, a graph library, or an engine dependency to adopt this data contract.


## 11. Executable contract checks

A standard-library Python conformance harness lives at `tests/narrative/test_narrative_contract.py`. Run it from the repository root:

```sh
python -m unittest discover -s tests/narrative -v
```

The harness checks local schema-reference resolution, the sample's semantic references and types, conditional-choice visibility, stale-choice rejection, ordered event output, atomic effect failure, fail-closed invalid conditions, duplicate IDs, invalid event payloads, and complete typed save validation.

This harness is an executable specification for the proposed data contract. It is **not** the production narrative runtime and does not replace a standards-compliant JSON Schema validator or the future Rust headless runtime tests. The repository currently has no CI workflow; the Integration stream owns adding the repository-wide CI gate. Keep this contract Proposed until the Runtime stream reviews it and automated checks are wired into CI.
