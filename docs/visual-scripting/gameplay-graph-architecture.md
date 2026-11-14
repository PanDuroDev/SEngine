# Gameplay Visual Scripting: Architecture and Contract Proposal

- **Status:** Proposed; requires Runtime, Story/Editor, and Scripting cross-stream review.
- **Owner:** Visual Scripting.
- **Scope:** General gameplay graphs, graph authoring/runtime boundary, and the first versioned graph asset contract.
- **Non-goal:** This proposal does not implement the engine runtime, dialogue/story semantics, scripting language, renderer, physics, audio, animation, or editor framework.

This proposal is engine-neutral. ADR 0001 is still Proposed, there is no Rust workspace or editor, and the project manifest/narrative contracts in PRs #2 and #4 are also proposals. The graph contract therefore avoids depending on a selected engine, UI toolkit, ECS, or unreviewed runtime API.

## 1. Repository findings

The current main branch contains no graph implementation, Rust source, tests, or workspace. The roadmap places typed gameplay graph IR, nodes, pins, edges, execution/data flow, validation, events, variables, and headless tests in M6. The 0.1 vertical slice requires a Gameplay Logic Graph for world interactions and a separate Dialogue Graph for narrative choices.

| Proposal | Relevance | Constraint |
|---|---|---|
| PR #2 — Narrative Document v0.1 | Dialogue graph semantics and stable-ID conventions | Do not reuse dialogue node semantics as gameplay execution semantics |
| PR #3 — Fyrox vs Bevy evidence | Editor/runtime foundation | No foundation selected; research is not an executable spike |
| PR #4 — Project Manifest v1 | Project and asset identity | Still proposed; do not hard-code its IDs or paths into this contract |
| PR #5 — Runtime architecture plan | Runtime host, event/command, diagnostics, cross-stream boundaries | Proposed; Runtime owns host lifecycle and bridge, not gameplay graph semantics |

The only current ADR is ADR 0001 and remains Proposed. Its graph principles are design direction, not proof of implementation: typed serializable graph IR, stable node/pin IDs, separate editor/runtime dependencies, and headless execution.

## 2. Graph domains and shared infrastructure

SEngine should have several graph-shaped authoring tools, not one universal interpreter with a kind label.

| Domain | Owns | Must not inherit |
|---|---|---|
| Gameplay Graph | World/gameplay events, execution flow, typed data flow, gameplay variables, host commands, reusable gameplay functions | Dialogue choice rules or story progression |
| Dialogue Graph | Dialogue lines, choices, availability, narrative effects, dialogue completion | Generic gameplay execution semantics |
| Story Map / Story Graph | Chapter/scene/beat organization and narrative-level transitions | Per-frame gameplay execution |
| State Machine Graph | States, transitions, guards, entry/exit behavior, state lifecycle | Unrestricted general-purpose execution |
| Animation Logic Graph | Animation parameters and transitions where needed | Ownership of animation runtime |
| AI Logic Graph | AI decision/task semantics, cancellation, scheduling | Implicit reuse of gameplay semantics |

**Shared infrastructure:** stable graph/node IDs, graph asset loading, node-definition discovery, typed port descriptors, connection indexing, editor canvas primitives, selection/undo commands, diagnostics, serialization versioning, and source mapping.

**Domain-specific:** allowed node definitions, graph entry/exit rules, execution model, type restrictions, validation rules, scheduling/cancellation, and runtime host capabilities. Each domain registers a distinct semantics profile. A shared canvas cannot silently interpret one domain using another domain's rules.

## 3. Layered architecture

Keep these modules independently testable and enforce one-way dependencies:

1. **Graph Authoring Model:** persistent graph identity, nodes, typed connections, variables, and references. No UI or engine handles.
2. **Node Catalog:** versioned node definitions supplied by domains/extensions: ports, data types, configuration schema, purity/effect classification, execution contract.
3. **Graph Validator:** structural, reference, type, domain, reachability, and execution-safety checks. Returns structured diagnostics; never repairs data silently.
4. **Graph Compiler / IR:** converts validated authoring data into an immutable executable program plus node/source map. Bytecode format remains undecided.
5. **Graph Runtime:** deterministic interpreter/VM or another measured strategy. No editor dependencies.
6. **Runtime Host Adapter:** narrow bridge to engine-owned entities, events, commands, clocks/timers, resources, and diagnostics.
7. **Editor Adapter:** canvas rendering and user interaction over authoring data and editor-only layout. It does not execute game logic.
8. **Serialization / Migration:** versioned graph assets, node-definition compatibility, deterministic migrations.

