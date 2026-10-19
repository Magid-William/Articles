# Format contract

The first table is a fixed-width ASCII drawing, not a normal Markdown table.
Spaces carry meaning. A Markdown formatter that reflows it has broken it.

## Table 1: breadboard map

Every ordinary cell is exactly four characters between pipes:

```text
| .  |    | R1 | 01 |
```

That is:

- empty hole: one space, a dot, two spaces;
- no hole: four spaces;
- occupied by a reference: one space, the reference, padding to two
  characters, one space;
- row number: one space, two digits, one space;
- header: the same rule, e.g. `| #  |`, `| A  |`.

The center-channel cell is the exception and is always exactly `|----|`
(four hyphens, no spaces).

The header, separator, and every data row have one cell per table column.
For a 16-column board that is 17 pipes and 81 characters per line. For the
12-column 170 board it is 13 pipes and 61 characters per line.

### 170 header

```text
| #  | A  | B  | C  | D  | E  |----| F  | G  | H  | I  | J  |
|----|----|----|----|----|----|----|----|----|----|----|----|
```

### 400 / 830 header

```text
| #  | +  | -  | A  | B  | C  | D  | E  |----| F  | G  | H  | I  | J  | +  | -  |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
```

### Data rows

- Keep the row count for the profile; do not omit or add rows.
- Number rows `01`-`17`, `01`-`30`, or `01`-`63`, depending on the board.
- Never abbreviate with `...` or "rest unchanged".
- A terminal cell is `.` or a reference. It is never blank.
- A rail cell is `.` or a reference on a rail row, and blank otherwise.
- The center cell is `----` on every data row.
- A cell holds one lead. Use another free hole on the same net instead of
  putting two references in one cell.
- References are 1-2 characters: `R1`, `J2`, `D1`, `P1`. Use `RA`, `RB`, ...
  rather than widening a cell if you run past `R9`.

## Table 2: components and wiring

Use exactly these six columns and content widths:

```text
| Location | Ref | Components | Value   | Reading | Note                        |
| -------- | --- | ---------- | ------- | ------- | --------------------------- |
```

Content widths are 8, 3, 10, 7, 7, and 27 characters. With one padding space
on each side of every cell, the full line is 81 characters.

- `Location` is the pair of endpoint holes: `G1:G4`, `R+3:F3`, `D5:L-5`.
- For a 2-pin part, Table 1 contains the reference at exactly two holes matching
  those endpoints.
- Keep existing rows in order and keep existing references unchanged unless
  the user asks.
- Leave `Reading` blank unless the user provides a value.
- Keep notes short enough for 27 characters. Put longer explanations below the
  table, not in the cell.
- Do not invent readings or values.

### Rail coordinates

Write rail endpoints as side + polarity + row:

- `L+3` = left `+` rail, row 03.
- `L-5` = left `-` rail, row 05.
- `R+3` = right `+` rail, row 03.
- `R-6` = right `-` rail, row 06.

The first table does not label the side of a rail; the column position does.
Table 2 uses the `L` / `R` prefix to disambiguate.

## Output rules

- Return both complete tables. Do not return only changed rows.
- Put each table in its own fenced `text` block.
- Do not put commentary inside the code blocks.
- Use ASCII spaces only: no tabs, no non-breaking spaces, no smart quotes.
- Do not use `│` in the canonical table. If the user asks for the Zed view,
  produce a separate display-only copy with only the `|` delimiters replaced
  by `│`.
- Flag inconsistencies instead of silently fixing them.

## Common mistakes

1. Reflowing the table to the longest cell. The cells are fixed at 4 characters.
2. Using `| . |` or `|  . |` instead of `| .  |`.
3. Using `| R1|` or `|R1 |` instead of `| R1 |`.
4. Forgetting the center cell or writing `| -- |` instead of `|----|`.
5. Truncating a 63-row table to 9 rows or using `...`.
6. Treating a blank rail row as a break in the rail bus.
7. Assuming `A1` and `A2` are connected because they share a column. They are
   different rows and different nets.
8. Putting two references in one cell instead of using another free hole on
   the same net.
9. Using `│` in the table that gets pasted back into the editor.
10. Writing a `Location` span that disagrees with the two reference cells in
    Table 1.
