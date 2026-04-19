import os
import zipfile

from rich.console import Console

console = Console()


def pack_zip(tasks: dict, student_id: str) -> None:
    zip_name = f"{student_id}.zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for task, cfg in tasks.items():
            for src in cfg.sources:
                path = os.path.join(task, src)
                zf.write(path, arcname=path)
    console.print(f"[bold #22c55e][PACK][/] All passed — packed to [#06b6d4]{zip_name}[/]")