~~~text
Editor UI -> Authoring Model -> Validator -> Compiler -> Graph Runtime -> Runtime Host API
    |               |              |            |
    +-> Layout      +-> Serialization          +-> Source map / diagnostics
Node Catalog -> Validator / Compiler / Editor presentation
~~~

Runtime builds must not link graph canvas widgets. Graph runtime must not query editor selection, viewport state, or open documents.

## 4. Graph asset and identity model

### 4.1 Persistent graph document

The proposed Gameplay Graph v1 JSON document contains:

- format discriminator: sengine.gameplay-graph;
- schema_version and semantics_version;
- stable graph_id and graph_kind=gameplay;
- explicitly typed graph-local variables;
- stable node instances referencing catalog definitions and definition versions;
- explicit execution or data connections between node IDs and catalog-defined port IDs.

The machine-readable schema and fixture in this proposal establish a reviewable data boundary, not a final engine-wide project format.

### 4.2 Identity rules

- IDs are opaque, case-sensitive, stable strings. They are never array positions.
- Graph, node, variable, function, and custom-port IDs survive reorder, rename, save, and reload.
- A node instance references stable node_type_id and node_definition_version; its configuration is validated by that node definition.
- A connection endpoint is (node_id, port_id). Port IDs come from the versioned node definition, not display labels or array order.
- Removing/changing a port is a compatibility change requiring migration or a clear validation error.
- Runtime object/resource references use SEngine-owned stable IDs supplied by Runtime contracts. Never serialize ECS indices, engine handles, pointers, GPU handles, or memory addresses.
- Unknown schema/semantics/node-definition versions fail closed with actionable diagnostics.

### 4.3 Editor layout is not executable data

Node positions, zoom, pan, comments, visual groups, collapsed state, bookmarks, and editor selection belong in a separate versioned editor-layout sidecar keyed by graph/node IDs. They are not inputs to validation or execution and are not required by a headless game build.

A missing sidecar can be recreated with deterministic default layout without changing graph semantics.

## 5. Node and port model

A node definition is registered by a domain and contains:

- stable type ID and definition version;
- display name, category, description, search keywords, and visual classification;
- input/output port descriptors with stable IDs, direction, port kind, data type, cardinality, and optional/default behavior;
- configuration schema and defaults;
- execution contract: pure data operation, synchronous execution node, event source, latent operation, or host command;
- determinism and side-effect metadata;
- compile/validation hooks and runtime implementation identifier;
- compatibility/migration declarations.

A node instance stores only its stable instance ID, type ID, definition version, and authored configuration. It does not duplicate catalog port definitions.

### Port kinds

- **Execution:** control-flow input/output; carries no data value.
- **Data:** typed value input/output; does not advance execution by itself.

V1 built-in types: bool, i64, f64, string, entity_ref, resource_ref, and explicitly declared domain structs. Avoid implicit numeric coercion, string conversion, or wildcard ports initially.

A data input is required, optional with a declared default, or variadic only when the node definition explicitly supports it. A data output is single-source in v1 unless a future node type explicitly defines aggregation.

### Node extensibility

New nodes register through a domain/node catalog; adding a node must not require editing graph core. Extensions cannot invent global type coercions or bypass validation. Custom nodes declare versioned ports/configuration and provide validation/runtime behavior. Third-party plugin loading and ABI are deferred until the plugin trust/versioning decision exists.

## 6. Connection and validation rules

A connection is valid only when:

1. Both endpoint node IDs exist in the same graph.
2. Both port IDs exist in the referenced node definitions and are exposed in the declared directions.
3. Port kinds match: execution-to-execution or data-to-data.
4. Data types are exactly compatible under the domain's registered type rules.
5. Input cardinality is not exceeded; duplicate edges are rejected.
6. The graph domain permits the edge and node definitions are available at required versions.

V1 additional rules:

- Execution outputs may fan out only if their definition permits it. Multiple outgoing edges execute in authored order.
- Execution inputs accept at most one incoming edge unless a node explicitly defines merge semantics.
- Data inputs accept at most one incoming edge unless a node explicitly defines aggregation.
- Data-flow cycles are rejected. A future feedback/delay node may add cycles only with explicit tick/delay semantics.
- Execution loops use explicit loop/control nodes. Arbitrary execution cycles are rejected.
- Unreachable nodes, unconnected required inputs, missing entry points, unused variables, and unused nodes are diagnostics. Structural/type/execution-safety errors block compilation.
- Validation is non-mutating: never silently delete edges, coerce values, auto-create nodes, or rewrite IDs.

