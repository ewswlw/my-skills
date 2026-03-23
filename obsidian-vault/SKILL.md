---
name: obsidian-vault
description: Search, create, and organize notes in this user's Obsidian vault with wikilinks and index notes. Use when working inside the Obsidian vault, finding or creating markdown notes, or maintaining MOC/index files.
---

# Obsidian vault (this workspace)

## Default vault path

Primary workspace when the user refers to "the vault":

`C:\Users\Eddy\Documents\Obsidian Vault`

If the active project is a subfolder (e.g. `Coding Projects\`), still respect vault-wide rules for any `.md` under the vault root.

## Conventions (high level)

- **Folders:** Title Case with spaces; topic-based; use index/MOC notes instead of deep hierarchies where possible.
- **Files:** Prefer clear titles; index files often use an "Index" suffix (e.g. `Algo Trading Index.md`).
- **Links:** Obsidian `[[wikilinks]]`; verify targets exist before creating new links; update backlinks when renaming.
- **Frontmatter:** When creating or editing vault markdown, follow the project's vault standards: required fields (e.g. `tags`, `description`, dates as applicable), dual tagging if the project uses `## Tags`, 2-space indent, no tabs.

## Workflows

### Search

Use **Glob**, **Grep** (ripgrep), or Obsidian search—prefer tools over shell `find`/`grep` on Windows unless the user prefers terminal.

### Create a note

1. Confirm folder placement and naming with vault rules.
2. Add valid frontmatter per project standards.
3. Link related notes and update the folder's **Index** note when the folder has 3+ markdown files (per project rules).

### Maintain index notes

When adding, renaming, or removing notes in a folder that uses an index, update that index so it stays complete.

## Python in the vault

If the task involves Python: use **`uv run`** and the project `.venv` per workspace rules—never bare `python` unless the user confirms the environment.

*Adapted from [mattpocock/skills/obsidian-vault](https://github.com/mattpocock/skills/tree/main/obsidian-vault) (MIT); paths and standards customized for this workspace.*
