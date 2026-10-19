#!/usr/bin/env python3
"""Tests for breadboard.py. Run with: python -m unittest test_breadboard.py"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import breadboard as bb


HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent / "examples"


def blank_text(board: str) -> str:
    profile = bb.PROFILES[board]
    return bb.blank_table1(profile) + "\n\n" + bb.blank_table2()


def example_text(board: str) -> str:
    return (EXAMPLES / f"{board}-led.md").read_text(encoding="utf-8")


def tables_from(text: str) -> list[list[str]]:
    return bb.extract_tables(text)


def join_tables(tables: list[list[str]]) -> str:
    return "\n\n".join("\n".join(table) for table in tables)


class ProfileTests(unittest.TestCase):
    def test_blank_tables_validate(self) -> None:
        for key in ("170", "400", "830"):
            with self.subTest(board=key):
                report = bb.validate_text(blank_text(key), bb.PROFILES[key])
                self.assertTrue(report.ok, report.errors)

    def test_examples_validate(self) -> None:
        for key in ("170", "400", "830"):
            with self.subTest(board=key):
                report = bb.validate_text(
                    example_text(key), bb.PROFILES[key]
                )
                self.assertTrue(report.ok, report.errors)

    def test_profile_widths(self) -> None:
        self.assertEqual(bb.PROFILES["170"].line_width, 61)
        self.assertEqual(bb.PROFILES["400"].line_width, 81)
        self.assertEqual(bb.PROFILES["830"].line_width, 81)
        self.assertEqual(bb.TABLE2_LINE_WIDTH, 81)


class Table1Tests(unittest.TestCase):
    def test_bad_line_width(self) -> None:
        text = blank_text("830")
        lines = text.splitlines()
        lines[2] = lines[2].replace("| .  |", "| .   |", 1)
        report = bb.validate_text("\n".join(lines), bb.PROFILES["830"])
        self.assertFalse(report.ok)
        self.assertTrue(any("chars; expected 81" in e for e in report.errors))

    def test_missing_row(self) -> None:
        text = blank_text("830")
        lines = text.splitlines()
        del lines[2]
        report = bb.validate_text("\n".join(lines), bb.PROFILES["830"])
        self.assertFalse(report.ok)
        self.assertTrue(any("expected 65" in e for e in report.errors))

    def test_hole_on_closed_rail(self) -> None:
        text = blank_text("830")
        lines = text.splitlines()
        # Row 08 has no rail hole. Its data line is at index 2 + 7.
        line_index = 2 + 7
        cells = bb.split_table_line(lines[line_index])
        # Right + is the second-to-last cell.
        cells[-2] = bb.cell_text(".")
        lines[line_index] = "|" + "|".join(cells) + "|"
        report = bb.validate_text("\n".join(lines), bb.PROFILES["830"])
        self.assertFalse(report.ok)
        self.assertTrue(any("rail has a hole" in e for e in report.errors))

    def test_bad_row_number(self) -> None:
        text = blank_text("400")
        lines = text.splitlines()
        cells = bb.split_table_line(lines[2])
        cells[0] = bb.cell_text("99")
        lines[2] = "|" + "|".join(cells) + "|"
        report = bb.validate_text("\n".join(lines), bb.PROFILES["400"])
        self.assertFalse(report.ok)
        self.assertTrue(any("row number" in e for e in report.errors))


class Table2Tests(unittest.TestCase):
    def test_location_mismatch(self) -> None:
        text = example_text("830").replace("G3:G6", "G3:G7", 1)
        report = bb.validate_text(text, bb.PROFILES["830"])
        self.assertFalse(report.ok)
        self.assertTrue(any("Table 1 but" in e for e in report.errors))

    def test_missing_table2(self) -> None:
        text = bb.blank_table1(bb.PROFILES["830"])
        report = bb.validate_text(text, bb.PROFILES["830"])
        self.assertTrue(report.ok, report.errors)

    def test_missing_component_row(self) -> None:
        text = example_text("830")
        tables = tables_from(text)
        tables[1] = tables[1][:-1]
        report = bb.validate_text(join_tables(tables), bb.PROFILES["830"])
        self.assertFalse(report.ok)
        self.assertTrue(any("missing from Table 2" in e for e in report.errors))

    def test_bad_table2_width(self) -> None:
        text = example_text("830")
        tables = tables_from(text)
        tables[1][2] = tables[1][2].replace("R+3:F3", "R+3:F3 ", 1)
        report = bb.validate_text(join_tables(tables), bb.PROFILES["830"])
        self.assertFalse(report.ok)
        self.assertTrue(any("Table 2 line 3" in e for e in report.errors))


class ConnectivityTests(unittest.TestCase):
    def test_short_is_reported(self) -> None:
        tables = tables_from(example_text("830"))
        table1 = tables[0]
        # Row 06: R1 is at G6. Move it to H3, which is the same row-3
        # right-side net as G3. That shorts R1.
        row06_index = 2 + 5
        row03_index = 2 + 2
        cells06 = bb.split_table_line(table1[row06_index])
        cells03 = bb.split_table_line(table1[row03_index])
        # G is index 10; H is index 11.
        self.assertEqual(cells06[10], " R1 ")
        self.assertEqual(cells03[11], " .  ")
        cells06[10] = " .  "
        cells03[11] = " R1 "
        table1[row06_index] = "|" + "|".join(cells06) + "|"
        table1[row03_index] = "|" + "|".join(cells03) + "|"
        # Table 2: header, separator, J1, R1, D1, J2.
        tables[1][3] = tables[1][3].replace("G3:G6", "G3:H3", 1)
        report = bb.validate_text(join_tables(tables), bb.PROFILES["830"])
        self.assertFalse(report.ok)
        self.assertTrue(any("short" in e for e in report.errors))

    def test_row_buses_are_separate(self) -> None:
        tables = tables_from(example_text("170"))
        # P1 is at A1/A2. Move A2 to A3; P1 then spans two different
        # rows, which is not a short. The header of Table 2 is unchanged.
        table1 = tables[0]
        row01_index = 2 + 0
        row02_index = 2 + 1
        row03_index = 2 + 2
        cells01 = bb.split_table_line(table1[row01_index])
        cells02 = bb.split_table_line(table1[row02_index])
        cells03 = bb.split_table_line(table1[row03_index])
        self.assertEqual(cells01[1], " P1 ")
        self.assertEqual(cells02[1], " P1 ")
        cells02[1] = " .  "
        cells03[1] = " P1 "
        table1[row01_index] = "|" + "|".join(cells01) + "|"
        table1[row02_index] = "|" + "|".join(cells02) + "|"
        table1[row03_index] = "|" + "|".join(cells03) + "|"
        tables[1][2] = tables[1][2].replace("A1:A2", "A1:A3", 1)
        report = bb.validate_text(join_tables(tables), bb.PROFILES["170"])
        self.assertTrue(report.ok, report.errors)


if __name__ == "__main__":
    unittest.main()
