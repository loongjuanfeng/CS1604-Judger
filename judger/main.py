import os
import shutil
import sys
import tempfile

from rich.console import Console
from rich.table import Table

from judger.compiler import compile_cpp
from judger.judge import judge_task
from judger.pack import pack_zip
from judger.tasks import check_forbid, discover

console = Console()
DEFAULT_TIMEOUT = 2.0


def _doctor(result) -> None:
    console.print(f"[bold #3b82f6]Source:[/] {result.source}\n")
    table = Table(show_header=True, header_style="bold #06b6d4")
    table.add_column("#")
    table.add_column("Task")
    table.add_column("Sources")
    table.add_column("Exe")
    table.add_column("Timeout")
    table.add_column("Forbid")
    for i, (name, cfg) in enumerate(result.tasks.items(), 1):
        timeout = f"{cfg.timeout}s" if cfg.timeout else f"{DEFAULT_TIMEOUT}s (default)"
        forbid = ", ".join(result.forbid.get(name, [])) or "—"
        table.add_row(str(i), name, ", ".join(cfg.sources), cfg.exe, timeout, forbid)
    console.print(table)


def _run_task(task: str, result) -> bool:
    cfg = result.tasks[task]
    src_paths = [os.path.join(task, s) for s in cfg.sources]
    data_dir = os.path.join("data", task)

    missing = next((p for p in src_paths if not os.path.exists(p)), None)
    if missing:
        console.print(f"[bold #ef4444][FAIL][/] Missing Source Code: {missing}")
        return False
    if check_forbid(task, src_paths, result.forbid):
        return False

    workdir = tempfile.mkdtemp()
    try:
        exe = os.path.join(workdir, cfg.exe)
        if not compile_cpp(src_paths, exe):
            return False
        return judge_task(task, exe, data_dir, data_dir, cfg.timeout or DEFAULT_TIMEOUT)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main():
    result = discover()
    task_list = list(result.tasks)
    argv = sys.argv[1:]

    if not argv:
        if not task_list:
            console.print("[bold #ef4444][FAIL][/] No tasks found in current directory")
            sys.exit(1)
        all_passed = all(_run_task(t, result) for t in task_list)
        if all_passed:
            pack_zip(result.tasks, os.environ.get("STUDENT_ID", "student"))
        else:
            console.print("[bold #ef4444][FAIL][/] Some tasks failed — no zip created")
            sys.exit(1)

    elif argv[0] == "doctor":
        if not task_list:
            console.print("[bold #ef4444][FAIL][/] No tasks found in current directory")
            sys.exit(1)
        _doctor(result)

    elif argv[0] == "run" and len(argv) == 2:
        try:
            n = int(argv[1])
        except ValueError:
            console.print(f"[bold #ef4444][FAIL][/] Expected a number, got: {argv[1]}")
            sys.exit(1)
        if not 1 <= n <= len(task_list):
            console.print(f"[bold #ef4444][FAIL][/] Task number {n} out of range (1–{len(task_list)})")
            sys.exit(1)
        _run_task(task_list[n - 1], result)

    else:
        console.print("Usage: judger [doctor | run <number>]")
        sys.exit(1)


if __name__ == "__main__":
    main()
