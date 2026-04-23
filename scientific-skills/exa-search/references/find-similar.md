# Find Similar

Find pages similar to: $ARGUMENTS

## When to use

Use **find-similar** when the user already has a reference URL — a specific paper, article, company homepage, or blog post — and wants more like it. Find-similar uses Exa's neural embeddings to surface pages that are semantically related to the seed URL rather than keyword-matched.

Common patterns:
- "Find more papers like this one: <arxiv URL>"
- "Show me competitors of <company URL>"
- "Find follow-up / citation-style work to <paper URL>"
- "What other posts cover the same angle as <blog URL>?"

When the user only describes a topic (no URL), use **web-search** instead.

## Command

Choose a short, descriptive filename (e.g., `similar-to-mixtral`, `egfr-related-work`). Use lowercase with hyphens, no spaces.

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_find_similar.py" "$URL" \
  --num-results 10 \
  --exclude-source-domain \
  --text --highlights \
  -o "$FILENAME.json"
```

`--exclude-source-domain` drops results from the same domain as the seed URL. Useful when the seed is from a large site (nature.com, arxiv.org) and you want cross-domain coverage rather than sibling articles on the same platform.

## Refinement options

- `--category "research paper"` when the seed is a scholarly URL and you want only scholarly results back
- `--include-domains` / `--exclude-domains` for tighter filtering on top of the neural match
- `--start-published-date YYYY-MM-DD` to restrict to a time window (e.g., only find recent follow-ups to an older seed paper)

## Academic source strategy

For papers, always add `--category "research paper"`:

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_find_similar.py" "$URL" \
  --category "research paper" \
  --num-results 15 \
  --exclude-source-domain \
  --text --highlights \
  -o "$FILENAME.json"
```

This biases results toward other scholarly work rather than news write-ups or blog posts about the seed paper.

## Response format

Same conventions as web search:
- Every claim cited inline as `[Author et al., Year](url)` for academic results or `[Source Title](url)` otherwise
- Mandatory **Sources** section at the end, grouped by Academic / Peer-reviewed vs. Other
- Mention the output file path (`$FILENAME.json`) so the user can ask follow-up questions
