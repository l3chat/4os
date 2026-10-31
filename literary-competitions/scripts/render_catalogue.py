#!/usr/bin/env python3
"""Render saved research into Markdown and JSON downloads. Never accesses the network."""

import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
STATUSES = {
    "open": "приём объявлен открытым",
    "opens_later": "приём начнётся позднее",
    "closed": "последний раунд закрыт",
    "postponed": "открытие отложено",
}


def validate(data):
    if data["schema_version"] != 1:
        raise ValueError("Unsupported schema_version")
    date.fromisoformat(data["as_of"])
    sources = data["sources"]
    seen = set()
    for source in sources.values():
        if not source["url"].startswith("https://"):
            raise ValueError("Official source must have an HTTPS URL")
        date.fromisoformat(source["checked_on"])
    for item in data["competitions"]:
        identifier = item["id"]
        if identifier in seen or not re.fullmatch(r"[a-z0-9-]+", identifier):
            raise ValueError(f"Duplicate or invalid ID: {identifier}")
        seen.add(identifier)
        if "en" not in item["submission_languages"]:
            raise ValueError(f"English not supported: {identifier}")
        if item["entry_status_at_check"] not in STATUSES:
            raise ValueError(f"Invalid status: {identifier}")
        date.fromisoformat(item["checked_on"])
        for value in (item["opening_date"], item["last_announced_deadline"], item["next_deadline"]["date"]):
            if value:
                date.fromisoformat(value)
        deadline = item["next_deadline"]
        if deadline["date"] and deadline["date"] < data["as_of"]:
            raise ValueError(f"Past date cannot be the next deadline: {identifier}")
        if deadline["date"] and deadline["verification"] != "confirmed":
            raise ValueError(f"Unconfirmed date must remain null: {identifier}")
        if deadline["local_time"] and not deadline["timezone"]:
            raise ValueError(f"Time without timezone: {identifier}")
        for field in ("recurrence", "next_deadline", "entry_fee", "top_prize", "eligibility"):
            refs = item[field]["source_ids"]
            if not refs or any(ref not in sources for ref in refs):
                raise ValueError(f"Missing provenance for {identifier}.{field}")
        for field, key in (("entry_fee", "amount"), ("top_prize", "cash_amount")):
            money = item[field]
            amount = money[key]
            if amount is not None and (isinstance(amount, bool) or amount < 0 or not money["currency"]):
                raise ValueError(f"Invalid money: {identifier}.{field}")
        if item["eligibility"]["geographic_scope"] not in {"worldwide", "restricted", "not_stated"}:
            raise ValueError(f"Invalid eligibility: {identifier}")
    if data["coverage"]["records"] != len(seen):
        raise ValueError("Coverage count does not match records")


def money(value, key):
    amount = value[key]
    return "не подтверждено" if amount is None else f"{amount:,} {value['currency']}".replace(",", " ")


def deadline_text(item):
    value = item["next_deadline"]
    if not value["date"]:
        return "точная дата не подтверждена"
    result = date.fromisoformat(value["date"]).strftime("%d.%m.%Y")
    if value["local_time"]:
        result += f" · {value['local_time']} ({value['timezone']})"
    else:
        result += " · точное время не установлено"
    return result


def references(value, sources):
    return " ".join(
        f'<a href="{escape(sources[key]["url"], quote=True)}" '
        f'title="{escape(sources[key]["title"], quote=True)}">источник</a>'
        for key in value["source_ids"]
    )


def prize_text(item):
    prize = money(item["top_prize"], "cash_amount")
    if item["top_prize"]["applies_to"] != item["edition"]:
        prize += " †"
    if item["top_prize"].get("cash_includes_expense_allowance"):
        prize += " (в т.ч. поездка)"
    return prize


