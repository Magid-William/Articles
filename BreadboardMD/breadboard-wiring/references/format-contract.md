# Format contract

Table 1 is a fixed-width ASCII drawing. Spaces are data; do not reflow it.

## Table 1 cells

Every ordinary cell is exactly 4 characters between pipes:

```text
| .  |    | R1 | 01 |
```

- empty hole: `| .  |` (space, dot, two spaces);
- no hole: `|    |` (four spaces);
- occupied: `| R1 |`;
- row number: `| 01 |`;
- header: `| #  |`, `| A  |`.

The center cell is always `|----|` (four hyphens, no spaces).
16 columns -> 17 pipes, 81 characters; 12 columns -> 13 pipes, 61 characters.

### Headers

```text
| #  | A  | B  | C  | D  | E  |----| F  | G  | H  | I  | J  |
|----|----|----|----|----|----|----|----|----|----|----|----|
```

```text
| #  | +  | -  | A  | B  | C  | D  | E  |----| F  | G  | H  | I  | J  | +  | -  |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
```

### Data rules

Keep every row for the profile, numbered `01`-`N`; never use `...`. Terminal
cells are `.` or a reference; rail cells are `.` or a reference on rail rows
and blank otherwise; center cells are `----`. One lead per cell: use another
free hole on the same net if occupied. References are 1-2 characters (`R1`,
`J2`, `P1`); use `RA`, `RB`, ... past `R9` instead of widening a cell.

## Table 2

```text
| Location | Ref | Components | Value   | Reading | Note                        |
| -------- | --- | ---------- | ------- | ------- | --------------------------- |
```

Content widths: 8, 3, 10, 7, 7, 27. Full line: 81 characters.

- `Location` is the two endpoints: `G1:G4`, `R+3:F3`, `D5:L-5`.
- Each 2-pin reference appears exactly twice in Table 1, at those endpoints.
- Keep rows and refs in their existing order.
- Leave `Reading` blank unless supplied; do not invent values.
- Keep notes within 27 characters; put longer text below the table.

### Rail coordinates

`L+3` = left `+` row 03; `L-5` = left `-` row 05;
`R+3` = right `+` row 03; `R-6` = right `-` row 06.

## Output

Return both complete tables in fenced `text` blocks, with no commentary inside.
Use ASCII spaces only; no tabs, non-breaking spaces, or smart quotes. Keep `│`
out of the canonical table; for the Zed view, make a separate display copy.
Flag inconsistencies instead of silently fixing them.

Common mistakes: reflowing cells; `| . |` instead of `| .  |`; missing
`|----|`; truncating rows; treating a rail gap as a break; assuming `A1` and
`A2` connect; two refs in one cell; using `│` in the saved table.
