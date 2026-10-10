"""Repo-local falsifier for the f649af index permalink-collision cure.

Born-red before the cure: two subtopic-index pairs each shared one
permalink (``/making-money-from-cr-f649af-affiliate/`` and
``/making-money-from-cr-f649af-niche/``), so the sitemap listed one URL
for two documents and the losing index was shadowed.

Post-cure law: every ``pages/*.md`` front-matter ``permalink`` is unique
across the whole tree, and each cured index carries its topic-specific
route.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
_PERMALINK = re.compile(r"^permalink:\s*[\"']?(/[^\s\"'#]*)[\"']?\s*$", re.M)

CURED = {
    "making_money_from_cr_f649af_affiliate_content_mi_86bb15_index.md":
        "/making-money-from-cr-f649af-affiliate-content-mix/",
    "making_money_from_cr_f649af_affiliate_disclosure_342140_index.md":
        "/making-money-from-cr-f649af-affiliate-disclosures/",
    "making_money_from_cr_f649af_niche_authority_blog_7d2a98_index.md":
        "/making-money-from-cr-f649af-niche-authority/",
    "making_money_from_cr_f649af_niche_buyer_intent_9e67b9_index.md":
        "/making-money-from-cr-f649af-niche-choice/",
}

RETIRED = (
    "/making-money-from-cr-f649af-affiliate/",
    "/making-money-from-cr-f649af-niche/",
)


def _permalink(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    front = _FRONT_MATTER.match(text)
    if not front:
        return None
    match = _PERMALINK.search(front.group(1))
    return match.group(1) if match else None


def _all_permalinks() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for page in sorted(REPO_ROOT.rglob("*.md")):
        permalink = _permalink(page)
        if permalink:
            found.setdefault(permalink, []).append(
                page.relative_to(REPO_ROOT).as_posix()
            )
    return found


def test_tree_wide_permalink_uniqueness():
    """No two markdown pages may share a permalink."""
    duplicates = {
        permalink: files
        for permalink, files in _all_permalinks().items()
        if len(files) > 1
    }
    assert duplicates == {}, f"colliding permalinks: {duplicates}"


def test_cured_indexes_carry_topic_specific_permalinks():
    for name, expected in CURED.items():
        assert _permalink(REPO_ROOT / "pages" / name) == expected


def test_colliding_index_slugs_are_retired():
    """The two shared truncation slugs belong to no page after the cure."""
    for slug in RETIRED:
        pages = _all_permalinks().get(slug, [])
        assert pages == [], f"{slug} still served by {pages}"
