# SEngine

**SEngine is an experimental, Rust-first 2D and 3D game engine focused on story-driven games.**

The long-term goal is an English-language visual editor where creators can build scenes, dialogue, branching narratives, events, timelines, and gameplay logic primarily through direct manipulation and visual graphs, while retaining the option to write code.

SEngine is at the **architecture and validation stage**. It is not yet a usable game engine. No renderer, physics runtime, editor, scripting system, or export pipeline is implemented.

## Project principles

- **Story-driven by design:** dialogue, choices, conditions, events, and narrative state are core authoring concepts, not add-ons.
- **2D and 3D together:** shared project, asset, scene, and workflow concepts where practical, with specialized tools where necessary.
- **Visual first, code when useful:** visual scripting must be a real authoring path, not a decorative node canvas.
- **Runtime/editor separation:** shipped games must not need the editor or editor-only dependencies.
- **Data ownership:** project files are explicit, versionable, inspectable, and designed for safe migration.
- **Reuse before reinvention:** prefer maintained, compatible open-source components when they meet the engine's requirements.
- **Evidence over feature claims:** a feature is considered implemented only when it is exercised by a reproducible example or test.

## Current status

| Area | Status |
|---|---|
| Architecture and technical validation | In progress |
| Rust workspace and runtime | Not started |
| 2D / 3D rendering | Not started |
| Scene and asset pipeline | Not started |
| Visual editor and viewport | Not started |
| Dialogue and narrative graph | Not started |
| Visual scripting | Not started |
| Physics, animation, audio, UI | Not started |
| Packaging and export | Not started |

## Development

The initial architecture and staged roadmap are documented in:

- [Architecture decision 0001](docs/architecture/decisions/0001-engine-foundation.md)
- [Roadmap](ROADMAP.md)

No engine dependencies have been committed yet. Candidate libraries must pass compatibility, maintenance, platform, integration, and license review before adoption.

## Non-goals for the first milestone

- Building a custom programming language before a working runtime exists.
- Writing a renderer, physics engine, or ECS from scratch without a demonstrated need.
- Creating placeholder modules that imply functionality that does not exist.
- Promising platform support before a real export test passes.

## License

No project license has been selected yet. Until one is added, do not assume that the repository is licensed for reuse or redistribution.