def render_item(item, sources):
    """Native details keeps the summary visible and works without JavaScript."""
    frequency = item["recurrence"]["description"]
    if item["recurrence"].get("verification") == "inferred_from_editions":
        frequency += " (по истории сезонов)"
    deadline = item["next_deadline"]["date"]
    short_deadline = date.fromisoformat(deadline).strftime("%d.%m.%Y") if deadline else "не подтверждён"
    fee = money(item["entry_fee"], "amount") + " / " + item["entry_fee"]["unit"]
    flags = []
    if item["eligibility"]["geographic_scope"] == "restricted":
        flags.append("ограничение гражданства или проживания")
    if item["entry_status_at_check"] != "open":
        flags.append(STATUSES[item["entry_status_at_check"]])
    subtitle = " · ".join([item["organizer_country"], ", ".join(item["genres"]), *flags])
    lines = [
        '<li class="competition-item">',
        f'<details id="{escape(item["id"], quote=True)}" class="competition">',
        '<summary>',
        f'<span class="competition-title">{escape(item["name"])}</span>',
        f'<span class="competition-subtitle">{escape(subtitle)}</span>',
        '<span class="competition-facts">',
    ]
    for label, value in (("Частота", frequency), ("Дедлайн", short_deadline), ("Взнос", fee), ("Приз", prize_text(item))):
        lines.append(f'<span><strong>{label}:</strong> {escape(value)}</span>')
    lines += [
        '</span>', '<span class="competition-toggle" aria-hidden="true"></span>',
        '</summary>', '<div class="competition-body">', '<dl>',
    ]

    def row(label, text, evidence=None):
        refs = " " + references(evidence, sources) if evidence else ""
        lines.append(f'<dt>{escape(label)}</dt><dd>{escape(text)}{refs}</dd>')

    row("Сезон", item["edition"])
    row("Жанры", ", ".join(item["genres"]))
    row("Организатор", item["organizer"] + "; " + item["organizer_country"])
    row("Проверено", item["checked_on"] + "; на эту дату " + STATUSES[item["entry_status_at_check"]])
    row("Периодичность", frequency, item["recurrence"])
    row("Ближайший дедлайн", deadline_text(item) + ". " + item["next_deadline"]["note"], item["next_deadline"])
    if item["opening_date"]:
        row("Объявленное открытие", item["opening_date"])
    if item["last_announced_deadline"]:
        row("Последний объявленный дедлайн", item["last_announced_deadline"] + "; уже прошёл")
    fee_data, prize = item["entry_fee"], item["top_prize"]
    row("Взнос", fee + ". " + fee_data["note"] + " Применимость: " + fee_data["applies_to"] + ".", fee_data)
    row("Главный приз", prize_text(item) + ". " + prize["note"] + " Применимость: " + prize["applies_to"] + ".", prize)
    row("Кто может участвовать", item["eligibility"]["description"], item["eligibility"])
    row("ID", item["id"])
    lines.append('</dl>')
    if item["notes"]:
        lines += ['<h3>Примечания</h3>', '<ul>']
        lines += [f'<li>{escape(note)}</li>' for note in item["notes"]]
        lines.append('</ul>')
    indexed = any(
        sources[ref]["access_method"] == "indexed_primary_page"
        for field in ("recurrence", "next_deadline", "entry_fee", "top_prize", "eligibility")
        for ref in item[field]["source_ids"]
    )
    if indexed:
        lines.append('<p class="source-note">Часть сведений проверена по индексированному тексту официальных страниц. Перед подачей повторно сверить действующие правила.</p>')
    lines += ['</div>', '</details>', '</li>']
    return "\n".join(lines)


def render(data):
    validate(data)
    records = sorted(data["competitions"], key=lambda item: (item["next_deadline"]["date"] or "9999", item["name"]))
    lines = [
        "---", "layout: default", "title: Англоязычные литературные конкурсы — каталог",
        "lang: ru", "catalogue_language: en", "section: contests", "---", "",
        "<!-- Generated by scripts/render_catalogue.py from research/en/catalogue.json. Do not edit. -->", "",
        "# Англоязычные литературные конкурсы", "",
        f"**Срез проверки: {data['as_of']}.** Конкурсов и конкурсных категорий в первой партии: {len(records)}; "
        f"стран организаторов: {len(data['coverage']['organizer_countries'])}. Это не полный мировой реестр; расширение выполняется отдельными партиями.", "",
        "Речь о языке произведений. Описания составлены по-русски. Даты и статусы отражают сохранённую проверку, а не проверку в реальном времени. Суммы оставлены в исходных валютах; указан главный приз, а не общий призовой фонд.", "",
        "[Скачать данные JSON]({{ '/data/en-catalogue.json' | relative_url }}) · "
        "[Как устроен поиск](https://github.com/l3chat/4os/blob/main/literary-competitions/research/README.md)", "",
        "Нажмите на название конкурса, чтобы раскрыть подробные условия и источники. В краткой записи видны частота, дедлайн, взнос и главный приз. Можно раскрыть несколько конкурсов одновременно.", "",
        "Тариф может относиться к пакету работ, ранней подаче или последнему объявленному сезону. Пометка † означает, что сумму нужно подтвердить для нового сезона.", "",
    ]
    groups = [
        ("Подтверждённые ближайшие даты", [r for r in records if r["next_deadline"]["date"] and r["eligibility"]["geographic_scope"] != "restricted"]),
        ("Конкурсы с ограничением гражданства или проживания", [r for r in records if r["next_deadline"]["date"] and r["eligibility"]["geographic_scope"] == "restricted"]),
        ("Ожидаем точную дату или новый сезон", [r for r in records if not r["next_deadline"]["date"]]),
    ]
    for title, items in groups:
        lines += [f"## {title}", "", '<ul class="competition-list">']
        for item in items:
            lines.append(render_item(item, data["sources"]))
        lines += ['</ul>', ""]
    return "\n".join(lines).rstrip() + "\n"


def products(data):
    return {
        PROJECT / "docs/contests/en/catalogue.md": render(data),
        PROJECT / "docs/data/en-catalogue.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate research and fail if generated files differ")
    args = parser.parse_args()
    data = json.loads((PROJECT / "research/en/catalogue.json").read_text(encoding="utf-8"))
    errors = []
    for path, content in products(data).items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                errors.append(str(path.relative_to(PROJECT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if errors:
        raise SystemExit("Run scripts/render_catalogue.py to refresh: " + ", ".join(errors))
    print(f"Validated {len(data['competitions'])} research records; generated files " + ("are current." if args.check else "updated."))


if __name__ == "__main__":
    main()
