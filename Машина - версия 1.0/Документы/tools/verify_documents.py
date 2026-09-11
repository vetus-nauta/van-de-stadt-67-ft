#!/usr/bin/env python3
"""Verify canonical document bytes and source occurrence references."""
import csv
import hashlib
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    document_count = occurrence_count = duplicate_count = 0
    for register in sorted((root / "documentation/registers").glob("*/documents.csv")):
        with register.open(newline="") as stream:
            documents = list(csv.DictReader(stream, delimiter=";"))
        by_id = {row["document_id"]: row for row in documents}
        assert len(by_id) == len(documents), "Duplicate document IDs"
        assert len({row["sha256"] for row in documents}) == len(documents), "Duplicate canonical files"
        for row in documents:
            data = (root / row["path"]).read_bytes()
            assert len(data) == int(row["bytes"]), row["path"]
            assert hashlib.sha256(data).hexdigest() == row["sha256"], row["path"]
        with (register.parent / "occurrences.csv").open(newline="") as stream:
            occurrences = list(csv.DictReader(stream, delimiter=";"))
        seen = set()
        for row in occurrences:
            doc = by_id[row["document_id"]]
            assert row["sha256"] == doc["sha256"]
            assert row["canonical_path"] == doc["path"]
            expected = "EXACT_DUPLICATE" if row["sha256"] in seen else "CANONICAL"
            assert row["disposition"] == expected
            duplicate_count += expected == "EXACT_DUPLICATE"
            seen.add(row["sha256"])
        assert seen == {row["sha256"] for row in documents}
        document_count += len(documents)
        occurrence_count += len(occurrences)
    assert document_count, "No document registers found"
    print(f"PASS: {document_count} canonical files; {occurrence_count} occurrences; {duplicate_count} exact duplicates")


if __name__ == "__main__":
    main()
