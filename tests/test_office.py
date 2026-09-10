import csv
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

SPEC = importlib.util.spec_from_file_location("office", Path(__file__).resolve().parents[1] / "tools" / "office.py")
office = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(office)


class OfficeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def row(self, **values):
        row = dict(zip(office.HEADER, ["L-1", "W-1", "S-1", "Учебный материал", "MATERIAL", "2", "шт", "10.00", "EUR", "NET", "SRC-1", "CONFIRMED", "", ""]))
        row.update(values)
        return row

    def csv(self, rows, name="input.csv"):
        path = self.root / name
        with path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=office.HEADER, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_decimal_rounds_each_line_then_sums(self):
        path = self.csv([self.row(quantity="1", unit_price="1.005"), self.row(line_id="L-2", quantity="1", unit_price="1.005")])
        result = office.cost(path, "EUR", "NET")
        self.assertEqual(result["total"], "2.02")
        self.assertEqual(result["status"], "CALCULATION_ONLY_NOT_APPROVAL")
        self.assertEqual(len(result["input_sha256"]), 64)

    def test_empty_and_missing_values_do_not_become_zero(self):
        for rows in ([], [self.row(quantity="")], [self.row(unit_price="")], [self.row(unit=" ")]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                office.cost(self.csv(rows), "EUR", "NET")

    def test_nan_infinity_negative_and_comma_rejected(self):
        for value in ("NaN", "Infinity", "-1", "1,20", "1e3"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                office.cost(self.csv([self.row(unit_price=value)]), "EUR", "NET")

    def test_duplicate_currency_basis_status_and_assumption_checks(self):
        bad = [[self.row(), self.row()], [self.row(currency="USD")], [self.row(price_basis="GROSS")],
               [self.row(status="DRAFT")], [self.row(status="APPROVED_ASSUMPTION", assumption_id=" ")]]
        for rows in bad:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                office.cost(self.csv(rows), "EUR", "NET")
        result = office.cost(self.csv([self.row(status="APPROVED_ASSUMPTION", assumption_id="A-1")]), "EUR", "NET")
        self.assertEqual(result["lines"][0]["assumption_id"], "A-1")

    def test_quantity_and_price_effects_and_rounding_reconcile(self):
        old = self.csv([self.row(quantity="1", unit_price="0.005")], "old.csv")
        new = self.csv([self.row(quantity="2", unit_price="0.01")], "new.csv")
        result = office.compare(old, new, "EUR", "NET")
        change = result["changed"][0]
        self.assertEqual(change["quantity_effect"], "0.01")
        self.assertEqual(change["price_effect"], "0.01")
        self.assertEqual(change["rounding_residual"], "-0.01")
        self.assertEqual(result["delta"], "0.01")

    def test_unit_change_cannot_be_treated_as_quantity_effect(self):
        old = self.csv([self.row()], "old.csv")
        new = self.csv([self.row(unit="компл")], "new.csv")
        change = office.compare(old, new, "EUR", "NET")["changed"][0]
        self.assertTrue(change["requires_review"])
        self.assertNotIn("quantity_effect", change)
        self.assertEqual(change["technical_equivalence"], "NOT_ASSESSED")

    def test_add_remove_and_stable_id_changes_delta(self):
        old = self.csv([self.row(), self.row(line_id="REMOVE", quantity="1", unit_price="5")], "old.csv")
        new = self.csv([self.row(quantity="3"), self.row(line_id="ADD", quantity="1", unit_price="7")], "new.csv")
        result = office.compare(old, new, "EUR", "NET")
        self.assertEqual(result["delta"], "12.00")
        self.assertEqual(result["added"][0]["line_id"], "ADD")
        self.assertEqual(result["removed"][0]["line_id"], "REMOVE")
        self.assertEqual(result["changed"][0]["line_id"], "L-1")

    def test_compare_validates_both_inputs(self):
        old = self.csv([self.row()], "old.csv")
        new = self.csv([self.row(currency="USD")], "new.csv")
        with self.assertRaises(ValueError):
            office.compare(old, new, "EUR", "NET")

    def test_invalid_cli_input_creates_no_output(self):
        path = self.csv([self.row(status="DRAFT")])
        out = self.root / "result.json"
        with redirect_stderr(io.StringIO()):
            self.assertEqual(office.main(["cost", str(path), "--currency", "EUR", "--price-basis", "NET", "--out", str(out)]), 2)
        self.assertFalse(out.exists())

    def test_manifest_exclusions_bytes_hash_and_no_overwrite(self):
        import hashlib
        (self.root / "document.txt").write_bytes(b"test")
        for directory in (".git", ".local", "__pycache__"):
            (self.root / directory).mkdir()
            (self.root / directory / "secret").write_text("excluded")
        out = self.root / "manifest.json"
        document = office.manifest(self.root, out)
        self.assertEqual(document["files"], [{"path": "document.txt", "sha256": hashlib.sha256(b"test").hexdigest(), "bytes": 4}])
        office.write_new(out, document)
        original = out.read_bytes()
        with self.assertRaises(FileExistsError):
            office.manifest(self.root, out)
        with self.assertRaises(FileExistsError):
            office.write_new(out, {})
        self.assertEqual(out.read_bytes(), original)

    def test_cost_refuses_existing_output(self):
        path = self.csv([self.row()])
        out = self.root / "result.json"
        out.write_text("previous release")
        with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
            result = office.main(["cost", str(path), "--currency", "EUR", "--price-basis", "NET", "--out", str(out)])
        self.assertEqual(result, 2)
        self.assertEqual(out.read_text(), "previous release")


if __name__ == "__main__":
    unittest.main()
