# ADR 0001: Engine foundation and architectural boundaries

- **Status:** Proposed, pending the 0.1 vertical-slice comparison
- **Date:** 2026-11-13
- **Decision scope:** language, runtime/editor boundaries, subsystem ownership, and dependency-selection policy

## Context

SEngine is a 2D and 3D engine whose defining workflow is authoring story-driven games: chapters, scenes, dialogue, branching choices, narrative state, events, timelines, and gameplay logic. Its English-language editor should be visual-first, with drag-and-drop workflows, typed visual graphs, an optional text scripting path, and a strong preview/debugging experience.

The project must avoid two traps: rebuilding mature technology without a reason, and adopting a full engine so deeply that the story-first experience cannot be shaped around it. Decisions must be tested against one shared playable vertical slice.

## Decision

### 1. Rust-first; no default C++ layer

Use stable Rust for the initial runtime, project model, editor host, tools, and build pipeline.

C++ is allowed only when a specific subsystem has a compelling technical reason to use a mature native library that cannot reasonably be replaced by a maintained Rust option. Any such integration must have a written rationale and license review, use a narrow C ABI, document ownership/lifetimes/threading/errors, and include integration tests and a reproducible build strategy.

Do not add C++ merely to make the architecture look hybrid. A second language is an operational cost, not a feature.

### 2. Separate runtime from editor

The editor is a development tool, not a game runtime dependency.

`editor -> project model + editor services -> runtime interfaces`

`game runtime -> runtime + project format + selected runtime plugins`

Exported games must not link editor panels, graph widgets, editor-only file watchers, or authoring databases. Project data and runtime behavior must be testable without launching the editor.

### 3. Keep project data independent from editor widgets

- Scene, dialogue, narrative, and graph data must not store UI widget state as authoritative content.
- Use stable IDs for entities, nodes, pins, assets, story entries, and events. Never use array positions or editor selection indices as persistent identity.
- Include schema versions and explicit migrations.
- Treat caches and derived runtime data as rebuildable.
- Validation errors must identify the file and object that caused them.

### 4. Treat graphs as data and programs, not canvases

Define a typed, serializable graph intermediate representation (IR) with nodes, typed pins, edges, execution flow, data flow, validation, and versioned node definitions. The editor edits this IR; a compiler/interpreter executes it.

Dialogue and gameplay logic can share graph infrastructure but must have different domain node sets and validation rules. A dialogue choice is not simply a generic execution pin. The headless runtime must execute graphs without editor UI.

### 5. Make narrative a first-class runtime domain

The runtime must eventually model dialogue, speakers, choices, conditional availability, variables, persistent narrative state, events, triggers, timelines, localization keys, player save data, and migrations.

Do not hide narrative behavior in opaque script strings or editor UI state. See [the 0.1 vertical slice](../../product/vertical-slice.md) for the acceptance scenario.

### 6. Select foundations by a measured vertical slice

The candidates below are investigation targets, not blanket approvals.

| Concern | Candidate | Current position |
|---|---|---|
| Integrated 2D/3D engine and editor | Fyrox 1.x | Leading candidate for the first prototype because it provides a Rust 2D/3D engine and scene editor under MIT; must validate extensibility and SEngine narrative workflow integration |
| Modular 2D/3D runtime | Bevy 0.20.x | Leading modular alternative; Rust-native, data-driven, and flexible, but SEngine would own more editor/product integration |
| ECS / scheduling | Bevy ECS or engine-native scene model | Do not mix scene and ECS models without a demonstrated need |
| Graphics abstraction | Engine-native renderer or direct `wgpu` | Unselected; avoid owning GPU backends before the viewport spike |
| Editor UI | Fyrox editor framework or egui ecosystem | Compare docking, graph canvas, viewport embedding, keyboard navigation, accessibility, and undo/redo |
| Physics | Fyrox-native physics, Rapier 2D/3D, and Avian | Compare 2D/3D parity, character controllers, joints, determinism, profiling, and serialization |
| Audio | Engine-native audio or Kira | Validate codecs, mixing, spatial audio, editor preview, and target platforms |
| Project serialization | Serde and a human-readable format | Candidate; stable IDs and migration tests are mandatory |
| Scripting | Typed graph IR first; evaluate Rhai or Lua later | Deferred until runtime APIs and execution semantics are proven |
| Custom SEngine language | Possible future layer | Explicitly deferred |

