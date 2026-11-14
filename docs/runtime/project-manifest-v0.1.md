# Project Manifest Contract v0.1

- **Status:** Proposed Runtime-owned format; not an accepted public API.
- **Manifest format version:** 1
- **Scope:** Project identity, scene catalog, asset catalog, and the project's entry-scene reference.
- **Foundation:** Engine-neutral; does not select Fyrox or Bevy.

## Files

- `schemas/project/project-manifest.schema.json` defines the structural JSON Schema.
- `examples/project/minimal.project.json` is a valid empty-project manifest.

This is a manifest contract, not a scene-file format or a runnable game. Scene contents, asset import settings, runtime state, and editor layout are deliberately outside this version.

## 1. Ownership and boundaries

The manifest is project authoring data. It identifies the project and indexes scene and asset resources by stable IDs.

It must not contain:

- player save state or mutable per-player variables;
- renderer handles, ECS entity indices, pointers, GPU resources, or process-local IDs;
- editor selection, panel layout, graph zoom/pan, window geometry, or widget state;
- UI-framework types or engine-specific scene object serialization;
- absolute machine-specific paths.

The manifest is owned by the Runtime/project-format boundary. Editor tools may edit it through a project service, but editor widgets are not part of the serialized format.

The Narrative Document and Player Save are separate domain formats. A future project manifest may index narrative documents as assets, but it does not redefine dialogue, gameplay-graph, or save semantics.

## 2. Root file and versioning

The proposed root file name is `sengine.project.json`.

Required fields:

| Field | Meaning |
|---|---|
| `kind` | Discriminator; must be `sengine.project`. |
| `format_version` | Integer format version. Version 1 is defined here. |
| `project_id` | Stable identity for the project. |
| `name` | Human-readable project name; not an identity. |
| `entry_scene_id` | Stable ID of the initial scene, or `null` for a project with no scenes yet. |
| `scenes` | Scene catalog, keyed by each record's `id`. |
| `assets` | Asset catalog, keyed by each record's `id`. |

An optional `description` is informational only.

Version 1 readers must reject an unknown `kind`, unknown `format_version`, malformed required field, or unknown property. They must not guess how a newer format should be interpreted.

A future migration must be explicit and deterministic. It must preserve the project ID and every surviving scene/asset ID, produce actionable diagnostics, and never silently discard records or references. No migration is needed for this initial format because no prior project manifest exists.

## 3. Stable identity

- IDs are opaque, case-sensitive strings matching the schema pattern.
- `project_id` identifies the project. Scene and asset IDs identify resources within that project.
- Scene IDs and asset IDs share one project-wide uniqueness namespace. A scene and an asset cannot have the same ID.
- IDs must not be derived from array positions, display names, or file paths.
- Renaming or moving a resource preserves its ID.
- Reordering `scenes` or `assets` must not change identity or references.
- A deleted ID must not be reassigned to a different resource in the same project history.

The arrays preserve authoring/display order only. All references resolve by ID.

## 4. Scene catalog

Each scene record contains:

- `id`: stable scene ID;
- `path`: project-root-relative scene file path;
- `dimension`: `2d`, `3d`, or `mixed`.

The manifest does not define scene-file contents, node/entity identity, transforms, hierarchy, cameras, or serialization. Those require a separate scene-format contract and must not be inferred from this catalog entry.

If `scenes` is empty, `entry_scene_id` must be `null`. If one or more scenes exist, `entry_scene_id` must be non-null and resolve to exactly one scene record.

## 5. Asset catalog

Each asset record contains:

- `id`: stable asset ID;
- `path`: project-root-relative source/resource path;
- `kind`: one of `texture`, `mesh`, `audio`, `font`, `material`, `narrative`, `data`, or `other`.

This is a coarse catalog classification, not an importer contract. Importer settings, derived cache keys, dependency edges, generated artifacts, and platform variants are deferred.

A resource reference in future scene or project data must use its stable asset ID, not copy its path. Moving a file therefore changes the catalog path but does not invalidate references.

