# Board profiles

Use these profiles to decide the row count, table columns, rail holes, and
line width. The table orientation is the same for every board: rows run down
the page, A-J run across, and the center channel sits between E and F.

| Profile | Name | Rows | Terminal columns | Rails | Table 1 columns | Line width |
|---|---|---:|---|---:|---:|---:|
| `170` | 170-point mini | 17 | A-J | none | 12 | 61 |
| `400` | 400-point half-size | 30 | A-J | 4 x 25 holes | 16 | 81 |
| `830` | 830-point full-size | 63 | A-J | 4 x 50 holes | 16 | 81 |

Table 1 line width is always `5 * columns + 1`:

- 170: 12 columns -> `5 * 12 + 1 = 61`.
- 400 and 830: 16 columns -> `5 * 16 + 1 = 81`.

## 170-point mini

- Rows: `01`-`17`.
- Terminal holes: `A`-`J` on every row.
- Power rails: none.
- Table 1 header: `#`, `A`-`E`, center, `F`-`J`.

## 400-point half-size

- Rows: `01`-`30`.
- Terminal holes: `A`-`J` on every row.
- Power rails: left `+`, left `-`, right `+`, right `-`.
- Rail holes: 25 per rail.
- Rail rows: `01`-`05`, `07`-`11`, `13`-`17`, `19`-`23`, `25`-`29`.
- Rows `06`, `12`, `18`, `24`, and `30` have no rail holes.
- Each rail is one continuous bus along its side, including across the blank
  rows between its 5-hole groups. See `connectivity.md`.

## 830-point full-size

- Rows: `01`-`63`.
- Terminal holes: `A`-`J` on every row.
- Power rails: left `+`, left `-`, right `+`, right `-`.
- Rail holes: 50 per rail.
- Rail rows: `03`-`07`, `09`-`13`, `15`-`19`, `21`-`25`, `27`-`31`,
  `33`-`37`, `39`-`43`, `45`-`49`, `51`-`55`, `57`-`61`.
- Rows `01`-`02` and `62`-`63` have no rail holes.
- Each rail is one continuous bus along its side, including across the blank
  rows between its 5-hole groups. See `connectivity.md`.
- Total: 630 terminal holes + 200 rail holes = 830.

## 3220-point giant

- 63 rows x 40 terminal columns, plus 7 power buses.
- A single fixed-width Table 1 would be over 200 characters wide.
- Represent it as four linked 830 blocks or as a separate schematic, not as
  one table.

## Custom boards

If a board is not listed, define:

- row count;
- terminal columns;
- whether rails exist;
- the exact rows that contain rail holes;
- table columns and line width.

Keep the same cell grammar from `format-contract.md`. Add the profile to
`scripts/breadboard.py` only when the geometry is stable and testable.
