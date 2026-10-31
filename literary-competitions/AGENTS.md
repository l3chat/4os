# Instructions for agents

This directory maintains multilingual literary competition lists and publishes them with GitHub Pages. The repository also contains unrelated tasks. These instructions apply only to `literary-competitions/`; all project-relative paths below are relative to this directory. Follow its README.md and CONTRIBUTING.md.

- Keep research independent from presentation. Canonical facts and provenance are in `research/<language>/catalogue.json`, with follow-up work in `research/<language>/backlog.json`. See `research/README.md` for the schema and research workflow.
- Run `python3 scripts/render_catalogue.py` after research or rendering changes. It discovers all language catalogues and generates `docs/contests/<language>/catalogue.md` and `docs/data/<language>-catalogue.json` without network access. Use `--language uk` to process one language. Never edit generated files directly or perform a fresh web search merely to restyle results. Other manually maintained lists may remain Markdown under `docs/contests/<language>/`.
- Keep catalogue presentation as a compact numbered list with continuous numbering across groups and two native disclosure levels. The outer summary contains only the competition name. Opening it increases surrounding spacing and reveals brief facts (frequency, deadline, fee and prize); a nested "Подробнее" disclosure reveals full conditions and official sources. Both levels start closed. Distinguish manuscripts from published-book nominations and similarly named awards.
- Record significant research, presentation and infrastructure changes in `../history/events.json`. Run `python3 scripts/render_history.py` to regenerate `../CHANGELOG.md` and `docs/history.md`. Do not invent historical events or claim deployment succeeded before verification; a current changeset may have a null commit to avoid self-reference.
- Preserve null for unconfirmed facts, distinguish historical fees/prizes from the current edition, and keep explicit sources for frequency, deadlines, fees, prizes and eligibility. Never claim the initial batch is exhaustive.
- Read the latest repository files before changing them; preserve concurrent edits.
- Preserve stable competition IDs and any original reference numbers.
- Verify changeable facts against official sources for the correct season; record verification dates. Never invent deadlines, fees, eligibility, prizes, or AI policies.
- Distinguish the language of eligible submissions from the language of the description.
- Keep factual rules separate from editorial advice. Mark missing or conflicting information explicitly.
- Do not populate empty lists with invented sample contests. Templates belong outside `docs/`.
- Preserve closed seasons for reference. Update all language copies when shared facts change.
- Use Jekyll `relative_url` for project links so the `/4os/literary-competitions` base path works. `repository_baseurl` points to the global project directory at `/4os/`.
- GitHub Pages is the selected host. Do not introduce another hosting platform, analytics, external fonts, or a backend without a task requiring them.
- Do not change repository visibility or claim publication succeeded unless deployment is verified.
- The shared executable workflow lives at `../.github/workflows/pages.yml`. It builds `literary-competitions/docs/` into the repository-level `_site/literary-competitions/`, adds the global project directory, validates the combined site and publishes it once. Preserve the project subdirectory in public URLs. Never deploy this project alone over the global Pages site.
- Run appropriate checks. The Pages workflow builds Jekyll and runs `scripts/check_links.py` before deploying. Report any verification that could not be completed.
