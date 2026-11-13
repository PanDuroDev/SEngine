# SEngine

**SEngine is an experimental, Rust-first 2D/3D game engine designed around creating story-driven games.**

Its goal is not to add a generic node canvas to another engine. SEngine aims to make the entire story-to-game workflow coherent: story maps, dialogue and branching, interactive 2D/3D scenes, gameplay logic, timelines, playtesting, and a debugger that explains narrative behavior.

The planned editor is English-language and visual-first. Creators should be able to work through direct manipulation, drag-and-drop, and typed visual graphs, with text scripting available as an escape hatch.

> **Current state:** architecture and technical validation only. SEngine is not yet a usable engine. No runtime, renderer, editor, physics, scripting, or export pipeline is implemented.

## Product definition

The first usable milestone is a complete, small story-driven game workflow:

- Create a project with 2D, 3D, or mixed scenes.
- Organize chapters, scenes, and story beats in a Story Map.
- Author dialogue, characters, choices, conditions, and state changes.
- Connect world interactions to narrative events.
- Preview the story and inspect rejected choices, variable changes, and event history.
- Save and restore both project data and player state.
- Package a playable sample without the editor.

See [the 0.1 vertical slice](docs/product/vertical-slice.md) for the acceptance scenario.

## Engineering principles

- **Story-first:** narrative is a core runtime domain, not a plugin bolted on later.
- **2D and 3D together:** share project, asset, and authoring workflows where practical.
- **Visual-first, code-capable:** typed graphs are executable project data, not decorative canvases.
- **Runtime/editor separation:** shipped games do not depend on editor-only code.
- **Stable project data:** human-readable files, persistent IDs, versioned schemas, and migrations.
- **Reuse before reinvention:** adopt maintained libraries only after compatibility, integration, and license checks.
- **Evidence over claims:** a feature counts as implemented only when a reproducible test or sample proves it.

## Current status

| Area | Status |
|---|---|
| Product vision and 0.1 acceptance scenario | Defined |
| Architecture and technical validation | In progress |
| Rust workspace and runtime | Not started |
| Scene, asset, and project format | Not started |
| 2D / 3D rendering | Not started |
| Editor and viewport | Not started |
| Narrative runtime and dialogue graphs | Not started |
| Gameplay visual scripting | Not started |
| Physics, animation, audio, and UI | Not started |
| Packaging and export | Not started |

## Development

- [Architecture decision 0001](docs/architecture/decisions/0001-engine-foundation.md)
- [Roadmap](ROADMAP.md)
- [0.1 vertical slice](docs/product/vertical-slice.md)
- [Parallel workstreams and merge policy](docs/development/WORKSTREAMS.md)

The initial foundation comparison is between Fyrox (integrated Rust 2D/3D engine and editor) and Bevy (modular Rust engine framework). Neither is approved yet; both must be tested against the same story-driven sample.

## Non-goals for the first milestone

- A custom SEngine programming language before runtime and graph semantics are proven.
- Rewriting mature rendering, physics, audio, or ECS systems without evidence.
- Empty crates and placeholder APIs presented as completed systems.
- Promising support for platforms that have not passed real build and export tests.
- A plugin marketplace or multiplayer infrastructure before the core authoring loop works.

## License

No project license has been selected yet. Until one is added, do not assume that this repository is licensed for reuse or redistribution.
