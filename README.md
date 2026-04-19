# CS1604 Judger

Local judger for CS1604 programming assignments. Compiles and judges C++ submissions against test data, then packs a submission zip when all tasks pass.

## Install

```bash
uv tool install git+https://github.com/loongjuanfeng/CS1604-Judger.git
```

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- `g++` with C++17 support

## Usage

```bash
# Judge all tasks; pack <STUDENT_ID>.zip if all pass
STUDENT_ID=20XXXXXXXX judger

# Judge a single task by number
judger run 2

# Show detected configuration
judger doctor
```

## Project Layout

```
.
├── judger.py          # task config (optional, see below)
├── data/
│   └── <task>/
│       ├── 1.in … N.in
│       └── 1.out … N.out
└── <task>/
    └── main.cpp
```

Task directories must match `<number>_<name>` (e.g. `1_hello`, `3_regex`).

## judger.py (optional)

If a `judger.py` is present in the working directory, the judger reads task configuration from its `exec_name` and `forbid_map` dicts instead of scanning directories.

```python
exec_name = {
    '1_hello':  ['main.cpp', 'hello'],
    '2_multi':  [['main.cpp', 'util.cpp'], 'multi'],  # multi-file
    '3_regex':  ['main.cpp', 'regex', 1.0],           # custom timeout (seconds)
}

forbid_map = {
    '3_regex': ['regex'],  # forbidden #include keywords
}
```

Without `judger.py`, tasks are auto-discovered from directories and compiled from `main.cpp`.

## Reinstalling after code changes

```bash
uv tool uninstall judger
uv cache clean --force
uv tool install .
```
