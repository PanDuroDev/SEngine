# SEngine 0.1: story-driven vertical slice

## Product thesis

SEngine should not try to win by being "another general-purpose engine with a node editor." Its defining workflow is making a playable story in which narrative structure and game-world interaction are designed together.

The first usable release should prove one complete creator journey, not claim a long list of disconnected engine features.

## The first creator journey

A creator should be able to:

1. Create a project and choose a 2D, 3D, or mixed presentation.
2. Organize the experience as chapters, scenes, and story beats.
3. Create reusable character/speaker profiles with portraits, names, audio references, and localization-ready display text.
4. Draw dialogue flow with choices, conditions, state changes, and transitions.
5. Build a small world scene and connect world interactions to the story.
6. Preview the game from the editor and inspect why a choice appeared, which event fired, and which variables changed.
7. Save, close, reopen, and continue the project and player state without losing references.
8. Build a standalone playable sample without shipping the editor.

## Core authoring surfaces

### 1. Story Map

A high-level overview of chapters, scenes, story beats, and transitions. It answers "where does the player go next?" without exposing low-level execution details.

### 2. Dialogue Graph

A dedicated story authoring surface for dialogue lines and speakers, choices and choice availability, conditions and variable changes, entry/exit points, scene transitions, and localization keys.

The graph should warn about unreachable dialogue, missing exits, dead ends, duplicate IDs, invalid conditions, and choices that can never appear.

### 3. Scene View

A shared project workflow for 2D and 3D scenes, with the appropriate specialized viewport and manipulators. A mixed project should move between 2D and 3D scenes without changing project identity or asset management.

### 4. Gameplay Logic Graph

A typed graph for world interactions and gameplay behavior: input, triggers, events, branches, variables, timers, and calls into runtime systems.

Do not force narrative dialogue and general gameplay into one untyped graph. They may reuse graph editor infrastructure, but their node sets, validation rules, and runtime semantics remain domain-specific.

### 5. Timeline

A sequence editor for timed story and gameplay events: dialogue timing, animation, audio, camera changes, visual effects, and event triggers. Timeline data must be deterministic and testable outside the editor.

### 6. Narrative Debugger

This is a high-value differentiator, not a cosmetic panel. During preview, show:

- current story node and scene;
- available and rejected choices, including why each rejected choice is unavailable;
- current narrative variables and state changes;
- event/trigger execution history;
- a trace that can be stepped through or exported for bug reports.

The debugger should make narrative bugs explainable rather than forcing creators to reproduce them by guesswork.

## Shared runtime contracts

- A versioned, human-readable project format with stable IDs and explicit migration.
- A deterministic narrative state machine independent of rendering and editor code.
- Typed conditions and variables, with clear behavior for missing or invalid values.
- Event messages with explicit ownership and ordering semantics.
- A typed graph intermediate representation for executable logic.
- A save format that separates project authoring data from player save data.
- Localization-ready text identifiers; do not hard-code editor UI language into runtime data.

## Deliberately deferred

- A custom SEngine programming language.
- Multiplayer/network replication.
- A universal plugin marketplace.
- Mobile/console export promises.
- Custom physics, audio, or rendering technology when maintained libraries meet requirements.
- Reproducing every feature of large engines before the story-driven workflow is proven.

## 0.1 acceptance scenario

The first end-to-end sample should be a small playable scene sequence:

- a character enters a 2D or 3D scene;
- interacting with an object starts a dialogue;
- the dialogue offers at least two choices;
- a condition hides or enables one choice based on a narrative variable;
- selecting a choice changes state and triggers an event;
- the event changes the current scene or timeline;
- player state is saved and restored;
- the editor's narrative debugger can explain the chosen path.

The same narrative runtime must run headlessly in automated tests. The sample must be playable outside the editor after packaging on the first supported desktop platform.

This single acceptance scenario is the measure for architecture decisions. New systems should be prioritized by how much they improve this workflow.
