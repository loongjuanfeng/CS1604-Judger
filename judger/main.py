import os
import re
import random
import shutil
import subprocess
import sys
import tempfile
import zipfile

from rich.console import Console
from rich.text import Text

console = Console()


def _print_result(i, msg, score):
    tp = Text(f"[TEST {i}] ", style="bold cyan")
    tp.append(msg, style="bold green" if score == 10 else "bold red")
    tp.append(f"  [{score}/10]", style="bold yellow" if 0 < score < 10 else ("bold green" if score == 10 else "bold red"))
    console.print(tp)


FORBID = {
    "3_regex": ["regex"],
}


def discover_tasks(base="."):
    tasks = {}
    for entry in sorted(os.listdir(base)):
        if re.match(r"^\d+_.+$", entry) and os.path.isfile(os.path.join(base, entry, "main.cpp")):
            tasks[entry] = ("main.cpp", "_".join(entry.split("_")[1:]))
    return tasks


def _random_name():
    return "".join(chr(ord("A") + random.randint(0, 25)) for _ in range(10))


def check_forbid(task, src):
    for keyword in FORBID.get(task, []):
        kw = keyword.encode()
        with open(src, "rb") as f:
            for line in f:
                if b"include" not in line or kw not in line:
                    continue
                pos = line.find(kw)
                if keyword == "string" and pos > 0 and line[pos - 1] in (ord("c"), ord("C")):
                    continue
                console.print(f'[bold red][FAIL][/] #include "{keyword}" is forbidden in {task}')
                return True
    return False


def judge_one(exe, workdir, input_file, std_file, timeout):
    out = os.path.join(workdir, _random_name() + ".out")
    with open(input_file) as fin, open(out, "w") as fout:
        try:
            subprocess.run([os.path.join(workdir, exe)], check=True, timeout=timeout, stdin=fin, stdout=fout)
        except subprocess.TimeoutExpired:
            return "Out of Time Limit!", 0
        except subprocess.CalledProcessError as e:
            return f"Runtime Error with returncode {e.returncode}", 0
    with open(std_file) as f:
        expected = f.read().rstrip().splitlines()
    with open(out) as f:
        actual = f.read().rstrip().splitlines()
    if len(expected) != len(actual):
        return "File length differs", 0
    for i, (e, a) in enumerate(zip(expected, actual)):
        if e.rstrip() != a.rstrip():
            return f"Wrong answer found at Line {i + 1}", 0
    return "Correct", 10


def judge_task(task, tasks, input_dir=None, output_dir=None, source_dir=None, timeout=2.0):
    """Run all test points for a task. Returns True if all passed."""
    src_file, exe_name = tasks[task]
    src_path = os.path.join(source_dir or task, src_file)
    input_dir = input_dir or os.path.join("data", task)
    output_dir = output_dir or os.path.join("data", task)

    console.rule(f"[bold blue]{task}")

    if not os.path.exists(src_path):
        console.print("[bold red][FAIL][/] Missing Source Code")
        return False
    if check_forbid(task, src_path):
        return False

    workdir = tempfile.mkdtemp()
    try:
        exe_path = os.path.join(workdir, exe_name)
        result = subprocess.run(
            ["g++", src_path, "-o", exe_path, "-g", "-Wall", "-Wextra", "--std=c++17"],
            capture_output=True,
        )
        if result.returncode != 0:
            console.print("[bold red][FAIL][/] Compile Error")
            console.print(result.stderr.decode(), style="red")
            return False

        all_passed = True
        for i in range(1, 6):
            inp = os.path.join(input_dir, f"{i}.in")
            std = os.path.join(output_dir, f"{i}.out")
            if not os.path.exists(inp):
                console.print(f"[bold yellow][WARN][/]  Test point {i}: Missing Input File")
                all_passed = False
            elif not os.path.exists(std):
                console.print(f"[bold yellow][WARN][/]  Test point {i}: Missing Standard Output File")
                all_passed = False
            else:
                msg, score = judge_one(exe_name, workdir, inp, std, timeout)
                _print_result(i, msg, score)
                if score < 10:
                    all_passed = False
        return all_passed
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def pack_zip(tasks, student_id):
    zip_name = f"{student_id}.zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for task in tasks:
            src = os.path.join(task, "main.cpp")
            zf.write(src, arcname=src)
    console.print(f"[bold green][PACK][/] All passed — packed to [cyan]{zip_name}[/]")


def main():
    import argparse

    tasks = discover_tasks()
    parser = argparse.ArgumentParser("judger")
    parser.add_argument("-T", "--task", choices=list(tasks), help="task to judge (omit to run all)")
    parser.add_argument("-I", "--input_dir")
    parser.add_argument("-O", "--output_dir")
    parser.add_argument("-S", "--source_dir")
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    if args.task:
        judge_task(args.task, tasks, args.input_dir, args.output_dir, args.source_dir, args.timeout)
    else:
        all_passed = all(judge_task(t, tasks, timeout=args.timeout) for t in tasks)
        if all_passed:
            student_id = os.environ.get("STUDENT_ID", "student")
            pack_zip(tasks, student_id)
        else:
            console.print("[bold red][FAIL][/] Some tasks failed — no zip created")
            sys.exit(1)


if __name__ == "__main__":
    main()
