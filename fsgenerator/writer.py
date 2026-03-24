from __future__ import annotations

from pathlib import Path


def write_files(output_dir: Path, files: list[tuple[str, str]]) -> list[str]:
    written = []
    for rel_path, content in files:
        full_path = output_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        written.append(rel_path)
    return written


def ensure_init_files(output_dir: Path) -> list[str]:
    created = []
    for dirpath in sorted(output_dir.rglob("*")):
        if dirpath.is_dir() and not dirpath.name.startswith("."):
            init_file = dirpath / "__init__.py"
            if not init_file.exists():
                has_py = any(f.suffix == ".py" for f in dirpath.iterdir())
                if has_py or any(d.is_dir() for d in dirpath.iterdir()):
                    init_file.write_text("", encoding="utf-8")
                    created.append(str(init_file.relative_to(output_dir)))
    return created
