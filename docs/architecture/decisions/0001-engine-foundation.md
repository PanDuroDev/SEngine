# ADR 0001: Engine foundation and architectural boundaries

- **Status:** Proposed, pending a runnable technical spike
- **Date:** 2026-11-13
- **Decision scope:** language, runtime/editor boundaries, subsystem ownership, and dependency-selection policy

## Context

SEngine is intended to become a 2D and 3D engine whose strongest workflow is authoring story-driven games: scenes, dialogue, branching choices, narrative state, events, timelines, and gameplay logic. Its editor should be English-language and visual-first, with drag-and-drop workflows, visual graphs, and an optional text scripting path.

This is a long-term product, not a demo that can be made credible by creating many empty crates. The first architecture must keep the project buildable, testable, and replaceable while minimizing the amount of foundational technology SEngine must maintain itself.

## Decision

### 1. Rust-first; no default C++ layer

Use stable Rust for the initial runtime, project model, editor host, tools, and build pipeline.

C++ is allowed only when a specific subsystem has a compelling technical reason to use a mature native library that cannot reasonably be replaced by a maintained Rust option. Any such integration must:

- have a written rationale and license review;
- be isolated behind a narrow C ABI boundary;
- define ownership, lifetime, threading, and error rules explicitly;
- include integration tests and a documented build strategy for supported platforms.

Do not add C++ merely to make the architecture look hybrid. A second language is an operational cost, not a feature.

### 2. Separate the game runtime from the editor

The editor is a development tool, not a runtime dependency.

The intended dependency direction is:

`editor -> project model + editor services -> runtime interfaces`

`game runtime -> runtime + project format + selected runtime plugins`

The shipped game must not link editor UI, editor panels, graph-canvas widgets, or editor-only file watchers unless a feature explicitly requires them at runtime.

Project data and runtime behavior must be testable without launching the editor.

### 3. Keep project data independent from editor widgets

Define serializable project formats and stable identifiers before building complex editor panels.

- Scene, dialogue, narrative, and gameplay graph data must not store UI widget state as authoritative content.
- Use stable IDs for entities, graph nodes, ports, assets, and story entries. Do not use array positions or editor selection indices as persistent identity.
- Include schema versions and explicit migrations for files that survive across releases.
- Treat caches and derived runtime data as rebuildable.
- Make validation errors point to the relevant file and object.

### 4. Make visual scripting a language-neutral graph model

The visual graph is not the runtime itself.

Define a typed, serializable graph intermediate representation (IR) with explicit nodes, pins, edges, data types, execution flow, and validation rules. The editor edits this IR; a compiler/interpreter executes it.

This allows the graph to be tested headlessly, supports undo/redo and future editor changes, and leaves room for more than one authoring frontend.

Dialogue branching and gameplay logic may share graph infrastructure, but they must retain domain-specific node types and validation. A dialogue choice is not merely a generic execution pin.

### 5. Treat narrative as a first-class runtime domain

The runtime should eventually provide explicit data models for:

- dialogue entries and speakers;
- choices and conditional availability;
- variables and persistent narrative state;
- events and triggers;
- timelines and timed transitions;
- localization keys and text resources;
- save/load and version migration.

The editor should author these structures directly. Do not bury the story model inside UI code or opaque script strings.

### 6. Reuse libraries, but do not select a full stack by popularity

The following are candidates for investigation, not approved dependencies:

| Concern | Candidate direction | Current decision |
|---|---|---|
| ECS / scheduling | `bevy_ecs` and Bevy application primitives | Strong candidate; validate API stability and integration boundaries |
| 2D/3D rendering | Bevy renderer or a direct `wgpu`-based layer | Unselected; prove viewport, materials, 2D and 3D before committing |
| Editor UI | `egui` ecosystem | Candidate for dockable editor UI; validate graph/viewport integration and accessibility |
| Physics | Rapier 2D/3D; compare Avian where ECS integration is relevant | Unselected; maturity and cross-dimensional feature parity matter |
| Audio | Kira or another actively maintained Rust audio layer | Unselected; validate codecs, mixing, spatial audio, and target platforms |
| Asset formats | glTF ecosystem plus image/audio format libraries | Prefer established formats; review each crate and transitive license |
| Serialization | Serde with a human-readable project format | Candidate; schema migration and stable IDs are mandatory |
| Gameplay scripting | A small embedded scripting runtime, evaluated after graph IR | Deferred; compare Lua/Rhai and host API ergonomics |
| Custom SEngine language | Possible future authoring layer | Explicitly deferred until runtime and graph semantics are proven |