## 6. Path safety and portability

All paths are relative to the project root and use forward slashes.

A valid path must:

- be non-empty and not begin with `/` or a drive prefix;
- contain no backslash, control character, colon, empty segment, `.` segment, or `..` segment;
- identify a file path, not end in a slash;
- remain inside the project root after filesystem resolution.

The loader must resolve paths relative to the manifest directory, canonicalize existing path components, and reject symlinks or other filesystem indirections that escape the project root. A schema pattern is only an early structural check; it cannot prove filesystem containment.

For portable projects, validation must reject path collisions after Unicode NFC normalization and case folding. This avoids projects that work on a case-sensitive filesystem but alias resources on common case-insensitive filesystems.

The manifest loader must not silently rewrite paths or follow an external absolute path.

## 7. Semantic validation and diagnostics

JSON Schema checks structure and primitive types. A project validator must additionally check:

- project-wide duplicate IDs across scenes and assets;
- duplicate normalized paths across all catalog entries;
- `entry_scene_id` consistency with the scene catalog;
- referenced files exist when opening a complete project;
- path resolution remains inside the project root;
- unsupported scene dimensions or asset kinds are rejected rather than guessed.

Diagnostics should be structured and stable, with a code, severity, manifest path, object ID when known, and actionable explanation.

Initial diagnostic codes:

- `unsupported_project_kind`
- `unsupported_project_format_version`
- `duplicate_resource_id`
- `duplicate_resource_path`
- `entry_scene_missing`
- `entry_scene_unexpected`
- `invalid_project_path`
- `project_path_escape`
- `resource_file_missing`
- `unknown_resource_kind`

The same validator must be callable headlessly and by the editor. The editor may make diagnostics clickable, but must not own validation rules.

## 8. Conformance cases for the first project loader

These are acceptance cases for the future Runtime implementation, not claims that a loader exists.

| Case | Input | Expected result |
|---|---|---|
| Empty project | The supplied minimal manifest with no scenes/assets | Valid manifest; project opens without an entry scene. |
| Populated catalog | Two scenes, one asset, and a matching entry scene ID | Valid manifest; every resource resolves by stable ID. |
| Entry scene missing | Non-empty scene list and null entry ID | Reject with `entry_scene_missing`. |
| Entry scene unknown | Entry ID not present in the scene catalog | Reject with `entry_scene_missing`. |
| Unexpected entry | Empty scene list and non-null entry ID | Reject with `entry_scene_unexpected`. |
| Duplicate IDs | Reuse an ID between a scene and an asset | Reject with `duplicate_resource_id`. |
| Duplicate paths | Two resources resolve to the same normalized path | Reject with `duplicate_resource_path`. |
| Path traversal | A path contains `../` or a symlink escapes the root | Reject with `invalid_project_path` or `project_path_escape`. |
| Absolute path | A path begins with `/`, a drive prefix, or a UNC/backslash prefix | Reject before opening the resource. |
| Reordering | Reorder scene/asset arrays without changing IDs | Resource identity and entry-scene resolution remain unchanged. |
| Unknown version | Set `format_version` to an unsupported value | Reject with `unsupported_project_format_version`. |
| Missing resource | A catalog path does not exist when opening a complete project | Reject or return a structured missing-resource diagnostic; never silently substitute another file. |

## 9. Compatibility and explicit exclusions

This proposal introduces a new manifest format and has no existing project files to migrate.

It does not define:

- scene-file schema or scene runtime object model;
- asset import pipeline, metadata sidecars, dependency graph, or cache format;
- narrative execution or the Story & Editor contract;
- player save location or save serialization;
- renderer, ECS, physics, audio, windowing, or editor APIs;
- packaging/export configuration or platform promises.

The next Runtime-owned contract should define a minimal scene file and stable scene-object identity after the foundation spike identifies the appropriate integration boundary. Do not add an engine dependency merely to adopt this manifest.
