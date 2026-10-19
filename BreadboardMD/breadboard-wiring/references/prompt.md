# Portable prompt

This is the short prompt for chat LLMs that do not load OpenCode skills. It is
673 characters. The skill adds board profiles, templates, examples, and the
validator; the prompt itself is intentionally board-size agnostic.

```text
Read Table 1 as a breadboard; Table 2 lists parts. A-E in a row are one net, F-J another; center splits them; each +/- rail is one continuous net per side, left/right separate; blank rail cell = missing hole, not a break. One lead per cell. Answer or rewire, then return both full tables in the same format. Table 1: every line is 5*columns+1 chars; ordinary cell is 4 chars between pipes: empty hole | .  |, no hole |    |, ref | R1 |, center |----|; keep row count and all rows, never "...". Table 2: keep columns, widths, and Location spans. Put each table in a fenced text block; no reflow, tabs, or prose inside the blocks; flag inconsistencies instead of fixing them.
```

For a specific board, add one line before the tables:

```text
Board: 830-point full-size, 63 rows, 10 terminal columns, four 50-hole rails.
```

or let the model infer the profile from the row count and columns.
