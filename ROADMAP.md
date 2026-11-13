# SEngine Roadmap

This is an outcome-based roadmap, not a calendar promise. A milestone is complete only when its acceptance scenario works from a clean checkout.

## M0 — Product and architecture validation

**Goal:** choose a foundation using one realistic sample rather than feature-list comparisons.

- [x] Define the story-first 2D/3D product direction.
- [x] Define the 0.1 end-to-end acceptance scenario.
- [x] Establish Rust-first, runtime/editor separation, stable project data, and typed graph IR principles.
- [x] Establish independent development streams and integration rules.
- [ ] Build comparable Bevy- and Fyrox-based spikes.
- [ ] Record exact dependency versions, direct/transitive licenses, platform support, and trade-offs.
- [ ] Choose the base engine and record the decision in an ADR.
- [ ] Select the first supported desktop target and pin a reproducible Rust toolchain.

**Exit criteria:** a runnable technical spike and a reviewed architecture decision backed by measured evidence.

## M1 — Buildable runtime and project foundation

**Goal:** open a project, validate it, and run a minimal game through a stable runtime entry point.

- [ ] Create a minimal Rust workspace with explicit runtime, project-format, and editor boundaries.
- [ ] Add logging, actionable errors, configuration, and application lifecycle.
- [ ] Define a versioned project manifest and stable identifiers.
- [ ] Add serialization validation and migration tests.
- [ ] Add CI for formatting, linting, tests, and supported target builds.
- [ ] Provide a headless runtime test path.

**Exit criteria:** a clean checkout builds in CI; a sample project loads and runs; invalid data produces useful errors.

## M2 — Shared scene and asset pipeline

**Goal:** create, save, reload, and inspect 2D/3D scenes without losing references.

- [ ] Define scene identity, hierarchy, transforms, and references.
- [ ] Define typed assets, import metadata, and dependency tracking.
- [ ] Support the first 2D and 3D asset formats required by the sample.
- [ ] Add asset validation and useful diagnostics.
- [ ] Prove save/load round-trips and migration behavior.

**Exit criteria:** sample scenes survive save/reload with stable entity and asset references.

## M3 — First visual runtime slice

**Goal:** render the sample world through the same project workflow.

- [ ] Render one 2D scene and one 3D scene.
- [ ] Implement camera, transforms, basic materials, and sprite/mesh presentation.
- [ ] Add viewport resize and editor/runtime separation.
- [ ] Add a reproducible visual smoke test on the first supported desktop target.

**Exit criteria:** the 2D and 3D sample scenes render in the runtime and can be inspected by the editor.

## M4 — Narrative runtime

**Goal:** execute a branching story without editor dependencies.

- [ ] Define speakers, dialogue entries, choices, conditions, variables, and narrative state.
- [ ] Define deterministic event and transition semantics.
- [ ] Add localization-ready text identifiers.
- [ ] Add player save/load separate from project authoring data.
- [ ] Test valid branches, unreachable nodes, dead ends, invalid conditions, state changes, and migration.

**Exit criteria:** the acceptance story executes headlessly, branches correctly, and survives save/load.

## M5 — Editor authoring foundation

**Goal:** author the acceptance story and scenes visually.

- [ ] Project browser and asset inspection.
- [ ] Scene hierarchy, inspector, and 2D/3D viewport.
- [ ] Story Map and Dialogue Graph.
- [ ] Undo/redo and safe save workflow.
- [ ] Validation panel with actionable file/object diagnostics.

**Exit criteria:** the acceptance story and scenes can be authored without hand-editing project files.

## M6 — Gameplay logic and timeline

**Goal:** connect world interaction to story and game behavior.

- [ ] Typed, versioned gameplay graph IR.
- [ ] Nodes, pins, edges, execution/data flow, and graph validation.
- [ ] Events, triggers, variables, and timers.
- [ ] Timeline tracks for dialogue, animation, audio, camera, and events.
- [ ] Text scripting escape hatch with a documented host API.
- [ ] Headless graph tests and Narrative Debugger trace.

**Exit criteria:** the sample game uses visual logic and timeline events, and the debugger can explain a path.

## M7 — Production systems

- [ ] Physics integration for 2D and 3D.
- [ ] Animation state machines and timelines.
- [ ] Audio playback, mixing, and spatial audio.
- [ ] UI authoring and runtime.
- [ ] Particles, lighting, materials, and post-processing.
- [ ] Profiling, debugging, and runtime diagnostics.

Each subsystem needs a working sample, automated tests where applicable, manual verification where automation is not practical, and documented limitations.

## M8 — Packaging and extensibility

- [ ] Plugin API with explicit versioning and permission boundaries.
- [ ] Reproducible build profiles and packaging.
- [ ] Export pipeline for each supported platform.
- [ ] Crash reporting and release diagnostics.
- [ ] Published compatibility/support matrix.

**Exit criteria:** the sample game launches outside the editor on every platform explicitly declared supported.

## First acceptance scenario

The first end-to-end sample is specified in [docs/product/vertical-slice.md](docs/product/vertical-slice.md). It must prove an interaction-triggered dialogue, conditional branching, state changes, an event/scene or timeline transition, save/restore, a usable editor preview, and a headless test of the same narrative runtime.

## Release principle

A folder, interface, mockup, benchmark disconnected from the sample, or TODO list is not an implemented feature. Do not mark a milestone complete until its exit criteria are demonstrated in a clean checkout.