Diagnostics contain stable code, severity, graph/node/connection/port location when known, concise message, and optional machine-readable details. Editor presentation may add navigation/fixes, but validator owns the truth.

## 7. Execution semantics proposal

### 7.1 Gameplay Graph v1

- An event node is an execution entry point.
- Execution edges define which node activates next.
- Data edges define inputs evaluated for an activation.
- Pure data nodes are evaluated on demand and may be cached for the current activation only when declared pure.
- Side-effecting nodes execute only when reached by an execution edge.
- A branch activates exactly one output based on a valid boolean condition.
- A loop node owns explicit iteration state and cancellation behavior.
- Latent/timer nodes suspend through the host scheduler and resume via a continuation token. They never block the game thread.

### 7.2 Determinism and safety

Define stable ordering for event delivery, execution fan-out, and host command results. V1 should process an activation in a deterministic queue. Each activation carries graph ID, instance ID, event/activation ID, and execution budget.

Required guards: maximum node activations per event, loop iteration limits, recursion/call-depth limits, cancellation, stale entity/resource reference handling, and explicit error propagation. Exceeding a budget terminates the activation with a diagnostic rather than hanging the game.

Host operations may be nondeterministic (for example asynchronous resource loading). Such nodes declare that fact and return results through explicit continuation/event messages. Pure graph evaluation remains deterministic.

### 7.3 Compiler / IR decision

Do not select bytecode, register VM, or direct interpreter before a real benchmark and debugger prototype. The initial boundary is:

~~~text
ValidatedGameplayGraph -> CompiledGameplayProgram + SourceMap
~~~

The immutable program contains resolved node operations, execution links, typed data dependencies, and source-node mapping. Source maps preserve graph/node/port IDs for diagnostics and debugging. Compiled programs are derived caches rebuilt from graph assets and exact node-definition versions.

A direct interpreter is acceptable for the first headless conformance slice if it implements the same semantics. A later IR may replace it without changing the serialized authoring contract.

## 8. Variables, functions, events, and control flow

### Variables

V1 supports graph-local typed variables. Reads/writes are explicit nodes; a write occurs only when its execution input activates. Missing IDs or type mismatches are errors, never implicit defaults. Project, scene, entity, and persistent/player-state scopes require Runtime-owned storage contracts and are deferred.

### Functions and reusable graphs

A function is a separately identified graph asset with typed input/output parameters and explicit purity/effect classification. Calls reference function IDs and pinned interface versions. Recursion is rejected in v1; call depth and execution budgets are mandatory. Function graphs share compiler/runtime infrastructure but have function-specific entry/return semantics.

### Events and signals

Event nodes declare typed signatures and register with the Runtime host. The graph domain maps event signatures to entry nodes; Runtime owns event sourcing, dispatch lifecycle, ordering, threading, and shutdown. Do not create a second event bus inside graph core.

### Branches and loops

Branch has a boolean condition and distinct true/false execution outputs. Loops are explicit nodes with initialization, iteration, completion, and cancellation behavior. No hidden control-flow cycles.

## 9. Editor architecture and large-graph UX

The editor is a view/controller over the authoring model, node catalog, validator, and layout sidecar. User actions are commands so selection, connection creation, movement, deletion, paste, and layout operations support undo/redo.

Required surfaces:

- searchable node palette grouped by domain/category, with keyboard navigation;
- typed port visualization and connection previews;
- multi-select, box select, copy/paste with regenerated instance IDs and remapped internal edges;
- pan/zoom, minimap, fit-to-selection, align/distribute, optional auto-layout;
- comments and visual groups stored in layout metadata;
- validation panel with click-to-node navigation;
- execution highlighting, current activation, pin values, call stack, event/variable watch, pause/resume/step, and trace export;
- graph overview and bookmarks for large graphs.

Large-graph performance:

- maintain node/connection indexes; do not scan every edge for each hover or drag;
- spatially index node bounds and render only visible nodes/edges plus small overscan;
- batch connection rendering and avoid rebuilding all geometry on pointer movement;
- keep selection/hover transient and outside graph semantics;
- incremental validation for local edits, full validation before compile/save/export;
- cache compilation by graph content hash plus node-definition versions;
- virtualize palette/search results and debounce text search;
- auto-layout is explicit, cancellable, and non-destructive to semantics.

Do not choose egui, Fyrox UI, Bevy Feathers, or another graph-widget library until the engine/editor spike measures integration, keyboard navigation, accessibility, docking, undo/redo, and large-graph performance.

