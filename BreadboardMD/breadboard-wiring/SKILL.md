---
name: Breadboard Wiring
description: Read, edit, validate, and explain fixed-width breadboard maps (170/400/830) and component lists. Use when the user pastes a breadboard table or asks for breadboard wiring or rewiring help.
---

# Breadboard Wiring

## Workflow

1. Identify the board from `references/board-profiles.md`. If the user pasted a table, infer it from row count and columns.
2. Read `references/format-contract.md` before editing.
3. If starting fresh, copy `templates/<board>.md` or run `python scripts/breadboard.py new --board <board>`.
4. Parse Table 1 into nets using `references/connectivity.md`.
5. Make the requested change. Keep one lead per cell; if a hole is occupied, use another free hole on the same net.
6. Update Table 2. Keep existing rows, refs, values, and `Location` spans.
7. Validate: `python scripts/breadboard.py validate --board <board> <file>`.
8. Return both complete tables in fenced `text` blocks, with no commentary inside the blocks.

## Invariants

- A-E in a row are one net; F-J in a row are another; different rows are not connected.
- Each `+` and `-` rail is one continuous net per side. Left and right rails are separate; `+` and `-` are separate.
- A blank rail cell is a missing hole, not a break in the rail bus.
- Every ordinary cell is exactly 4 characters between pipes: `| .  |`, `|    |`, `| R1 |`. The center cell is `|----|`.
- Table 1 line width is `5 * columns + 1`. Keep every row; never use `...`.
- A 2-pin part must span two different nets.

## References

- `references/board-profiles.md`
- `references/format-contract.md`
- `references/connectivity.md`
- `references/prompt.md`
- `templates/`
- `examples/`
