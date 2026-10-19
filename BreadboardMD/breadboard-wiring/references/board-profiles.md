# Board profiles

| Profile | Rows | Rails | Table 1 columns | Line width |
|---|---|---|---:|---:|
| `170` mini | 17 | none | 12 | 61 |
| `400` half | 30 | 4 x 25 holes | 16 | 81 |
| `830` full | 63 | 4 x 50 holes | 16 | 81 |

Line width is `5 * columns + 1`.

- **170:** rows `01`-`17`, terminal `A`-`J`, no rails.
- **400:** rows `01`-`30`, terminal `A`-`J`; rail rows `01`-`05`, `07`-`11`,
  `13`-`17`, `19`-`23`, `25`-`29`. Rows `06`, `12`, `18`, `24`, `30` have no
  rail holes.
- **830:** rows `01`-`63`, terminal `A`-`J`; rail rows `03`-`07`, `09`-`13`,
  `15`-`19`, `21`-`25`, `27`-`31`, `33`-`37`, `39`-`43`, `45`-`49`, `51`-`55`,
  `57`-`61`. Rows `01`-`02` and `62`-`63` have no rail holes. Total: 630
  terminal + 200 rail = 830.

Each rail is one continuous net along its side, across blank rows. Left/right
and +/- are separate.

`3220` is 63 rows x 40 terminal columns with 7 buses; use four linked 830
blocks. For a custom board, define its rows, columns, rail rows, and table
width, then keep the same cell grammar.
