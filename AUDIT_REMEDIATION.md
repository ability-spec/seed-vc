# October audit remediation

| Finding | Change |
|---|---|
| S01 | Parse `--compile` as a real boolean: False/0 disable, True/1 enable, unknown values fail parsing. |
| S02 | Preserve multidot stems and append a short hash of the resolved input path to distinguish equal names in different directories. Both single and batch save paths use this identity. |

## Verification

**6 CPU-only tests passed** against the actual inference parser and batch save function, extracted without importing GPU/model dependencies.

```bash
python -m pip install pytest
python -m pytest tests/test_cli_regressions.py -q
```

Output filenames change (for example, `speech.one_<path-hash>`). Consumers must use the reported output path instead of constructing the old truncated name. Repeating the same input/target/settings still intentionally overwrites its output; the hash is path identity, not audio-content identity. The hash is a disambiguator, not a cryptographic uniqueness guarantee. No voice quality, compilation speed or GPU runtime was tested.
