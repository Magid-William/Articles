#!/usr/bin/env python3
"""Generate and validate fixed-width breadboard maps.

The canonical format is documented in references/format-contract.md.
Python 3.9+; standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------


def _rows_from_ranges(ranges: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    return tuple(
        row
        for start, end in ranges
        for row in range(start, end + 1)
    )


def _mini_header() -> tuple[str, ...]:
    return ("#", "A", "B", "C", "D", "E", "----", "F", "G", "H", "I", "J")


def _rail_header() -> tuple[str, ...]:
    return (
        "#", "+", "-",
        "A", "B", "C", "D", "E", "----", "F", "G", "H", "I", "J",
        "+", "-",
    )


@dataclass(frozen=True)
class Profile:
    key: str
    name: str
    rows: int
    has_rails: bool
    rail_rows: tuple[int, ...]
    header: tuple[str, ...]

    @property
    def rail_set(self) -> set[int]:
        return set(self.rail_rows)

    @property
    def center_index(self) -> int:
        return self.header.index("----")

    @property
    def line_width(self) -> int:
        return 5 * len(self.header) + 1


PROFILES: dict[str, Profile] = {
    "170": Profile(
        key="170",
        name="170-point mini",
        rows=17,
        has_rails=False,
        rail_rows=(),
        header=_mini_header(),
    ),
    "400": Profile(
        key="400",
        name="400-point half-size",
        rows=30,
        has_rails=True,
        rail_rows=_rows_from_ranges(
            ((1, 5), (7, 11), (13, 17), (19, 23), (25, 29))
        ),
        header=_rail_header(),
    ),
    "830": Profile(
        key="830",
        name="830-point full-size",
        rows=63,
        has_rails=True,
        rail_rows=_rows_from_ranges(
            (
                (3, 7), (9, 13), (15, 19), (21, 25), (27, 31),
                (33, 37), (39, 43), (45, 49), (51, 55), (57, 61),
            )
        ),
        header=_rail_header(),
    ),
}


# ---------------------------------------------------------------------------
# Table formatting
# ---------------------------------------------------------------------------

TABLE2_HEADER = ("Location", "Ref", "Components", "Value", "Reading", "Note")
TABLE2_WIDTHS = (8, 3, 10, 7, 7, 27)
# Each raw cell also has one padding space on each side, and the line has
# one pipe per cell plus the two outer pipes.
TABLE2_LINE_WIDTH = sum(TABLE2_WIDTHS) + 2 * len(TABLE2_WIDTHS) + 7  # 81

REF_RE = re.compile(r"^[A-Z][A-Z0-9]?$")
TERMINAL_RE = re.compile(r"^([A-J])(\d{1,2})$")
RAIL_RE = re.compile(r"^([LR])([+-])(\d{1,2})$")
LOCATION_RE = re.compile(
    r"^([A-J]\d{1,2}|[LR][+-]\d{1,2})\s*:\s*"
    r"([A-J]\d{1,2}|[LR][+-]\d{1,2})$"
)


def cell_text(value: str) -> str:
    """Return one 4-character cell, including its padding."""
    if value == "----":
        return "----"
    if len(value) > 2:
        raise ValueError(f"cell value is too long: {value!r}")
    return " " + value.ljust(2) + " "


def render_line(values: Sequence[str]) -> str:
    return "|" + "|".join(cell_text(value) for value in values) + "|"


def render_table2_row(values: Sequence[object]) -> str:
    if len(values) != len(TABLE2_WIDTHS):
        raise ValueError("Table 2 rows must have exactly 6 values")
    cells: list[str] = []
    for value, width in zip(values, TABLE2_WIDTHS):
        text = str(value)
        if len(text) > width:
            raise ValueError(
                f"Table 2 value {text!r} does not fit in {width} characters"
            )
        cells.append(text.ljust(width))
    return "| " + " | ".join(cells) + " |"


def blank_table1(profile: Profile) -> str:
    lines = [
        render_line(profile.header),
        render_line(["----"] * len(profile.header)),
    ]
    rails = profile.rail_set
    for row in range(1, profile.rows + 1):
        values = [f"{row:02d}"]
        if profile.has_rails:
            rail = "." if row in rails else ""
            values.extend((rail, rail))
        values.extend((".", ".", ".", ".", "."))
        values.append("----")
        values.extend((".", ".", ".", ".", "."))
        if profile.has_rails:
            rail = "." if row in rails else ""
            values.extend((rail, rail))
        lines.append(render_line(values))
    return "\n".join(lines)


def blank_table2() -> str:
    separator = ["-" * width for width in TABLE2_WIDTHS]
    return "\n".join(
        (render_table2_row(TABLE2_HEADER), render_table2_row(separator))
    )


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def split_table_line(line: str) -> list[str]:
    text = line.strip()
    if not (text.startswith("|") and text.endswith("|")):
        raise ValueError("not a table line")
    return text[1:-1].split("|")


def extract_tables(text: str) -> list[list[str]]:
    """Return contiguous groups of Markdown table lines."""
    tables: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            current.append(line)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def normalize_coord(coord: str) -> str | None:
    coord = coord.strip().upper().replace(" ", "")
    match = TERMINAL_RE.fullmatch(coord)
    if match:
        return f"{match.group(1)}{int(match.group(2))}"
    match = RAIL_RE.fullmatch(coord)
    if match:
        return f"{match.group(1)}{match.group(2)}{int(match.group(3))}"
    return None


def parse_location(location: str) -> tuple[str, str] | None:
    match = LOCATION_RE.fullmatch(location.strip().upper().replace(" ", ""))
    if not match:
        return None
    left = normalize_coord(match.group(1))
    right = normalize_coord(match.group(2))
    if left is None or right is None:
        return None
    return left, right


def coord_exists(profile: Profile, coord: str) -> bool:
    match = TERMINAL_RE.fullmatch(coord)
    if match:
        return 1 <= int(match.group(2)) <= profile.rows
    match = RAIL_RE.fullmatch(coord)
    if match:
        if not profile.has_rails:
            return False
        return int(match.group(3)) in profile.rail_set
    return False


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass
class Report:
    profile: Profile
    errors: list[str]
    warnings: list[str]
    refs: dict[str, tuple[str, str]]
    components: dict[str, str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _coord_at(profile: Profile, row: int, column_index: int) -> str:
    label = profile.header[column_index]
    if label in "ABCDEFGHIJ":
        return f"{label}{row}"
    if label in ("+", "-"):
        side = "L" if column_index < profile.center_index else "R"
        return f"{side}{label}{row}"
    raise ValueError(f"no coordinate for column {label!r}")


def _validate_table1(
    lines: Sequence[str], profile: Profile
) -> tuple[list[str], list[str], dict[str, list[str]]]:
    errors: list[str] = []
    warnings: list[str] = []
    ref_positions: dict[str, list[str]] = {}

    expected_lines = profile.rows + 2
    if len(lines) != expected_lines:
        errors.append(
            f"Table 1 has {len(lines)} lines; expected {expected_lines} "
            f"(header + separator + {profile.rows} data rows)"
        )
    if len(lines) < 2:
        return errors, warnings, ref_positions

    try:
        header = tuple(cell.strip() for cell in split_table_line(lines[0]))
    except ValueError:
        errors.append("Table 1 header is not a valid table line")
        return errors, warnings, ref_positions

    if header != profile.header:
        errors.append(
            "Table 1 header does not match the "
            f"{profile.name} profile: {profile.header}"
        )

    try:
        separator = [cell.strip() for cell in split_table_line(lines[1])]
    except ValueError:
        errors.append("Table 1 separator is not a valid table line")
        separator = []
    if separator and any(cell != "----" for cell in separator):
        errors.append("Table 1 separator must be |----| repeated for every column")

    for line_number, line in enumerate(lines[2:], start=3):
        row = line_number - 2
        if "\t" in line:
            errors.append(f"Table 1 line {line_number} contains a tab")
        if line != line.rstrip():
            errors.append(f"Table 1 line {line_number} has trailing whitespace")
        if any(ord(character) > 127 for character in line):
            errors.append(f"Table 1 line {line_number} contains non-ASCII text")
        stripped = line.strip()
        if len(stripped) != profile.line_width:
            errors.append(
                f"Table 1 line {line_number} is {len(stripped)} chars; "
                f"expected {profile.line_width}"
            )
        try:
            cells = split_table_line(line)
        except ValueError:
            errors.append(f"Table 1 line {line_number} is not a valid table line")
            continue
        if len(cells) != len(profile.header):
            errors.append(
                f"Table 1 line {line_number} has {len(cells)} cells; "
                f"expected {len(profile.header)}"
            )
            continue
        for cell_index, cell in enumerate(cells):
            if len(cell) != 4:
                errors.append(
                    f"Table 1 line {line_number}, column {cell_index + 1} "
                    f"is {len(cell)} chars; expected 4"
                )
        row_number = cells[0].strip()
        expected_number = f"{row:02d}"
        if row_number != expected_number:
            errors.append(
                f"Table 1 line {line_number} has row number "
                f"{row_number!r}; expected {expected_number!r}"
            )

        center_index = profile.center_index
        for cell_index, raw in enumerate(cells):
            if cell_index == 0:
                # The first cell is the row number, not a breadboard hole.
                continue
            value = raw.strip()
            if cell_index == center_index:
                if raw != "----":
                    errors.append(
                        f"Table 1 line {line_number}: center cell must be "
                        "'|----|'"
                    )
                continue
            if raw == "----":
                errors.append(
                    f"Table 1 line {line_number}, column {cell_index + 1}: "
                    "unexpected center cell"
                )
                continue

            label = profile.header[cell_index]
            is_rail = label in ("+", "-") and profile.has_rails
            if is_rail:
                if row not in profile.rail_set:
                    if value != "":
                        errors.append(
                            f"Table 1 line {line_number}: rail has a hole at "
                            f"row {row:02d}, but this profile has no rail there"
                        )
                    continue
                if value == "":
                    errors.append(
                        f"Table 1 line {line_number}: rail hole is blank at "
                        f"row {row:02d}"
                    )
                    continue
            else:
                if value == "":
                    errors.append(
                        f"Table 1 line {line_number}: terminal hole is blank "
                        f"at {_coord_at(profile, row, cell_index)}"
                    )
                    continue

            if value == ".":
                continue
            if not REF_RE.fullmatch(value):
                errors.append(
                    f"Table 1 line {line_number}, column {cell_index + 1}: "
                    f"invalid reference {value!r} (use 1-2 chars, e.g. R1)"
                )
                continue
            coord = _coord_at(profile, row, cell_index)
            ref_positions.setdefault(value, []).append(coord)

    for ref, coords in sorted(ref_positions.items()):
        if len(coords) != 2:
            errors.append(
                f"{ref} appears {len(coords)} times in Table 1; "
                "a 2-pin part must appear exactly twice"
            )

    return errors, warnings, ref_positions


def _validate_table2(
    lines: Sequence[str] | None,
    profile: Profile,
    ref_positions: dict[str, list[str]],
) -> tuple[list[str], list[str], dict[str, str]]:
    errors: list[str] = []
    warnings: list[str] = []
    components: dict[str, str] = {}

    if lines is None:
        if ref_positions:
            errors.append("Table 2 is missing while Table 1 contains parts")
        return errors, warnings, components
    if len(lines) < 2:
        errors.append("Table 2 must have a header and separator row")
        return errors, warnings, components

    try:
        header = tuple(cell.strip() for cell in split_table_line(lines[0]))
    except ValueError:
        errors.append("Table 2 header is not a valid table line")
        return errors, warnings, components
    if header != TABLE2_HEADER:
        errors.append(f"Table 2 header must be: {TABLE2_HEADER}")

    for line_number, line in enumerate(lines, start=1):
        if "\t" in line:
            errors.append(f"Table 2 line {line_number} contains a tab")
        if line != line.rstrip():
            errors.append(f"Table 2 line {line_number} has trailing whitespace")
        stripped = line.strip()
        if len(stripped) != TABLE2_LINE_WIDTH:
            errors.append(
                f"Table 2 line {line_number} is {len(stripped)} chars; "
                f"expected {TABLE2_LINE_WIDTH}"
            )
        try:
            cells = split_table_line(line)
        except ValueError:
            errors.append(f"Table 2 line {line_number} is not a valid table line")
            continue
        if len(cells) != len(TABLE2_WIDTHS):
            errors.append(
                f"Table 2 line {line_number} has {len(cells)} cells; "
                f"expected {len(TABLE2_WIDTHS)}"
            )
            continue
        for cell_index, (cell, width) in enumerate(zip(cells, TABLE2_WIDTHS)):
            if len(cell) != width + 2:
                errors.append(
                    f"Table 2 line {line_number}, column {cell_index + 1} "
                    f"is {len(cell)} chars; expected {width + 2}"
                )

    if len(lines) >= 2:
        try:
            separator = [cell.strip() for cell in split_table_line(lines[1])]
        except ValueError:
            separator = []
        expected_separator = ["-" * width for width in TABLE2_WIDTHS]
        if separator and separator != expected_separator:
            errors.append("Table 2 separator does not match its column widths")

    seen_refs: set[str] = set()
    for line_number, line in enumerate(lines[2:], start=3):
        try:
            cells = [cell.strip() for cell in split_table_line(line)]
        except ValueError:
            errors.append(f"Table 2 line {line_number} is not a valid table line")
            continue
        if len(cells) != len(TABLE2_WIDTHS):
            continue
        if all(cell == "" for cell in cells):
            continue
        location, ref, component, value, reading, note = cells
        if not ref:
            errors.append(f"Table 2 line {line_number}: empty Ref")
            continue
        if not REF_RE.fullmatch(ref):
            errors.append(
                f"Table 2 line {line_number}: invalid Ref {ref!r}"
            )
            continue
        if ref in seen_refs:
            errors.append(f"Table 2 line {line_number}: duplicate Ref {ref!r}")
            continue
        seen_refs.add(ref)
        components[ref] = component

        if ref not in ref_positions:
            errors.append(
                f"Table 2 line {line_number}: {ref} does not appear in Table 1"
            )
            continue
        parsed = parse_location(location)
        if parsed is None:
            errors.append(
                f"Table 2 line {line_number}: invalid Location {location!r}; "
                "use e.g. G1:G4 or R+3:F3"
            )
            continue
        for coord in parsed:
            if not coord_exists(profile, coord):
                errors.append(
                    f"Table 2 line {line_number}: {coord} is not a hole on "
                    f"the {profile.name} profile"
                )
        expected = ref_positions[ref]
        if len(expected) == 2 and set(parsed) != set(expected):
            errors.append(
                f"Table 2 line {line_number}: {ref} is at {tuple(expected)} "
                f"in Table 1 but {parsed} in Table 2"
            )

    for ref in sorted(ref_positions):
        if ref not in seen_refs:
            errors.append(f"{ref} is in Table 1 but missing from Table 2")

    return errors, warnings, components


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, item: str) -> None:
        self.parent.setdefault(item, item)

    def find(self, item: str) -> str:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, a: str, b: str) -> None:
        self.add(a)
        self.add(b)
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a != root_b:
            self.parent[root_b] = root_a


def _check_connectivity(
    profile: Profile,
    ref_positions: dict[str, list[str]],
    components: dict[str, str],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    uf = _UnionFind()

    # Add every hole that exists on this profile.
    for row in range(1, profile.rows + 1):
        for column in "ABCDEFGHIJ":
            uf.add(f"{column}{row}")
    if profile.has_rails:
        for row in profile.rail_rows:
            for side in ("L+", "L-", "R+", "R-"):
                uf.add(f"{side}{row}")

    # Row buses: A-E and F-J are separate nets.
    for row in range(1, profile.rows + 1):
        for first, second in zip("ABCD", "BCDE"):
            uf.union(f"{first}{row}", f"{second}{row}")
        for first, second in zip("FGHI", "GHIJ"):
            uf.union(f"{first}{row}", f"{second}{row}")

    # Each rail is one continuous bus along its side.
    if profile.has_rails:
        for side in ("L+", "L-", "R+", "R-"):
            coords = [f"{side}{row}" for row in profile.rail_rows]
            for coord in coords[1:]:
                uf.union(coords[0], coord)

    # A 2-pin part is a short only when both leads are already on the same
    # *base* net (row bus or rail). Do not union parts into the base net
    # here: a series circuit legitimately connects a part's endpoints
    # through the other parts.
    for ref, coords in sorted(ref_positions.items()):
        if len(coords) != 2:
            continue
        first, second = coords
        if not (coord_exists(profile, first) and coord_exists(profile, second)):
            continue
        if uf.find(first) == uf.find(second):
            component = components.get(ref, "").lower()
            if "jumper" in component:
                warnings.append(
                    f"{ref} is a jumper between two holes on the same net "
                    f"({first} and {second}); it is a no-op"
                )
            else:
                errors.append(
                    f"{ref} has both leads on the same net "
                    f"({first} and {second}); this is a short"
                )

    return errors, warnings


def validate_text(text: str, profile: Profile) -> Report:
    tables = extract_tables(text)
    if not tables:
        return Report(
            profile=profile,
            errors=["No Markdown table found"],
            warnings=[],
            refs={},
            components={},
        )

    warnings: list[str] = []
    if len(tables) > 2:
        warnings.append(
            f"Found {len(tables)} tables; only the first two were validated"
        )

    table1_errors, table1_warnings, ref_lists = _validate_table1(
        tables[0], profile
    )
    errors = list(table1_errors)
    warnings.extend(table1_warnings)

    ref_positions = {
        ref: tuple(coords)
        for ref, coords in ref_lists.items()
        if len(coords) == 2
    }
    table2 = tables[1] if len(tables) > 1 else None
    table2_errors, table2_warnings, components = _validate_table2(
        table2, profile, ref_positions
    )
    errors.extend(table2_errors)
    warnings.extend(table2_warnings)

    if not errors and ref_positions:
        connectivity_errors, connectivity_warnings = _check_connectivity(
            profile, ref_positions, components
        )
        errors.extend(connectivity_errors)
        warnings.extend(connectivity_warnings)

    return Report(
        profile=profile,
        errors=errors,
        warnings=warnings,
        refs=ref_positions,
        components=components,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _read_text(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _write_text(text: str, path: str | None) -> None:
    if path is None or path == "-":
        print(text)
    else:
        Path(path).write_text(text + "\n", encoding="utf-8")


def _cmd_new(args: argparse.Namespace) -> int:
    profile = PROFILES[args.board]
    text = "\n\n".join((blank_table1(profile), blank_table2()))
    _write_text(text, args.out)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    profile = PROFILES[args.board]
    report = validate_text(_read_text(args.file), profile)
    if report.errors:
        print(f"FAIL: {profile.name} ({profile.key})")
        for error in report.errors:
            print(f"- {error}")
    else:
        print(
            f"OK: {profile.name} ({profile.key}), {profile.rows} rows, "
            f"{len(profile.header)} columns, {profile.line_width} chars/line"
        )
    if report.warnings:
        print("Warnings:")
        for warning in report.warnings:
            print(f"- {warning}")
    return 0 if report.ok else 1


def _cmd_zed(args: argparse.Namespace) -> int:
    text = _read_text(args.file)
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            lines.append(line.replace("|", "│"))
        else:
            lines.append(line)
    _write_text("\n".join(lines), args.out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="breadboard.py",
        description="Generate and validate fixed-width breadboard tables.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser(
        "new", help="print a blank Table 1 and Table 2"
    )
    new_parser.add_argument("--board", choices=sorted(PROFILES), required=True)
    new_parser.add_argument("--out", help="write to this file instead of stdout")
    new_parser.set_defaults(func=_cmd_new)

    validate_parser = subparsers.add_parser(
        "validate", help="validate a Markdown file or stdin"
    )
    validate_parser.add_argument(
        "--board", choices=sorted(PROFILES), required=True
    )
    validate_parser.add_argument(
        "file", nargs="?", help="Markdown file; omit or use - for stdin"
    )
    validate_parser.set_defaults(func=_cmd_validate)

    zed_parser = subparsers.add_parser(
        "zed", help="print a display-only copy with │ delimiters"
    )
    zed_parser.add_argument("file", nargs="?", help="Markdown file or stdin")
    zed_parser.add_argument("--out", help="write to this file instead of stdout")
    zed_parser.set_defaults(func=_cmd_zed)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
