# Engine Foundation Evidence Snapshot — 2026-11-14

- **Status:** Investigation report; no engine selected.
- **Scope:** Runtime and engine foundation only.
- **Compared releases:** Fyrox 1.0.1 and Bevy 0.20.1.
- **Repository baseline:** `main` at `9404f31b9d5536879d27a4da1d52c69b7dd42612`.
- **Decision authority:** ADR 0001 remains Proposed. This report does not accept or amend it.

## 1. Repository state

The current `main` branch contains product and architecture documentation only. It has no `Cargo.toml`, Rust source, sample project, test harness, or GitHub Actions workflow. No engine, runtime, project model, renderer, or platform layer exists to benchmark in-place.

The only open PR at the start of this investigation is PR #2, owned by the Story & Editor stream. It proposes a narrative document/save contract and is not a Runtime dependency. It remains unmerged and is not treated as an accepted public API. No Runtime-owned branch or open Runtime PR existed.

This report is intentionally evidence and a reproducible comparison plan, not a substitute for the runnable spike required by ADR 0001.

## 2. Exact candidate package facts

| Property | Fyrox | Bevy |
|---|---|---|
| Release used for this snapshot | `fyrox` / `fyrox-impl` **1.0.1** | `bevy` **0.20.1** |
| Registry release date | 2026-03-28 | 2026-10-28 |
| Rust edition | 2021 | 2024 |
| Declared MSRV | Rust **1.87** | Rust **1.97.1** |
| Top-level license expression | MIT | MIT OR Apache-2.0 |
| Core architecture | Integrated scene-based 2D/3D engine | Modular ECS and plugin-based engine |
| Editor availability | Full native scene editor | No complete editor; editor-oriented UI building blocks |

Use exact versions in any spike. Do not use a floating `latest` dependency or the development branch.

### Maintenance snapshot

- Fyrox's registry package is still 1.0.1, but its public `master` branch was pushed on 2026-11-13. Recent commits include editor resource hot-reload work, inspector fixes, and cleanup. The 1.0 announcement describes a small team with limited resources. This is evidence of active development, but also a reason to inspect maintainer concentration and release cadence rather than equating a 1.0 label with a large support organization.
- Bevy 0.20.0 was released on 2026-10-08 and 0.20.1 followed on 2026-10-28. The 0.20 announcement records 227 contributors and 817 PRs for that release. Its repository was also actively updated on 2026-11-13. Bevy's crate documentation warns that API-breaking releases arrive approximately every three months and that migration effort is not guaranteed to be easy.

Repository stars and open-issue counts are recorded only as public activity context, not as quality or support guarantees.

## 3. Fit against the SEngine 0.1 workflow

| Requirement | Fyrox 1.0.1 | Bevy 0.20.1 | Current assessment |
|---|---|---|---|
| Clean project creation | Provides project manager, templates, and generated export CLI. The exact generated workspace and clean-build time still need measurement. | A new Cargo project can add Bevy directly. The exact cold build and required OS packages still need measurement. | Both are straightforward to start; neither has been built in this environment. |
| 2D + 3D in one project | First-class 2D/3D scene model and integrated renderer. | Explicit 2D and 3D feature sets, scenes, sprites, meshes, PBR, and materials. | Both meet the feature requirement. Compare scene authoring and mixed-scene transitions, not feature checklists. |
| Existing editor | Full native editor, scene hierarchy, asset browser, inspector, animation tools, and project workflow. | No complete editor. Feathers provides editor-oriented widgets, and Bevy 0.20 adds more controls and headless tab behavior. | Fyrox wins on immediate editor availability. |
| Custom editor integration | `fyroxed_base` is an editor library; `EditorPlugin` allows custom editor extensions. It is not a turnkey SEngine editor. Deeply custom surfaces still inherit Fyrox editor/UI concepts. | SEngine would build its own editor shell and authoring surfaces. Bevy UI/Feathers can supply widgets and accessibility/focus behavior, but not the complete product workflow. | Fyrox likely reduces initial editor work; Bevy offers more freedom but requires substantially more implementation. |
| Runtime/editor separation | The editor is in separate crates and Fyrox provides an export CLI. A generated project's actual runtime dependency graph must still prove that editor-only crates do not enter the game executable. | Engine plugins/features are modular and a game can omit editor-specific tooling. Bevy itself does not provide a full editor to accidentally ship. | Bevy has the cleaner starting boundary; Fyrox separation is feasible but must be checked with `cargo tree` and an exported build. |
| Headless execution | Engine plugins and scenes are available, but a graphics-free runtime path for the exact SEngine sample has not been demonstrated here. | `bevy_ecs` is independently usable and directly supports a World + Schedule without a window or renderer. | Bevy has the stronger documented headless ECS path. Fyrox needs an explicit headless spike. |
| World interaction to story | Fyrox plugins and scene nodes provide direct access to scenes and resources. This is convenient, but putting story semantics directly into engine plugins would couple project data to Fyrox. | ECS systems, resources, and events provide natural integration points for triggers and state. Bevy Entity IDs must not become persistent project IDs. | Both can integrate an engine-neutral narrative runtime. Bevy appears simpler for headless systems; Fyrox appears simpler for editor-visible scene integration. |
| Save/project identity | Fyrox has scene/resource serialization and UUID-based scene objects. SEngine still needs its own stable project IDs and migration rules. | Bevy scenes/world serialization exist, but entity identity and SEngine's project/asset contracts still need an adapter. | Neither removes the need for an SEngine-owned project format. |

