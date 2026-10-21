<img width="1376" height="768" alt="Gemini_Generated_Image_546m3g546m3g546m" src="https://github.com/user-attachments/assets/78d866cf-8bf9-4487-9cf0-7f342ad9a101" />

The following is a small hacky way to communicate breadboard wiring with LLMs.
For serious work that is beyond the breadboard, see [netlist](https://en.wikipedia.org/wiki/Netlist) as it's the right tool.

## Motivation  

I wanted to communicate my breadboard wiring to the LLMs, and this is my current approach:

## Breadboard:

<details>

  <summary>
  Copy 17 rows
  </summary>

  ```
| #  | A  | B  | C  | D  | E  |----| F  | G  | H  | I  | J  |
|----|----|----|----|----|----|----|----|----|----|----|----|
| 01 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 02 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 03 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 04 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 05 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 06 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 07 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 08 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 09 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 10 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 11 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 12 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 13 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 14 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 15 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 16 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
| 17 | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |
  ```
</details>

<details>

  <summary>
  Copy 30 rows
  </summary>

  ```
| #  | +  | -  | A  | B  | C  | D  | E  |----| F  | G  | H  | I  | J  | +  | -  |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| 01 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 02 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 03 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 04 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 05 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 06 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 07 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 08 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 09 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 10 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 11 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 12 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 13 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 14 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 15 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 16 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 17 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 18 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 19 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 20 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 21 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 22 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 23 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 24 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 25 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 26 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 27 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 28 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 29 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 30 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
  ```
</details>

<details>
  <summary>
    Copy the 63 row
  </summary>

```
| #  | +  | -  | A  | B  | C  | D  | E  |----| F  | G  | H  | I  | J  | +  | -  |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| 01 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 02 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 03 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 04 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 05 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 06 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 07 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 08 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 09 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 10 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 11 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 12 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 13 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 14 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 15 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 16 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 17 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 18 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 19 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 20 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 21 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 22 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 23 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 24 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 25 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 26 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 27 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 28 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 29 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 30 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 31 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 32 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 33 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 34 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 35 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 36 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 37 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 38 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 39 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 40 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 41 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 42 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 43 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 44 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 45 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 46 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 47 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 48 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 49 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 50 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 51 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 52 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 53 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 54 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 55 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 56 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 57 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 58 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 59 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 60 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 61 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 62 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 63 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
```
</details>

<details>

<summary>
Components & wiring  
</summary>

```
| Location | Ref | Components | Value   | Reading | Note                        |
| -------- | --- | ---------- | ------- | ------- | --------------------------- |
|          |     |            |         |         |                             |
|          |     |            |         |         |                             |
|          |     |            |         |         |                             |
```
</details>

## Usage example (first 9 rows shown):

| #  | +  | -  | A  | B  | C  | D  | E  |----| F  | G  | H  | I  | J  | +  | -  |
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|
| 01 |    |    | .  | .  | .  | .  | .  |----| R1 | R2 | J1 | J2 |    |    |    |
| 02 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  |    |    |    |
| 03 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 04 | .  | .  | .  | .  | .  | .  | .  |----| R1 | .  | .  | .  | .  | .  | .  |
| 05 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  | .  | .  |
| 06 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | J1 | .  | .  | .  | .  |
| 07 | .  | .  | .  | .  | .  | .  | .  |----| .  | R2 | .  | .  | J3 | .  | .  |
| 08 |    |    | .  | .  | .  | .  | .  |----| .  | .  | .  | .  | .  |    |    |
| 09 | .  | .  | .  | .  | .  | .  | .  |----| .  | .  | .  | J2 | J3 | .  | .  |

Components & Wiring:

| Location | Ref | Components | Value   | Reading | Note                        |
| -------- | --- | ---------- | ------- | ------- | --------------------------- |
| G1:G4    | R1  | resistor   | 2.2kohm |         |                             |
| H4:H7    | R2  | resistor   | 2.2kohm |         |                             |
| I1:I6    | J1  | jumper     | Red     |         |                             |
| J1:J9    | J2  | jumper     | White   |         |                             |
| B7:B9    | J3  | jumper     | Red     |         |                             |

It's basically a 2 table system, 
The first table might look redundant, but it actually was very useful to me as it "shows" me visually what goes where.  
adding one small trick to the first table made it so much easier to follow while wiring, by using `│` in [zed.dev](https://zed.dev/) editor,  

It looked like this:

<img width="967" height="356" alt="image" src="https://github.com/user-attachments/assets/0c94153b-4ffe-41ea-b7aa-65c1eeeba570" />


The wiring looks distinct enough that i could follow and debug the wiring easily.

To make the LLM understand it and be able to reply to you with some rewiring suggestions, you may want to use the following prompt:

```
You are my breadboard wiring assistant. 
I will paste two tables: 
1. a fixed-width breadboard map and 
2. a component list. 

Read the map as a physical breadboard, answer my questions about it, 
and when you propose a rewiring, 
return both tables updated in **exactly the same format**.

Read Table 1 as a breadboard; Table 2 lists parts. 
- A-E in a row are one net, 
- F-J another; center splits them; 
- each +/- rail is one continuous net per side, left/right separate; 
- blank rail cell = missing hole, not a break. 
- One lead per cell. 
- Answer or rewire, then return both full tables **in the same format**. 

Table 1: 
- every line is 5*columns+1 chars; 
- ordinary cell is 4 chars between pipes: 
  - empty hole `| .  |`, 
  - no hole `|    |`, 
  - ref `| R1 |`, 
  - center `|----|`; 
  - keep row count and all rows, never "...". 

Table 2: 
- Keep columns, widths, and Location spans. 
- Put each table in a fenced text block; 
- no reflow, tabs, or prose inside the blocks; 
- flag inconsistencies instead of fixing them.
```

Otherwise you'd be getting badly formatted table that looks fine in the preview but not in the editor, 
you'd be spending time correcting the formatting, so the prompt is trying to save you time.

## OpenCode skill

The prompt is also packaged as an OpenCode skill in [`breadboard-wiring/`](./breadboard-wiring/).
It adds board profiles for the 170, 400, and 830 point boards, blank templates,
complete LED examples, and a generator/validator:

```sh
python breadboard-wiring/scripts/breadboard.py new --board 830
python breadboard-wiring/scripts/breadboard.py validate --board 830 my-table.md
```

The validator checks the row count, 4-character cells, 81-character lines,
rail pattern, reference pairing, `Location` spans, and shorts. See the
[skill README](./breadboard-wiring/README.md) for installation and use.
