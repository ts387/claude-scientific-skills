# URL Extraction

Extract content from: $ARGUMENTS

## Command

Choose a short, descriptive filename based on the URL or content (e.g., `vespa-docs`, `react-hooks-api`). Use lowercase with hyphens, no spaces.

```bash
parallel-cli extract "$ARGUMENTS" --json -o "/tmp/$FILENAME.md"
```

Options if needed:
- `--objective "focus area"` to focus on specific content

## Response format

Return content as:

**[Page Title](URL)**

Then the extracted content verbatim, with these rules:
- Keep content verbatim - do not paraphrase or summarize
- Parse lists exhaustively - extract EVERY numbered/bulleted item
- Strip only obvious noise: nav menus, footers, ads
- Preserve all facts, names, numbers, dates, quotes

After the response, mention the output file path (`/tmp/$FILENAME.md`) so the user knows it's available for follow-up questions.
