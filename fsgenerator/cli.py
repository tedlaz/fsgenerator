from __future__ import annotations

import argparse
from importlib import resources
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from fsgenerator.generators import (
    domain_entity,
    dto_schema,
    frontend_router,
    i18n,
    repository_impl,
    repository_port,
    router,
    shared,
    sqlalchemy_model,
    template_html,
    use_case,
)
from fsgenerator.parser import AppConfig, load_entities
from fsgenerator.resolver import topological_sort
from fsgenerator.writer import ensure_init_files, write_files

PER_ENTITY_GENERATORS = [
    domain_entity,
    dto_schema,
    sqlalchemy_model,
    repository_port,
    repository_impl,
    use_case,
    router,
    frontend_router,
    template_html,
]


def _templates_dir() -> Path:
    """Resolve the bundled templates directory inside the installed package."""
    return Path(str(resources.files("fsgenerator") / "templates"))


def _sample_entities_dir() -> Path:
    """Resolve the bundled sample_entities directory inside the installed package."""
    return Path(str(resources.files("fsgenerator") / "sample_entities"))


def _init_json_entities() -> None:
    """Copy sample entity files into ./json_entities as a starting point."""
    dest = Path.cwd() / "json_entities"
    if dest.exists():
        print(f"Directory already exists: {dest}")
        raise SystemExit(1)
    src = _sample_entities_dir()
    dest.mkdir()
    for f in sorted(src.iterdir()):
        if f.is_file():
            (dest / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  {f.name}")
    print(f"Created {dest} with sample files. Edit them and run fsgenerator to generate your app.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate application code from JSON entity definitions.",
    )
    parser.add_argument(
        "-x",
        "--init",
        action="store_true",
        help="Create a json_entities/ directory in the current folder with sample starter files, then exit",
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        default=Path.cwd() / "json_entities",
        help="Path to the JSON entities directory (default: ./json_entities)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Parent directory for generated output (default: current directory)",
    )
    args = parser.parse_args()

    if args.init:
        _init_json_entities()
        return

    input_dir: Path = args.input_dir.resolve()
    config = AppConfig.load(input_dir / "app_config.json")
    output_parent: Path = (args.output_dir or Path.cwd()).resolve()
    output_dir = output_parent / config.app_name
    entities = load_entities(input_dir)
    sorted_entities = topological_sort(entities)

    env = Environment(
        loader=FileSystemLoader(str(_templates_dir())),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    all_files: list[tuple[str, str]] = []

    for entity in sorted_entities:
        for gen in PER_ENTITY_GENERATORS:
            all_files.extend(gen.generate(entity, env, config))

    all_files.extend(shared.generate(sorted_entities, env, config))
    all_files.extend(i18n.generate(sorted_entities, config))

    written = write_files(output_dir, all_files)
    init_files = ensure_init_files(output_dir)

    print(f"Generated {len(written)} files in {output_dir}")
    for f in sorted(written):
        print(f"  {f}")
    if init_files:
        print(f"Created {len(init_files)} __init__.py files")
