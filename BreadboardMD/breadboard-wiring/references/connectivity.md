# Connectivity model

## Base nets

1. **Row buses.** `A`-`E` in a row are one net; `F`-`J` in the same row are
   another. Different rows are separate; `E1` and `F1` are split by the center
   channel.
2. **Rails.** Left `+`, left `-`, right `+`, right `-` are four nets. Each is
   continuous along its side, across blank rail rows. Left/right and +/- are
   separate until a jumper joins them.
3. **Blanks.** A blank rail cell is a missing hole, not a break. A blank
   terminal cell is not a hole; only `.` is an empty terminal hole.

## Parts

Each reference appears at exactly two holes and is an edge between them:

```text
R1: G3 - G6
D1: E6 - F6
J1: R+3 - F3
```

- A 2-pin part joins its two nets; a jumper is a 2-pin part with no value.
- Both leads on the same **base** net = short.
- A jumper on the same base net = no-op; flag it.
- Do not call a part a short just because its endpoints connect through other
  parts. That is a normal series loop.

Example series circuit:

```text
R+3 -> J1 -> row 03 right -> R1 -> row 06 right -> D1 -> row 06 left -> J2 -> L-6
```

`R1` is not a short: its endpoints are connected through other parts, not by
the same base net.

## Rewiring

- Keep one lead per cell. If a hole is occupied, use another free hole on the
  same net (`F3`, `G3`, `H3`, `I3`, `J3` are one net).
- A part must span two different base nets; do not add a self-connecting
  jumper.
- When moving a part, restore its old holes to `.`, write it at the new holes,
  and update `Location` in Table 2. Never move onto an occupied hole.

## Quick checks

Every ref appears twice in Table 1 and once in Table 2; `Location` matches
those holes; no part is shorted by the base nets; rail rows and table width
match the profile.