## 10. Debugging and execution inspection

Runtime tracing must work headlessly. Each trace record includes monotonic sequence number, timestamp/tick, graph and instance IDs, activation ID, node ID, event/call context, outcome, duration where measurable, and structured error data.

The debugger consumes trace snapshots/events; it must not alter execution semantics. Breakpoints and step controls are preview/debug capabilities, not serialized runtime instructions. Watch windows inspect declared variables and evaluated data pins without mutating them. Trace export follows Runtime redaction policy.

## 11. Cross-stream integration contracts

| Stream | Required from Runtime | Owned by Visual Scripting |
|---|---|---|
| Engine Runtime | Host lifecycle, event subscription/delivery, typed command/query bridge, stable entity/resource IDs, clock/timer scheduler, cancellation, diagnostic sink, preview lifecycle | Gameplay graph format, node semantics, validation, compile/execute orchestration, graph trace schema |
| Story & Editor | Shared editor shell/undo conventions and stable project/document references | Generic graph core only; no dialogue/story data semantics |
| Scripting Language & Runtime | Versioned host capability API and shared value/error conventions | Graph-side typed values and host-call adapter; no language parser/compiler |
| Physics & Simulation | Stable object references and collision/trigger event envelope | Physics nodes only after that contract exists |
| Audio & Animation | Stable resource/object IDs, command/query/event interfaces | Audio/animation nodes only after owner contracts exist |
| Asset Pipeline | Resource IDs, resolver/load request/result, invalidation and diagnostics | Resource-reference ports and asset-node UI integration |
| Integration & Quality | CI, headless test entry point, compatibility policy | Graph conformance tests, fixtures, performance baselines |

Do not modify stream-owned files to force these contracts. Propose a narrow Runtime API issue/ADR before depending on a concrete signature. The scripting stream must review whether a shared value representation or host API can be reused; no shared IR is assumed.

## 12. Validation and conformance test plan

The first fixture should be checked for:

- JSON syntax and schema conformance;
- unique graph/node/variable IDs;
- all connection node and port references resolving against a pinned node catalog;
- port direction and kind compatibility;
- exact data type compatibility;
- input cardinality and duplicate-edge rules;
- entry-point validity and execution reachability;
- forbidden execution/data cycles;
- deterministic branch selection and execution order;
- execution-budget termination;
- stale host references and command failure propagation;
- stable IDs and semantic equivalence after save/load.

Negative fixtures should cover unknown node definitions/versions, missing endpoints, reversed port direction, mismatched data types, duplicate edges, multiple connections to a single-input port, missing required inputs, execution/data cycles, missing entry points, and budget exhaustion.

The schema validates document shape only. The node catalog and semantic validator enforce graph rules; JSON Schema alone does not prove a graph executable.

## 13. Incremental implementation plan

1. **Contract and fixture (this change):** gameplay graph v1 schema, example, domain boundary, IDs, port and connection rules. Review with Runtime and Story before acceptance.
2. **Pure graph-core conformance:** implement Rust types/parser/validator after workspace/foundation decision; run positive and negative fixtures without editor or GPU.
3. **Minimal interpreter:** event entry, typed local variable read, comparison, branch, and a test host recording a command. Prove deterministic headless execution.
4. **Editor vertical slice:** graph canvas for the same fixture, node palette, connections, validation navigation, save/load, undo/redo.
5. **Runtime bridge:** real world interaction event, stable entity refs, host commands, trace and preview lifecycle.
6. **Functions, loops, timers, debugger controls, large-graph optimizations:** each behind conformance tests and measured samples.

Do not start a Rust crate or add dependencies until ADR 0001 selects the workspace foundation. This first independently reviewable artifact is the versioned data contract and fixture; executable conformance belongs in step 2 when a reproducible Rust test harness exists.

## 14. Open questions for cross-stream review

- What stable-ID type and namespace will the project manifest/runtime standardize?
- Does Runtime provide a typed event registry and deterministic dispatch ordering, or should activation order be isolated behind an adapter?
- What stable entity/resource reference types survive scene reload and save/load?
- Which shared value/error types should the Scripting stream expose, if any?
- How should preview pause/step interact with the selected engine scheduler and physics fixed-step?
- Should editor layout be a project sidecar or separate editor workspace asset? This proposal prefers a sidecar keyed by graph ID.
- Which engine/editor candidate can host a performant graph canvas without forcing editor dependencies into exported games?

Until answered, this proposal remains Proposed and no external stream API is accepted.
