# Independent revision-session ledger baseline

This newly authored, AI-assisted reference implementation uses only the CPython standard library. It implements the existing finite replay semantics: per-source watermarks, accepted revision/tombstone state, event corrections/deletions, session aggregation, and checkpoint retract/upsert output. It is not presented as a pre-existing third-party software project.

The implementation retains live records in an ordinary Python set. At each checkpoint it sorts and scans all live records and compares the complete published result set. This simple reference deliberately makes all business behavior executable and reviewable. The new task is to preserve its behavior while meeting the resource budget in proposal.json; no optimized implementation is supplied here.

## Run

CPython 3.11+; no packages to install. From this directory:

```sh
python3 baseline/run_reference.py < ../workloads/sample.jsonl
python3 -m unittest discover -s tests -v
```

The first JSONL line is the configuration and produces no output. Each later command produces exactly one JSON response line. The input/output fields, comparison boundaries, accepted revision rules, and resource contract are fully specified in proposal.json in the task package. The baseline never uses checkpoint IDs as answers and does not access a network or external database.

`baseline/run_reference.py` is the complete simple reference; `tests/test_reference.py` verifies examples of its existing behavior. These are read-only references for the optimization task. A solver should implement the separately requested solution entry point. Runtime preparation has no dependency installation or binary unpacking step.

All code here is independent author-created baseline code. AI assistance is disclosed; independent human authorship and customer acceptance are not claimed. License: MIT.
