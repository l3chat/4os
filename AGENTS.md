# Instructions for agents

This repository maintains multilingual literary competition lists and publishes them with GitHub Pages. Follow README.md and CONTRIBUTING.md.

- Keep canonical content in Markdown under `docs/contests/<language>/`.
- Read the latest repository files before changing them; preserve concurrent edits.
- Preserve stable competition IDs and any original reference numbers.
- Verify changeable facts against official sources for the correct season; record verification dates. Never invent deadlines, fees, eligibility, prizes, or AI policies.
- Distinguish the language of eligible submissions from the language of the description.
- Keep factual rules separate from editorial advice. Mark missing or conflicting information explicitly.
- Do not populate empty lists with invented sample contests. Templates belong outside `docs/`.
- Preserve closed seasons for reference. Update all language copies when shared facts change.
- Use Jekyll `relative_url` for site links so the `/4os` base path works.
- GitHub Pages is the selected host. Do not introduce another hosting platform, analytics, external fonts, or a backend without a task requiring them.
- Do not change repository visibility or claim publication succeeded unless deployment is verified.
- Run appropriate checks. The Pages workflow builds Jekyll and runs `scripts/check_links.py` before deploying. Report any verification that could not be completed.
