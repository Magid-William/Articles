# Connectivity model

Use this model to answer "what is connected to what" and to check rewiring.

## Base nets

Build the base nets first. These exist before any component or jumper is added.

1. **Row buses.**
   - In one row, `A`-`E` are one net.
   - In the same row, `F`-`J` are a separate net.
   - Different rows are separate.
   - `E1` and `F1` are separated by the center channel.
   - `A1` and `A2` are not connected just because they share a column.

2. **Power rails.**
   - Left `+`, left `-`, right `+`, and right `-` are four separate nets.
   - Each rail is one continuous bus along its side, even across rows where
     the hole pattern has a gap.
   - The left and right rails are separate until a jumper joins them.
   - The `+` and `-` rails are separate.

3. **Blank cells.**
   - A blank rail cell is a missing hole, not a break in the rail bus.
   - A blank terminal cell is not a valid hole on these profiles; only `.` is
     an empty terminal hole.

## Add parts

Every reference appears at exactly two holes. Treat each part as an edge
between its two endpoints:

```text
R1: G3 - G6
D1: E6 - F6
J1: R+3 - F3
```

- A resistor, LED, capacitor, or other 2-pin part joins its two nets.
- A jumper is just a 2-pin part with no value; it joins its two nets.
- A part whose two leads are on the same **base** net is a short.
- A jumper whose two leads are on the same base net is a no-op; flag it.
- Do not treat a part as a short just because its endpoints are connected
  through other parts. That is a normal series loop.

The distinction matters. In this series circuit, `R1` is not a short:

```text
R+3 -> J1 -> row 03 right -> R1 -> row 06 right -> D1 -> row 06 left -> J2 -> L-6
```

`R1`'s endpoints are connected through `J1`, the rails, `D1`, and `J2`, but
they are not on the same base net. The validator therefore checks shorts
against the base nets only.

## Answering questions

When the user asks what is connected to a hole or part:

1. Name the base net: row side or rail.
2. List the parts whose leads are on that net.
3. Follow each part to its other net.
4. Stop when the net repeats; do not loop forever.

Example:

```text
row 03 right (F3-J3): J1, R1
row 06 right (F6-J6): R1, D1
row 06 left  (A6-E6): D1, J2
```

So the path is `J1 -> row 03 right -> R1 -> row 06 right -> D1 ->
row 06 left -> J2`.

## Rewiring rules

- Keep one lead per cell.
- If the target net has no free hole at the exact spot, use another free hole
  on the same row/side. For example, `F3`, `G3`, `H3`, `I3`, and `J3` are all
  the same net.
- A part must span two different base nets.
- A jumper between two holes on the same base net does nothing; do not add it
  unless the user explicitly wants a physical bridge for another reason.
- When moving a part, restore its old holes to `.` and write its reference at
  the new holes. Update `Location` in Table 2 to the same two endpoints.
- Do not move a part onto a hole that is already occupied by another reference.

## Quick checks

- Every reference appears exactly twice in Table 1.
- Every reference appears once in Table 2.
- `Location` endpoints match the two Table 1 cells.
- No part has both leads on the same base net.
- Rail rows match the board profile.
- Table 1 keeps every row and its exact width.