A candidate becomes an adopted dependency only after a spike records: exact crate version, repository activity, supported Rust/toolchain/platform matrix, license expression and bundled assets, security/advisory state, integration cost, and a working test.

### 7. Do not build a custom language or foundational engine subsystem prematurely

A custom SEngine language is not part of the first milestones. First build a stable runtime API and a typed graph IR. Later, evaluate whether a custom language materially improves authoring, diagnostics, determinism, or hot reload compared with an embedded language.

Likewise, do not implement a custom ECS, renderer, physics engine, audio mixer, or file format without a demonstrated requirement that existing components cannot satisfy.

## Candidate landscape and trade-offs

### Bevy

Bevy is a serious candidate because it is Rust-native, data-oriented, modular, and already covers substantial 2D and 3D runtime needs. Its project documentation also warns that it remains early-stage, that features are missing, and that breaking API changes are frequent. It is dual-licensed MIT/Apache-2.0, with exceptions and third-party asset notices that still require per-dependency review.

**Implication:** investigate Bevy as a foundation or source of modular crates, but isolate it behind SEngine-owned project and runtime interfaces. Do not expose Bevy-specific types in saved project formats or public SEngine scripting APIs.

### Fyrox

Fyrox is another Rust engine worth comparing because it aims to provide a broader integrated engine/editor experience. Before adopting it, validate its current 2D workflow, editor extensibility, narrative/visual scripting fit, project format, export targets, and the cost of shaping its architecture around SEngine's product goals.

**Implication:** compare a ready-made integrated engine against a modular Bevy-based foundation using the same small story-driven vertical slice. Do not decide from feature lists alone.

### Physics

Rapier is the maturity baseline to compare against. Avian may offer tighter ECS integration in a Bevy-based design, but its own documentation describes it as younger and with fewer community resources. The choice must be based on required 2D/3D parity, joints, character controllers, determinism needs, performance, and integration behavior.

## First technical spike

Before creating a large workspace, build one minimal vertical slice that answers these questions:

1. Can a clean Rust application open a window and render one 2D sprite and one 3D mesh?
2. Can the same project model save and reload both scenes with stable identifiers?
3. Can a small dialogue graph with two choices execute without editor dependencies?
4. Can the editor inspect and modify the same data without becoming a runtime dependency?
5. Can the chosen dependencies build on the first explicitly supported desktop target?
6. Are all selected dependencies and assets compatible with the intended distribution model?

Compare at least one Bevy-based path and one Fyrox-based path before locking the engine foundation. Record build times, binary/runtime footprint where meaningful, integration complexity, missing editor capabilities, and license findings.

## Consequences

### Benefits

- Rust remains the default implementation language.
- Editor technology can evolve without changing the game data model.
- Story and graph systems can be tested without graphics or UI.
- Dependencies remain replaceable behind SEngine-owned interfaces.
- The project avoids prematurely maintaining a custom language or low-level engine stack.

### Costs and risks

- An SEngine-owned editor and narrative workflow still require substantial work.
- Abstraction boundaries can become over-engineered if introduced before a vertical slice.
- Bevy's rapid evolution may create migration work.
- A full-engine base such as Fyrox may accelerate early progress but constrain deep editor/runtime customization.
- Cross-platform support cannot be promised until each target has a working build and export test.

## Revisit this decision when

- the vertical slice has been implemented and measured;
- a candidate dependency cannot meet a documented requirement;
- editor/runtime separation causes measurable integration friction;
- scripting or graph execution requirements become concrete enough to compare runtimes;
- target platforms or distribution requirements materially change.

## References

- [Bevy project and design goals](https://bevy.org/)
- [Bevy repository and license notes](https://github.com/bevyengine/bevy)
- [Fyrox project](https://github.com/FyroxEngine/Fyrox)
- [Rapier physics](https://rapier.rs/)
- [Avian physics](https://github.com/avianphysics/avian)
- [wgpu](https://wgpu.rs/)
- [egui](https://github.com/emilk/egui)
- [Kira audio](https://github.com/tesselode/kira)
