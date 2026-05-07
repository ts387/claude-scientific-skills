# pacsomatic skill

This directory packages the nf-core/pacsomatic operator skill.

## Layout

- `SKILL.md`: skill contract and usage guidance
- `config.yaml`: baseline defaults for runtime/execution/validation behavior
- `references/`: operator guidance and troubleshooting notes
- `scripts/run_pacsomatic.py`: execution helper
- `tests/`: unit tests for helper behavior

## Run tests

```bash
cd pacsomatic
python -m unittest discover -s tests -v
```
