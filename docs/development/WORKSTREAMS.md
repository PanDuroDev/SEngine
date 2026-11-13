# Parallel development and integration policy

This document is the operating contract for all human and automated contributors working on SEngine.

## 1. Independent workstreams

Each daily worker owns one area. Workers must not all select the same next task.

| Stream | Owns | Must not take over |
|---|---|---|
| Runtime and engine foundation | Rust workspace, runtime lifecycle, project/scene/asset core, rendering and platform integration spikes, CI and build reliability | Narrative authoring semantics or editor panel implementation |
| Narrative and gameplay logic | Dialogue, branching, narrative variables/state, conditions, events, timelines, graph IR, story examples and headless tests | Renderer internals or editor layout |
| Editor and visual authoring | English-language editor shell, project browser, inspectors, scene/viewport integration, dialogue/logic graph interaction, undo/redo and authoring UX | Runtime execution semantics or low-level renderer implementation |
| Integration and release | Repository health, issue/PR triage, review quality, CI, dependency/license risk, safe merges, release notes and cross-stream compatibility | Starting overlapping feature implementations unless a small integration fix is necessary |

The stream table defines ownership, not permanent technology choices. Update it through a reviewed PR if the project structure changes.

## 2. No waiting and no dependency deadlocks

A daily run is one bounded work session, not a long-running agent that can wait for another agent.

- Never wait for a PR to merge, a review to arrive, a CI run to start, or another worker to finish.
- Never spend a run repeatedly polling the same pending dependency.
- If a task depends on an unmerged change, continue with an independent task in the stream, write a small interface contract, use a test double/mock at a documented boundary, or prepare a proposal. Do not duplicate the pending implementation.
- A worker may build against an agreed public interface only when that interface is documented and stable enough to test independently.
- Record the blocked dependency and its exact owner/PR in the report, then move on.
- Do not create placeholder crates, empty interfaces, or speculative abstractions only to appear busy.

## 3. Branch and PR isolation

- Never push ordinary work directly to `main`.
- Use one short-lived branch per coherent change, named `agent/<stream>/<YYYY-MM-DD>-<short-topic>`.
- Check existing branches and open PRs before creating a branch. Continue an existing stream-owned PR only when it is the same task and the branch is still usable; otherwise choose a fresh, non-conflicting branch.
- Do not share a working branch between streams.
- Keep one PR focused on one reviewable outcome. Split unrelated work.
- Avoid modifying another stream's owned files unless required for integration and explained in the PR.
- Do not repeatedly open PRs for the same unfinished objective. Update the existing PR or leave a precise issue when genuinely blocked.
- All PR titles, descriptions, commit messages, code comments, and repository documentation must be in English.

## 4. Every change must prove its value

Before writing code, inspect current source, tests, issues, branches, and PRs. Confirm the feature is not already implemented.

Each PR must state:

1. What changed and why.
2. What explicitly did not change.
3. Exact test/build/lint commands and actual results.
4. Manual checks performed, if any.
5. Known gaps, unsupported targets, and compatibility consequences.
6. New/updated dependencies, exact versions, licenses, and rationale.
7. The sample or user workflow that demonstrates the feature.

Do not claim a feature is complete because a type, trait, UI mockup, folder, or TODO exists. Prefer a small end-to-end slice with a real sample over broad scaffolding.

## 5. Shared contracts and data ownership

- The project format is the shared contract between runtime, editor, and narrative tooling.
- Persistent entities, assets, scenes, graph nodes, pins, dialogue entries, and story events need stable IDs.
- Persistent data must be independent of editor widget state.
- Runtime-facing data structures must not depend on editor-only crates.
- Any schema or public interface change must include migration/compatibility notes and tests.
- If streams need a shared contract, propose it in a short ADR or issue first. Keep it narrow.
- Use one authoritative project roadmap. Do not create competing status documents per stream.

## 6. Daily run protocol

Every worker must:

1. Read this document, the roadmap, current project status, and files relevant to its stream.
2. Inspect current `main`, its own open branches/PRs, relevant issues, recent commits, and CI/check results.
3. Pick the highest-value task that is independent and can make verifiable progress in one run.
4. Implement or document the result, add/update tests, and run relevant checks.
5. Open or update one focused PR when there is a reviewable diff.
6. End with a concise report containing PR/issue link, test evidence, blockers, and the next independent task.

If there is no worthwhile code change, do useful review, test-gap analysis, dependency/license verification, documentation, or a concrete issue. Do not make cosmetic commits to satisfy a daily quota.

## 7. Integration and automatic merge policy

The integration worker is authorized to merge routine, project-owned PRs that satisfy every applicable requirement below. It must never merge merely because a PR is old or has no comments.

### Required checks for code changes

- PR is open, not draft, targets `main`, and comes from this repository.
- Diff is focused, readable, and within the owning stream's scope.
- PR branch has no unresolved merge conflict and GitHub reports it as mergeable.
- All applicable CI checks and workflow runs have completed successfully. A pending, missing, skipped, neutral, or unknown required check is not a pass.
- Relevant unit, integration, serialization/migration, and sample tests exist and pass for the changed behavior.
- No unresolved review threads or requested changes remain.
- No duplicate PR or superseding change makes it obsolete.
- Dependency changes have current version, license, security/advisory, platform, and maintenance checks recorded.
- Documentation accurately describes implemented behavior.

If CI is not configured or required checks are absent, do not merge runtime/editor/logic code. The integration worker may add or request CI coverage instead. A strictly documentation-only PR may be merged without code CI after changed files and links are manually inspected.

### Changes requiring human review

Do not auto-merge changes that alter repository permissions/settings, secrets, release credentials, CI supply-chain privileges, project licensing, legal notices, security boundaries, destructive migrations, public compatibility guarantees, or broad architecture decisions. Flag them for the owner with a short rationale.

### Merge execution

- Merge only PRs authored from this project's own repository branches; do not merge external forks automatically.
- Re-read the PR head SHA immediately before merging and use it as the expected head SHA.
- Prefer squash merge for a focused PR unless history or the PR explicitly requires another method.
- Merge one PR at a time, then refresh `main`, checks, and dependent PRs before the next merge.
- Never merge a PR that depends on another unmerged PR. Integrate in dependency order.
- Never force-push, delete branches, close issues, or rewrite another contributor's work as part of routine integration.
- If any criterion is uncertain, do not merge. Explain the exact missing evidence and what would make it ready.

## 8. Stop conditions

Stop the current change and report it rather than guessing when credentials or permissions are missing, a dependency's license/security status cannot be established, a migration could destroy user data, an untestable platform is central to the change, streams have incompatible contracts, or the change requires a broad public API/license decision.

A blocked task is not a reason to stop the whole stream. Choose the next safe independent task.