### Important editor distinction

Fyrox's `EditorPlugin` is a real extension point, not proof that its editor can be reshaped into the complete SEngine experience. The 0.1 editor has separate Story Map, Dialogue Graph, Gameplay Logic Graph, Timeline, preview, and diagnostics workflows. A plugin demo with a panel or inspector is not enough; the spike must measure whether these surfaces can be integrated without forking or replacing major editor internals.

Bevy Feathers is also not a finished editor. Bevy's own 0.20 roadmap describes file-backed `.bsn` authoring, asset entities, and a remote inspector as future work. It is inaccurate to compare Bevy's UI widgets to Fyrox's complete editor and call them equivalent.

## 4. Dependency and license evidence

### Fyrox

The published `fyrox-impl 1.0.1` package declares MIT and Rust 1.87. Its direct dependency set includes the engine's own core, resource, animation, UI, graphics, material, and texture crates, plus (among others):

- `rapier2d` and `rapier3d` 0.32;
- `winit` 0.30;
- `gltf` 1.4;
- `image` 0.25.1;
- `symphonia` 0.5.4 with `all-codecs`;
- `rayon`, `libloading`, and `clap`.

The editor library `fyroxed_base 1.0.1` is a separate package and directly adds project/build tooling and editor facilities such as `cargo_metadata` 0.22, `notify` 8, `imageproc` 0.25, `open` 5, `toml` 0.9, and `toml_edit` 0.23.

This is a capable integrated stack, but it is not a tiny runtime dependency. The audio codec feature set, both physics dimensions, graphics/windowing, image processing, and editor file watching must be checked against the exact features used by the game build. Fyrox's own engine manifest documents feature-unification/rebuild concerns between editor and game builds when dependency features differ.

### Bevy

The published `bevy 0.20.1` package declares edition 2024, Rust 1.97.1, and `MIT OR Apache-2.0`. The facade crate depends on `bevy_internal 0.20.1`; the engine is split into many official crates.

Its default feature collection enables `2d`, `3d`, `ui`, and `audio`. The 2D and 3D profiles each include the default app/platform pieces, scenes, picking, and their renderer pipelines. This is convenient for a full game, but a headless or runtime-only SEngine target should explicitly disable defaults and select the smallest required feature set. Bevy also exposes separate collections for scene, render, platform, audio, UI, and development tooling.

### License and transitive-dependency status

The license expressions above are the top-level engine package declarations only. They are **not** a transitive license clearance.

Neither candidate has had its full resolved dependency closure audited in this run. No package count, complete SPDX expression list, bundled native-library list, or third-party asset/font license inventory is claimed. A real spike must commit a lockfile and run a license/advisory tool over the selected feature graph. Bevy's repository also records external-origin code with additional notices; its example assets are separately licensed and are not automatically included in published Bevy crates.

No new dependencies have been added to SEngine.

## 5. Platform evidence

| Target | Fyrox 1.0.1 | Bevy 0.20.1 |
|---|---|---|
| Windows / Linux / macOS | Officially listed as PC targets. | Desktop platforms are the primary supported baseline; platform-specific OS packages/toolchains are required. |
| WebAssembly | Export CLI explicitly supports `wasm`. | Supported with renderer/browser limitations and target-specific configuration. |
| Android | Export CLI explicitly supports Android; Android toolchain and target setup are required. | Possible, but requires mobile-specific build configuration and validation. |
| iOS | **Do not count as supported for 1.0.1.** The 1.0 export CLI lists only PC, Android, and WASM. Issue #726 records the maintainer removing iOS from 1.0 support because it was not tested. | Community projects have shipped iOS builds, but mobile toolchain and feature coverage still require a dedicated test. |

