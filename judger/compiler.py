import subprocess

from rich.console import Console

console = Console()


def compile_cpp(sources: list[str] | str, out: str) -> bool:
    """Compile one or more source files to out. Returns True on success."""
    srcs = [sources] if isinstance(sources, str) else sources
    result = subprocess.run(
        ["g++", *srcs, "-o", out, "-g", "-Wall", "-Wextra", "--std=c++17"],
        capture_output=True,
    )
    if result.returncode != 0:
        console.print("[bold #ef4444][FAIL][/] Compile Error")
        console.print(result.stderr.decode(), style="#f87171")
        return False
    return True
