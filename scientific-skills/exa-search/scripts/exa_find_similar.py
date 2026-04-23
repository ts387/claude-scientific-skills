#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["exa-py>=1.14.0"]
# ///
"""Find pages similar to a given URL via Exa's find_similar endpoint.

Example:
    uv run exa_find_similar.py \\
        https://arxiv.org/abs/2401.04088 \\
        --num-results 10 \\
        --exclude-source-domain \\
        --text --highlights \\
        -o similar.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from typing import Any

try:
    from exa_py import Exa
except ImportError:
    print(
        "exa_py not installed. Run: uv pip install exa-py  (or invoke with: uv run --with exa-py)",
        file=sys.stderr,
    )
    sys.exit(2)


EXA_INTEGRATION_HEADER = "scientific-agent-skills"


@dataclass
class SimilarResult:
    """Typed view of a single find-similar result for JSON export."""

    title: str | None
    url: str
    id: str | None
    author: str | None
    published_date: str | None
    score: float | None
    text: str | None = None
    highlights: list[str] = field(default_factory=list)
    summary: str | None = None


def _split_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def _build_contents(text: bool, highlights: bool, summary: str | None) -> dict[str, Any] | None:
    contents: dict[str, Any] = {}
    if text:
        contents["text"] = True
    if highlights:
        contents["highlights"] = True
    if summary is not None:
        contents["summary"] = {"query": summary} if summary else True
    return contents or None


def _to_typed(item: Any) -> SimilarResult:
    return SimilarResult(
        title=getattr(item, "title", None),
        url=getattr(item, "url", ""),
        id=getattr(item, "id", None),
        author=getattr(item, "author", None),
        published_date=getattr(item, "published_date", None),
        score=getattr(item, "score", None),
        text=getattr(item, "text", None),
        highlights=list(getattr(item, "highlights", None) or []),
        summary=getattr(item, "summary", None),
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        print("EXA_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(2)

    client = Exa(api_key=api_key)
    client.headers["x-exa-integration"] = EXA_INTEGRATION_HEADER

    contents = _build_contents(args.text, args.highlights, args.summary)

    kwargs: dict[str, Any] = {
        "url": args.url,
        "num_results": args.num_results,
        "exclude_source_domain": args.exclude_source_domain,
    }
    if include := _split_csv(args.include_domains):
        kwargs["include_domains"] = include
    if exclude := _split_csv(args.exclude_domains):
        kwargs["exclude_domains"] = exclude
    if args.start_published_date:
        kwargs["start_published_date"] = args.start_published_date
    if args.end_published_date:
        kwargs["end_published_date"] = args.end_published_date
    if args.category:
        kwargs["category"] = args.category

    if contents is not None:
        response = client.find_similar_and_contents(**kwargs, **contents)
    else:
        response = client.find_similar(**kwargs)

    typed = [_to_typed(item) for item in getattr(response, "results", []) or []]
    return {
        "url": args.url,
        "num_results": len(typed),
        "results": [asdict(result) for result in typed],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find pages similar to a URL with Exa.")
    parser.add_argument("url", help="Seed URL to find similar pages for.")
    parser.add_argument("--num-results", type=int, default=10, help="Number of results (1-100).")
    parser.add_argument(
        "--exclude-source-domain",
        action="store_true",
        help="Exclude results from the same domain as the seed URL.",
    )
    parser.add_argument("--include-domains", default=None, help="Comma-separated allowlist.")
    parser.add_argument("--exclude-domains", default=None, help="Comma-separated blocklist.")
    parser.add_argument("--start-published-date", default=None, help="ISO date, e.g. 2024-01-01.")
    parser.add_argument("--end-published-date", default=None, help="ISO date, e.g. 2024-12-31.")
    parser.add_argument(
        "--category",
        default=None,
        choices=[
            "company",
            "research paper",
            "news",
            "pdf",
            "github",
            "tweet",
            "personal site",
            "linkedin profile",
            "financial report",
            "people",
        ],
        help="Bias results toward a content category.",
    )
    parser.add_argument("--text", action="store_true", help="Return full-text content per result.")
    parser.add_argument("--highlights", action="store_true", help="Return extracted highlight snippets.")
    parser.add_argument(
        "--summary",
        nargs="?",
        const="",
        default=None,
        help="Return LLM summary. Optional value is a query to focus the summary.",
    )
    parser.add_argument("-o", "--output", default=None, help="Write JSON to this file (default: stdout).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run(args)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {len(payload['results'])} results to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
