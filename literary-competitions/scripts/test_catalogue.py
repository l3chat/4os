"""Regression checks for provenance, unknown values and reproducible rendering."""

import copy
import json
from html.parser import HTMLParser
import unittest

from render_catalogue import PROJECT, fee_text, products, render, validate
from render_history import products as history_products


class Disclosures(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.items = []
        self.active = None
        self.in_summary = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "details":
            self.active = {"attrs": dict(attrs), "summary": "", "body": ""}
            self.items.append(self.active)
        elif tag == "summary":
            self.in_summary = True

    def handle_endtag(self, tag):
        if tag == "summary":
            self.in_summary = False
        elif tag == "details":
            self.active = None

    def handle_data(self, text):
        if self.active is not None:
            self.active["summary" if self.in_summary else "body"] += text


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((PROJECT / "research/en/catalogue.json").read_text(encoding="utf-8"))

    def test_duplicate_identifiers_fail(self):
        self.data["competitions"][1]["id"] = self.data["competitions"][0]["id"]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate(self.data)

    def test_unsupported_provenance_fails(self):
        self.data["competitions"][0]["entry_fee"]["source_ids"] = ["missing-source"]
        with self.assertRaisesRegex(ValueError, "provenance"):
            validate(self.data)

    def test_unconfirmed_date_cannot_be_presented_as_confirmed(self):
        item = next(c for c in self.data["competitions"] if c["next_deadline"]["date"] is None)
        item["next_deadline"]["date"] = "2027-01-15"
        with self.assertRaisesRegex(ValueError, "Unconfirmed"):
            validate(self.data)

    def test_previous_round_is_not_a_future_deadline(self):
        self.data["competitions"][0]["next_deadline"]["date"] = "2026-10-04"
        with self.assertRaisesRegex(ValueError, "Past date"):
            validate(self.data)

    def test_free_and_unknown_are_distinct(self):
        text = render(self.data)
        self.assertIn("0 USD", text)
        self.assertIn("не подтверждено", text)
        rattle = next(c for c in self.data["competitions"] if c["id"] == "en-rattle-chapbook-2027")
        self.assertIsNone(rattle["next_deadline"]["date"])

    def test_every_record_keeps_a_stable_anchor(self):
        text = render(self.data)
        for item in self.data["competitions"]:
            self.assertIn(f'id="{item["id"]}"', text)
        self.assertNotIn("{source:", text)

    def test_closed_disclosures_keep_brief_facts_and_full_details(self):
        parsed = Disclosures(render(self.data))
        self.assertEqual(len(parsed.items), len(self.data["competitions"]))
        by_id = {item["attrs"]["id"]: item for item in parsed.items}
        for contest in self.data["competitions"]:
            item = by_id[contest["id"]]
            self.assertNotIn("open", item["attrs"])
            self.assertIn(contest["name"], item["summary"])
            for label in ("Частота:", "Дедлайн:", "Взнос:", "Приз:"):
                self.assertIn(label, item["summary"])
            self.assertIn(contest["eligibility"]["description"], item["body"])

    def test_rendering_does_not_modify_research(self):
        before = copy.deepcopy(self.data)
        text = render(self.data)
        self.assertEqual(before, self.data)
        self.data["competitions"].reverse()
        self.assertEqual(text, render(self.data))

    def test_historical_prize_and_expense_allowance_are_visible(self):
        text = render(self.data)
        self.assertIn("15 000 NZD †", text)
        self.assertIn("3 000 EUR (в т.ч. поездка)", text)

    def test_ukrainian_catalogue_has_separate_outputs_and_disclosures(self):
        data = json.loads((PROJECT / "research/uk/catalogue.json").read_text(encoding="utf-8"))
        generated = products(data)
        self.assertEqual(set(generated), {
            PROJECT / "docs/contests/uk/catalogue.md",
            PROJECT / "docs/data/uk-catalogue.json",
        })
        text = generated[PROJECT / "docs/contests/uk/catalogue.md"]
        self.assertIn("catalogue_language: uk", text)
        self.assertIn("/data/uk-catalogue.json", text)
        parsed = Disclosures(text)
        self.assertEqual(len(parsed.items), len(data["competitions"]))
        for item in parsed.items:
            self.assertNotIn("open", item["attrs"])
            for label in ("Частота:", "Дедлайн:", "Взнос:", "Приз:"):
                self.assertIn(label, item["summary"])

    def test_mixed_catalogue_language_fails(self):
        self.data["submission_language"] = "uk"
        with self.assertRaisesRegex(ValueError, "language mismatch"):
            validate(self.data)

    def test_ukrainian_minimum_fee_and_calendar_basis_remain_visible(self):
        data = json.loads((PROJECT / "research/uk/catalogue.json").read_text(encoding="utf-8"))
        item = next(c for c in data["competitions"] if c["id"] == "uk-smoloskyp-2026")
        self.assertTrue(fee_text(item).startswith("от 300 UAH"))
        by_id = {d["attrs"]["id"]: d for d in Disclosures(render(data)).items}
        self.assertIn("по постоянным правилам", by_id[item["id"]]["summary"])
        item = next(c for c in data["competitions"] if c["id"] == "uk-granoslov-2026")
        self.assertIsNone(item["entry_fee"]["amount"])
        self.assertIn("денежная сумма не указана", by_id[item["id"]]["summary"])
        self.assertNotIn("0 UAH", by_id[item["id"]]["summary"])

    def test_event_history_outputs_are_synchronized(self):
        generated = history_products()
        self.assertEqual(len(generated), 2)
        for path, text in generated.items():
            self.assertEqual(path.read_text(encoding="utf-8"), text)
            self.assertIn("Украинский каталог", text)


if __name__ == "__main__":
    unittest.main()
