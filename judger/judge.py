import os
import re
import subprocess
import tempfile

from rich.console import Console
from rich.text import Text

console = Console()


def _print_result(i: int, msg: str, score: int) -> None:
    tp = Text(f"[TEST {i}] ", style="bold #06b6d4")
    tp.append(msg, style="bold #22c55e" if score == 10 else "bold #ef4444")
    score_style = "bold #22c55e" if score == 10 else ("bold #f59e0b" if score > 0 else "bold #ef4444")
    tp.append(f"  [{score}/10]", style=score_style)
    console.print(tp)


def judge_one(exe: str, input_file: str, std_file: str, timeout: float) -> tuple[str, int]:
    fd, out = tempfile.mkstemp(suffix=".out")
    os.close(fd)
    try:
        with open(input_file) as fin, open(out, "w") as fout:
            try:
                subprocess.run([exe], check=True, timeout=timeout, stdin=fin, stdout=fout)
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
    finally:
        os.unlink(out)


def judge_task(task: str, exe: str, input_dir: str, output_dir: str, timeout: float) -> bool:
    console.rule(f"[bold #3b82f6]{task}")
    indices = sorted(
        int(m.group(1))
        for f in os.listdir(input_dir)
        if (m := re.fullmatch(r"(\d+)\.in", f))
    )
    all_passed = True
    for i in indices:
        inp = os.path.join(input_dir, f"{i}.in")
        std = os.path.join(output_dir, f"{i}.out")
        if not os.path.exists(std):
            console.print(f"[bold #f59e0b][WARN][/]  Test point {i}: Missing Standard Output File")
            all_passed = False
        else:
            msg, score = judge_one(exe, inp, std, timeout)
            _print_result(i, msg, score)
            if score < 10:
                all_passed = False
    return all_passed
