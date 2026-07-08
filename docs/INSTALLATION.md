# Installation guide

## Prerequisites

- Python 3.10 or later.
- An Anthropic API key with access to a Claude model (`claude-sonnet-4-5` by default). Get one at [console.anthropic.com](https://console.anthropic.com).
- `pip`. A virtual environment is recommended but not required.

## 1. Get the code

If you have the zip archive:

```bash
unzip qtc-clause-bench.zip
cd qtc-clause-bench
```

If you're cloning from GitHub:

```bash
git clone https://github.com/<your-org>/qtc-clause-bench.git
cd qtc-clause-bench
```

## 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Installs `anthropic` (model client), `jsonschema` (output validation), and `pytest` (test runner).

## 4. Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...        # on Windows: set ANTHROPIC_API_KEY=sk-ant-...
```

Don't commit this key. Export it in your shell or use a `.env` file kept out of version control (`.gitignore` already excludes `.env`).

## 5. Verify the install

Run the test suite first. It checks dataset integrity, prompt building, and scoring logic, none of it calls the Claude API, so it passes even without an API key:

```bash
pytest tests/ -v
```

You should see 49 tests pass. If the dataset tests fail with a "no matching annotation" error, check that `data/contracts/` and `data/annotations/` both extracted correctly from the archive and every `.txt` has a same-named `.json`.

Then confirm your API key works by extracting from one bundled sample contract:

```bash
python -m qtc_clause_bench.cli extract --contract c001_msa_northwind
```

A successful run prints a JSON object with all 4 clause types. See the [user guide](USER_GUIDE.md) for how to read it and how to run the full scored benchmark.

## Troubleshooting

**`ModuleNotFoundError: No module named 'qtc_clause_bench'`**
Run commands from the repo root with `python -m qtc_clause_bench.cli ...`, not by calling `cli.py` directly.

**`anthropic.AuthenticationError`**
`ANTHROPIC_API_KEY` isn't set or is invalid in the current shell. Check with `echo $ANTHROPIC_API_KEY`.

**`FileNotFoundError: no rubric...` or dataset pairing errors**
`dataset.list_contract_ids()` requires every file in `data/contracts/*.txt` to have a same-named file in `data/annotations/*.json`, and vice versa. This is enforced on every load, not just in tests, so a stray file will surface immediately with the exact mismatched name.

**`SCHEMA VALIDATION FAILED` on extraction**
The model's response didn't match `schema/extraction_result.schema.json`, most often an enum value it invented (e.g. a `trigger_type` outside the fixed list) or a missing required field. Rerun; if it repeats on the same contract, see the [architecture doc's known gaps](ARCHITECTURE.md#known-gaps) for the retry-loop improvement this would motivate.

## Next steps

- [User guide](USER_GUIDE.md): running extraction and the scored benchmark, reading every metric.
- [Architecture](ARCHITECTURE.md): pipeline design, scoring methodology, dataset construction.
