# Breadboard Wiring skill

An OpenCode skill for the fixed-width breadboard tables in
[`../README.md`](../README.md).

It adds what the portable prompt cannot carry:

- board profiles for 170, 400, and 830 point boards;
- blank templates;
- complete LED examples;
- a generator and validator that check row count, line width, rail pattern,
  reference pairing, `Location` spans, and shorts.

## Install

### Global

Copy this folder to the OpenCode global skills directory:

```text
~/.config/opencode/skills/breadboard-wiring/
```

### Project-local

Copy it to a project:

```text
<project>/.opencode/skills/breadboard-wiring/
```

Or point OpenCode at this folder from `opencode.jsonc` when working from the
repository root:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": ["./BreadboardMD/breadboard-wiring"]
}
```

The relative path is resolved from the active OpenCode working directory, so
use `./breadboard-wiring` instead when the working directory is `BreadboardMD/`.

## Use

Ask normally when you paste a breadboard table, or load it explicitly with
`@breadboard-wiring`.

The skill tells the agent to:

1. identify the board profile;
2. read the format contract;
3. edit both tables;
4. run the validator;
5. return the complete tables in fenced `text` blocks.

## Commands

From this folder:

```sh
# Print a blank 830 table and its component-table header
python scripts/breadboard.py new --board 830

# Write a blank 400 template to a file
python scripts/breadboard.py new --board 400 --out breadboard-400.md

# Validate a file containing one or two tables
python scripts/breadboard.py validate --board 830 examples/830-led.md

# Print a display-only copy with │ delimiters for the Zed view
python scripts/breadboard.py zed examples/830-led.md

# Run the tests
python -m unittest -v scripts/test_breadboard.py
```

`validate` exits with status 1 when it finds an error. Warnings, such as a
no-op jumper, do not fail the file.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Skill trigger, workflow, and invariants |
| `references/board-profiles.md` | 170/400/830 geometry and rail rows |
| `references/format-contract.md` | Exact cell grammar and Table 2 widths |
| `references/connectivity.md` | Netlist model, shorts, and rewiring rules |
| `references/prompt.md` | Portable 673-character chat prompt |
| `templates/` | Blank 170/400/830 tables |
| `examples/` | Complete 170/400/830 LED circuits |
| `scripts/breadboard.py` | Generator, validator, and Zed renderer |
| `scripts/test_breadboard.py` | Unit tests for the validator |

The canonical data is always ASCII `|`. The `zed` command is only a display
copy; do not save its `│` output as the working table.
