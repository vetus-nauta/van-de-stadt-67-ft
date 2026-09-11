#!/usr/bin/env python3
"""Local arithmetic, change comparison and release checksums; no approval implied."""
import argparse
import csv
import hashlib
import io
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path
import re
import sys

HEADER = "line_id;wbs_id;spec_ids;description;cost_type;quantity;unit;unit_price;currency;price_basis;source_id;status;assumption_id;notes".split(";")
NOTICE = "CALCULATION_ONLY_NOT_APPROVAL"
CENT = Decimal("0.01")


def read_estimate(path, currency, price_basis):
    if not currency or currency != currency.strip():
        raise ValueError("Specify a nonempty currency without surrounding spaces")
    if price_basis not in {"NET", "GROSS"}:
        raise ValueError("price_basis must be NET or GROSS")
    raw = Path(path).read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), delimiter=";", strict=True)
    if reader.fieldnames != HEADER:
        raise ValueError(f"{path}: expected exact header: {';'.join(HEADER)}")
    records = []
    seen = set()
    for row in reader:
        number = reader.line_num
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"{path}:{number}: malformed column count")
        for key in ("line_id", "wbs_id", "description", "cost_type", "quantity", "unit", "unit_price", "currency", "price_basis", "source_id", "status"):
            if not row[key].strip():
                raise ValueError(f"{path}:{number}: missing {key}")
        if row["line_id"] != row["line_id"].strip():
            raise ValueError(f"{path}:{number}: line_id contains surrounding spaces")
        if row["line_id"] in seen:
            raise ValueError(f"{path}:{number}: duplicate line_id {row['line_id']}")
        seen.add(row["line_id"])
        if row["currency"] != currency or row["price_basis"] != price_basis:
            raise ValueError(f"{path}:{number}: currency/price_basis does not match requested basis")
        if row["status"] not in {"CONFIRMED", "APPROVED_ASSUMPTION"}:
            raise ValueError(f"{path}:{number}: unresolved status {row['status']}")
        if row["status"] == "APPROVED_ASSUMPTION" and not row["assumption_id"].strip():
            raise ValueError(f"{path}:{number}: approved assumption requires assumption_id")
        for key in ("quantity", "unit_price"):
            value = row[key]
            try:
                decimal = Decimal(value)
            except InvalidOperation:
                raise ValueError(f"{path}:{number}: invalid {key}") from None
            if not decimal.is_finite() or decimal < 0 or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
                raise ValueError(f"{path}:{number}: {key} must be a finite nonnegative decimal with a dot, without exponent")
        records.append(row)
    if not records:
        raise ValueError(f"{path}: no estimate lines; empty input is not a zero budget")
    return records, hashlib.sha256(raw).hexdigest()


def precision(*record_sets):
    return 30 + sum(len(row[key]) for rows in record_sets for row in rows for key in ("quantity", "unit_price"))


def money(value):
    return format(value.quantize(CENT, rounding=ROUND_HALF_UP), ".2f")


def line_total(row):
    return (Decimal(row["quantity"]) * Decimal(row["unit_price"])).quantize(CENT, rounding=ROUND_HALF_UP)


def cost(path, currency, price_basis):
    rows, digest = read_estimate(path, currency, price_basis)
    with localcontext() as context:
        context.prec = precision(rows)
        lines = [{**row, "line_total": money(line_total(row))} for row in rows]
        total = sum((line_total(row) for row in rows), Decimal(0))
        return {"status": NOTICE, "currency": currency, "price_basis": price_basis,
                "rounding": "HALF_UP_0.01_PER_LINE_THEN_SUM", "input_sha256": digest,
                "line_count": len(rows), "total": money(total), "lines": lines}


