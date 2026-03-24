from __future__ import annotations

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef
from fsgenerator.type_mapping import (
    id_python_import,
    id_python_type,
    python_imports,
    python_type_annotation,
)


def generate(entity: EntityDef, env: Environment, config: AppConfig) -> list[tuple[str, str]]:
    template = env.get_template("domain_entity.py.j2")

    imports: set[str] = set()
    id_imp = id_python_import(config)
    if id_imp:
        imports.add(id_imp)
    for field in entity.fields:
        imp = python_imports(field, config)
        if imp:
            imports.add(imp)

    field_types = {
        f.name: python_type_annotation(f, config)
        for f in entity.fields
    }

    content = template.render(
        entity=entity,
        imports=sorted(imports),
        id_type=id_python_type(config),
        field_types=field_types,
    )

    return [(f"domain/entities/{entity.name}.py", content)]
