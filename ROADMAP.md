# SEngine Roadmap

This roadmap is milestone-based. Dates are intentionally omitted until the project has a buildable baseline and measurable throughput.

## M0 — Architecture and validation

**Goal:** make foundational decisions with evidence, not guesses.

- [x] Define the story-driven 2D/3D product direction.
- [x] Establish Rust-first and runtime/editor separation as design constraints.
- [x] Record candidate subsystems and unresolved decisions.
- [ ] Compare engine foundations (including Bevy and Fyrox) against editor, runtime, and licensing requirements.
- [ ] Select a minimal vertical-slice stack and record exact versions and licenses.
- [ ] Define project-file compatibility and migration policy.

**Exit criteria:** a reviewed architecture decision with explicit trade-offs, a minimal dependency set, and a reproducible toolchain.

## M1 — Buildable runtime skeleton

**Goal:** open a window and run a tiny project through a stable runtime entry point.

- [ ] Create a Rust workspace with separate runtime, project-format, and editor crates.
- [ ] Establish logging, error reporting, configuration, and application lifecycle.
- [ ] Load and validate a minimal project manifest.
- [ ] Add CI for formatting, linting, and tests.
- [ ] Provide a headless test path where possible.

**Exit criteria:** a clean checkout builds in CI; a sample project launches; invalid project data produces actionable errors.

## M2 — Scene and asset foundation

**Goal:** create, save, reload, and inspect a small scene.

- [ ] Define stable scene/entity identifiers and transform hierarchy.
- [ ] Define typed asset references and import metadata.
- [ ] Implement serialization with schema versions and migrations.
- [ ] Add asset discovery, validation, and dependency tracking.
- [ ] Prove round-trip save/load with automated tests.

**Exit criteria:** a sample scene survives save/reload without losing identity or references.

## M3 — First 2D/3D rendering slice

**Goal:** render a minimal 2D scene and a minimal 3D scene through the same project workflow.

- [ ] Validate the chosen renderer and graphics backends.
- [ ] Implement camera, transform, material, and mesh/sprite workflows.
- [ ] Add resize handling and viewport presentation.
- [ ] Add a reproducible visual smoke test or capture procedure.

**Exit criteria:** both sample scenes render on at least one supported desktop platform.

## M4 — Narrative runtime

**Goal:** make a small branching story playable without editor dependencies.

- [ ] Define dialogue, speaker, choice, condition, and narrative-state data.
- [ ] Define deterministic event and transition semantics.
- [ ] Add localization-ready text identifiers.
- [ ] Add save/load of narrative state.
- [ ] Test branching, invalid links, conditions, and save compatibility.

**Exit criteria:** a playable sample story demonstrates branching, state changes, and save/load.

## M5 — Editor foundation

**Goal:** author the same project data visually.

- [ ] Project browser and asset inspection.
- [ ] Scene hierarchy, inspector, and 2D/3D viewport.
- [ ] Dialogue and branching graph editor.
- [ ] Undo/redo and safe save workflow.
- [ ] Clear diagnostics for invalid project data.

**Exit criteria:** the sample story and scenes can be created and edited without hand-editing project files.

## M6 — Visual gameplay logic

**Goal:** connect narrative and gameplay through a usable visual graph.

- [ ] Define a typed, serializable graph intermediate representation.
- [ ] Add nodes, pins, connections, validation, and execution semantics.
- [ ] Add conditions, events, variables, and timeline triggers.
- [ ] Add a text scripting escape hatch with a documented host API.
- [ ] Test graph execution independently of the editor UI.

**Exit criteria:** a sample game uses visual logic for interactions and narrative transitions.

## M7 — Production systems

- [ ] Physics integration for 2D and 3D.
- [ ] Animation state machines and timelines.
- [ ] Audio playback, mixing, and spatial audio.
- [ ] UI authoring and runtime.
- [ ] Particles, lighting, materials, and post-processing.
- [ ] Profiling, debugging, and runtime diagnostics.

Each subsystem must have a sample, tests, and documented limitations before being marked complete.

## M8 — Packaging and extensibility

- [ ] Plugin and extension API with versioning boundaries.
- [ ] Build profiles and reproducible packaging.
- [ ] Platform-specific export pipelines.
- [ ] Crash reporting and release diagnostics.
- [ ] Documented compatibility and support matrix.

**Exit criteria:** a sample game can be packaged and launched outside the editor on each platform explicitly declared supported.

## Release principle

A milestone is complete only when its exit criteria are demonstrated in a clean checkout. A folder, interface, mockup, or TODO list is not an implemented feature.
