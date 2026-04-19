import ast
import os
import re
from dataclasses import dataclass, field

from rich.console import Console

console = Console()


@dataclass
class TaskConfig:
    sources: list[str]
    exe: str
    timeout: float | None = None


@dataclass
class DiscoverResult:
    tasks: dict[str, TaskConfig]
    forbid: dict[str, list[str]] = field(default_factory=dict)
    source: str = "directory scan"


def _parse_judger_py(path: str) -> DiscoverResult:
    with open(path) as f:
        tree = ast.parse(f.read(), path)

    exec_name: dict = {}
    forbid_map: dict = {}

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name) or target.id not in ("exec_name", "forbid_map"):
                continue
            try:
                val = ast.literal_eval(node.value)
            except Exception:
                continue
            if target.id == "exec_name" and isinstance(val, dict):
                exec_name = val
            elif target.id == "forbid_map" and isinstance(val, dict):
                forbid_map = val

    tasks = {}
    for name, spec in exec_name.items():
        sources = spec[0] if isinstance(spec[0], list) else [spec[0]]
        timeout = float(spec[2]) if len(spec) > 2 else None
        tasks[name] = TaskConfig(sources=sources, exe=spec[1], timeout=timeout)
    return DiscoverResult(tasks=tasks, forbid=forbid_map, source=path)


def discover(base=".") -> DiscoverResult:
    judger_py = os.path.join(base, "judger.py")
    if os.path.isfile(judger_py):
        try:
            result = _parse_judger_py(judger_py)
            if result.tasks:
                return result
        except Exception:
            pass

    tasks = {}
    for entry in sorted(os.listdir(base)):
        if re.match(r"^\d+_.+$", entry) and os.path.isfile(os.path.join(base, entry, "main.cpp")):
            tasks[entry] = TaskConfig(sources=["main.cpp"], exe="_".join(entry.split("_")[1:]))
    return DiscoverResult(tasks=tasks)


def check_forbid(task: str, sources: list[str], forbid: dict[str, list[str]]) -> bool:
    for keyword in forbid.get(task, []):
        kw = keyword.encode()
        for src in sources:
            with open(src, "rb") as f:
                for line in f:
                    if b"include" in line and kw in line:
                        console.print(f'[bold #ef4444][FAIL][/] #include "{keyword}" is forbidden in {task}')
                        return True
    return False