### 7. Current candidate evidence (reviewed 2026-11-13)

- **Fyrox:** the official repository describes a feature-rich Rust 2D/3D engine with a scene editor and identifies its license as MIT. The Rust ecosystem index reports Fyrox 1.0.1 and recent project activity. This materially improves its position as the first integrated-engine prototype; it does not prove that its editor can be adapted to SEngine's story-first workflow.  
  Sources: [Fyrox repository](https://github.com/FyroxEngine/Fyrox), [Rust game-engine ecosystem index](https://arewegameyet.rs/ecosystem/engines/).
- **Bevy:** Bevy 0.20 was announced on 2026-10-08. The release adds editor-oriented UI widgets and improvements to scenes, shaders, and rendering, but Bevy's own repository still cautions about missing features and frequent breaking API changes. It remains attractive for a modular custom engine, but it is not a ready-made SEngine editor.  
  Sources: [Bevy 0.20 release](https://bevy.org/news/bevy-0-20/), [Bevy repository](https://github.com/bevyengine/bevy).

These facts are a point-in-time snapshot. Re-check versions, maintenance, licenses, platform support, and dependency trees before pinning any crate. The license of a top-level engine does not automatically clear all transitive crates, media assets, fonts, or plugins.

### 8. Avoid premature custom technology

Do not build a custom programming language, ECS, renderer, physics engine, audio mixer, or asset format until a tested requirement demonstrates why existing components are insufficient.

Start with a stable host API and typed graph IR. Later compare embedded scripting options for hot reload, sandboxing, error messages, determinism, debugging, and versioning. Only then reconsider a custom language.

## First technical spike: the same story, two foundations

Build the smallest comparable prototype on both candidate paths rather than benchmarking unrelated demos.

1. Create one project containing a 2D scene and a 3D scene.
2. Load a speaker profile and a dialogue graph with two choices and one conditional choice.
3. Execute the narrative state machine headlessly, then connect a world interaction to it.
4. Save and reload project data and player state with stable IDs.
5. Show the scene and dialogue in the editor; record the cost of extending the editor.
6. Build the sample on the first supported desktop platform.
7. Record exact crate versions, build time, binary/runtime footprint where meaningful, memory profile, integration effort, missing features, and all direct/transitive licenses.

Compare implementation effort and product fit, not only frame rate or feature counts. A technology that renders a demo quickly but makes story authoring awkward is not the right foundation.

## Consequences

### Benefits

- Rust remains the default implementation language.
- Editor technology can evolve without changing game data.
- Narrative and graph systems can be tested without graphics/UI.
- Dependencies can be replaced behind SEngine-owned project/runtime boundaries.
- The first product is judged by a complete story workflow.

### Risks

- Fyrox may accelerate the first editor but constrain deeper editor customization.
- Bevy may give more architectural freedom but require substantial editor and tooling work.
- Too many abstractions before the first sample would slow both approaches.
- Cross-platform support cannot be promised until each target has a real build and export test.

## Revisit when

- the same 0.1 acceptance scenario has been implemented on both foundations;
- a candidate fails a documented requirement;
- a public interface creates measurable friction;
- a scripting/runtime requirement is concrete enough to benchmark;
- target platforms or distribution requirements change.

## References

- [Fyrox repository](https://github.com/FyroxEngine/Fyrox)
- [Fyrox documentation](https://fyrox.rs/)
- [Bevy 0.20 release](https://bevy.org/news/bevy-0-20/)
- [Bevy repository](https://github.com/bevyengine/bevy)
- [Rapier physics](https://rapier.rs/)
- [Avian physics](https://github.com/avianphysics/avian)
- [wgpu](https://wgpu.rs/)
- [egui](https://github.com/emilk/egui)
- [Kira audio](https://github.com/tesselode/kira)
