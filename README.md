# CS1604 Judger

Local judger for CS1604 programming assignments.

## Quick Install

```bash
uv tool install git+https://github.com/loongjuanfeng/CS1604-Judger.git
```

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- `g++` with C++17 support

## Installation

**As a project dependency (development):**

```bash
uv sync
```

**As a global tool (from local source):**

```bash
uv tool install .
```

**As a global tool (directly from GitHub, no clone needed):**

```bash
uv tool install git+https://github.com/loongjuanfeng/CS1604-Judger.git
```

## Usage

Run all tasks and auto-pack a submission zip if all pass:

```bash
STUDENT_ID=your_student_id uv run judger
```

Run a single task:

```bash
uv run judger -T 1_hello
```

### Options

| Flag | Description |
|------|-------------|
| `-T`, `--task` | Task name to judge (e.g. `1_hello`). Omit to run all. |
| `-I`, `--input_dir` | Custom input directory |
| `-O`, `--output_dir` | Custom output directory |
| `-S`, `--source_dir` | Custom source directory |
| `--timeout` | Time limit per test in seconds (default: `2.0`) |

## STUDENT_ID

When all tasks pass, the judger packs your submissions into `<STUDENT_ID>.zip`.

```bash
export STUDENT_ID=20XXXXXXXX
uv run judger
```

If unset, the zip will be named `student.zip`.

## Project Layout

```
.
├── data/
│   └── <task>/
│       ├── 1.in … 5.in
│       └── 1.out … 5.out
├── <task>/
│   └── main.cpp
└── pyproject.toml
```

Each task directory must match `<number>_<name>` (e.g. `1_hello`, `3_regex`) and contain a `main.cpp`.