The Fyrox website has historically listed iOS, but its release-specific export options and the maintainer's issue response are stronger evidence for the 1.0 release boundary. SEngine must not advertise iOS support based on a website feature list alone.

For Bevy on Windows, the official setup guide requires the MSVC/Windows SDK/CMake toolchain. Linux and macOS also require their platform-specific development packages. A Rust-only codebase does not mean the native build toolchain has no non-Rust prerequisites.

## 6. Risks to validate

### Fyrox risks

- The native editor is a major head start, but deep SEngine-specific authoring may require large editor plugins or a fork.
- Runtime/editor feature unification can trigger duplicate engine builds or hot-reload problems if features differ.
- The engine package brings physics, audio, rendering, asset, and UI dependencies together; the exported runtime closure must be inspected.
- iOS is not a supported 1.0 target based on release-specific evidence.
- The public project is active, but the small maintainer team and gap between registry release and current master need monitoring.

### Bevy risks

- Rust 1.97.1 is a substantially higher toolchain floor than Fyrox 1.0.1's 1.87.
- The editor must be built by SEngine; Feathers does not supply the Story Map, graph editors, scene inspector, asset workflow, undo/redo, or export product.
- The roughly quarterly breaking API cadence creates ongoing upgrade and plugin compatibility work.
- The default feature set is broad; an explicit feature policy and lockfile are required to control build size and dependency exposure.

## 7. What was not measured

This run did not execute either candidate. The available execution container has no `rustc` or `cargo` binary. Therefore:

- no clean `cargo new` build was run;
- no 2D or 3D scene was rendered;
- no editor plugin or Feathers panel was built;
- no headless engine integration was executed;
- no binary size, memory, cold/warm build time, or rebuild time was measured;
- no `cargo tree`, `cargo metadata`, `cargo deny`, or `cargo audit` result exists;
- no Windows, Linux, macOS, WebAssembly, Android, or iOS build was run.

The build-duration figures shown by docs.rs are documentation-service observations, not comparable SEngine project build benchmarks, and are intentionally excluded from any performance conclusion.

## 8. Fair spike protocol

When a Rust toolchain is available, create two isolated spike workspaces outside the product workspace. Pin the same stable compiler (at least Rust 1.97.1 for Bevy 0.20.1) and use the same host machine, target, assets, and sample behavior.

Each spike must perform the same bounded tasks:

1. Generate a clean project and record exact commands, cold build time, warm incremental build time, and required system packages.
2. Load one 2D scene and one 3D scene in the same project; spawn a sprite and a mesh with camera/transform data.
3. Raise one world-interaction trigger and deliver it through an adapter to an engine-neutral event sink. Do not implement Dialogue Graph semantics in this Runtime spike.
4. Save and reload project/scene references and prove that persistent IDs survive array reordering and a fresh process.
5. Add one minimal editor extension: a Fyrox `EditorPlugin` panel versus a Bevy Feathers panel hosted by a minimal SEngine editor shell. Record what is reused and what must be built.
6. Build a standalone game target and inspect its dependency graph to prove editor-only crates are absent.
7. Record binary size, peak memory, cold/warm build time, and the exact steps needed to reproduce each result.
8. Run `cargo tree -e normal`, `cargo metadata --locked`, `cargo deny check licenses bans sources advisories`, and `cargo audit` against the committed lockfile and selected features. Record all direct/transitive crate versions and SPDX expressions.

Keep the same engine-neutral sample data and event contract in both spikes. Do not let one candidate implement a smaller scenario. Do not compare a full Fyrox editor to a Bevy widget gallery.

## 9. Provisional conclusion

There is not enough practical evidence to select a foundation.

- **Fyrox is the stronger first candidate if the primary risk is reaching a usable 2D/3D editor and scene workflow quickly.** Its native editor, project manager, extension API, and export CLI reduce the amount of foundational tooling SEngine must build.
- **Bevy is the stronger candidate if the primary risk is preserving complete control over a bespoke editor and a clean headless/runtime architecture.** Its modular ECS and feature model are attractive, but SEngine must fund and maintain a large editor/tooling layer and accept a higher MSRV and faster API churn.

The next decision should be made only after the equal spike protocol above has been executed. This report does not recommend adding either engine to the product workspace yet.