def compare(old_path, new_path, currency, price_basis):
    old_rows, old_sha = read_estimate(old_path, currency, price_basis)
    new_rows, new_sha = read_estimate(new_path, currency, price_basis)
    old = {row["line_id"]: row for row in old_rows}
    new = {row["line_id"]: row for row in new_rows}
    with localcontext() as context:
        context.prec = precision(old_rows, new_rows)
        added = [{**new[key], "line_total": money(line_total(new[key]))} for key in new if key not in old]
        removed = [{**old[key], "line_total": money(line_total(old[key]))} for key in old if key not in new]
        changed = []
        unchanged = 0
        for key in old:
            if key not in new:
                continue
            before, after = old[key], new[key]
            fields = {field: {"old": before[field], "new": after[field]} for field in HEADER if before[field] != after[field]}
            if not fields:
                unchanged += 1
                continue
            old_total, new_total = line_total(before), line_total(after)
            item = {"line_id": key, "fields": fields, "old_total": money(old_total),
                    "new_total": money(new_total), "delta": money(new_total - old_total),
                    "requires_review": True, "technical_equivalence": "NOT_ASSESSED"}
            if before["unit"] != after["unit"]:
                item["effect_status"] = "UNIT_CHANGED_NO_QUANTITY_PRICE_DECOMPOSITION"
            else:
                q0, q1 = Decimal(before["quantity"]), Decimal(after["quantity"])
                p0, p1 = Decimal(before["unit_price"]), Decimal(after["unit_price"])
                quantity_effect = (q1 - q0) * p0
                price_effect = q1 * (p1 - p0)
                item.update(quantity_effect=money(quantity_effect), price_effect=money(price_effect),
                            rounding_residual=money(new_total - old_total - Decimal(money(quantity_effect)) - Decimal(money(price_effect))),
                            effect_status="ARITHMETIC_ONLY_SAME_UNIT")
            changed.append(item)
        old_total = sum((line_total(row) for row in old_rows), Decimal(0))
        new_total = sum((line_total(row) for row in new_rows), Decimal(0))
        return {"status": NOTICE, "technical_equivalence": "NOT_ASSESSED", "currency": currency,
                "price_basis": price_basis, "rounding": "HALF_UP_0.01_PER_LINE_THEN_SUM",
                "old_input_sha256": old_sha, "new_input_sha256": new_sha,
                "old_total": money(old_total), "new_total": money(new_total), "delta": money(new_total - old_total),
                "added": added, "removed": removed, "changed": changed, "unchanged_count": unchanged}


def manifest(root, output):
    root = Path(root).resolve()
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite: {output}")
    if not root.is_dir():
        raise ValueError("manifest root must be a directory")
    files = []
    excluded = {".git", ".local", "__pycache__"}
    # Walk explicitly so excluded directories and symlink directories are never traversed.
    def walk(directory):
        for path in sorted(directory.iterdir(), key=lambda item: item.name):
            if path.name in excluded or path.absolute() == output:
                continue
            if path.is_symlink():
                raise ValueError(f"Manifest requires regular files/directories, found symlink: {path}")
            if path.is_dir():
                walk(path)
            elif path.is_file():
                data = path.read_bytes()
                files.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
            else:
                raise ValueError(f"Unsupported file type: {path}")
    walk(root)
    return {"status": "CHECKSUMS_ONLY_NOT_APPROVAL", "algorithm": "SHA256", "excluded_directories": sorted(excluded), "files": files}


def write_new(path, document):
    payload = json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("cost", "compare"):
        command = commands.add_parser(name)
        if name == "cost":
            command.add_argument("input")
        else:
            command.add_argument("old")
            command.add_argument("new")
        command.add_argument("--currency", required=True)
        command.add_argument("--price-basis", choices=("NET", "GROSS"), required=True)
        command.add_argument("--out", required=True)
    command = commands.add_parser("manifest")
    command.add_argument("--root", required=True)
    command.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        output = Path(args.out)
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Refusing to overwrite: {output}")
        if args.command == "cost":
            result = cost(args.input, args.currency, args.price_basis)
        elif args.command == "compare":
            result = compare(args.old, args.new, args.currency, args.price_basis)
        else:
            result = manifest(args.root, output)
        write_new(output, result)
    except (OSError, ValueError, csv.Error, InvalidOperation) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(str(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
