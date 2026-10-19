# Breadboard Wiring skill

OpenCode skill for the fixed-width tables in [`../README.md`](../README.md).
It adds board profiles, templates, LED examples, and a generator/validator.

## Install

Copy to `~/.config/opencode/skills/breadboard-wiring/` (global) or
`<project>/.opencode/skills/breadboard-wiring/` (project). Or, from the repo
root, add to `opencode.jsonc`:

```jsonc
{ "skills": ["./BreadboardMD/breadboard-wiring"] }
```

## Use

Ask normally when pasting a table, or load it with `@breadboard-wiring`.
The skill edits both tables, validates them, and returns the full tables in
fenced `text` blocks.

## Commands

```sh
python scripts/breadboard.py new --board 830
python scripts/breadboard.py validate --board 830 examples/830-led.md
python scripts/breadboard.py zed examples/830-led.md
python -m unittest -v scripts/test_breadboard.py
```

`validate` exits 1 on errors; warnings do not fail the file.
Canonical data uses ASCII `|`; `zed` output is display-only.
