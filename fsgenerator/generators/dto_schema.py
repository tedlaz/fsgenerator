from __future__ import annotations

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef
from fsgenerator.type_mapping import (
    id_python_import,
    id_python_type,
    pydantic_field_kwargs,
    python_imports,
    python_type_annotation,
)


def generate(entity: EntityDef, env: Environment, config: AppConfig) -> list[tuple[str, str]]:
    template = env.get_template("dto_schema.py.j2")

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

    has_field_constraints = False
    field_kwargs_create = {}
    field_kwargs_update = {}
    for f in entity.fields:
        kwargs = pydantic_field_kwargs(f, config)
        if kwargs:
            has_field_constraints = True
            parts = ", ".join(f'{k}={v!r}' for k, v in kwargs.items())
            field_kwargs_create[f.name] = f" = Field({parts})"
            field_kwargs_update[f.name] = f" = Field(default=None, {parts})"
        else:
            field_kwargs_create[f.name] = ""
            field_kwargs_update[f.name] = ""

    content = template.render(
        entity=entity,
        imports=sorted(imports),
        id_type=id_python_type(config),
        field_types=field_types,
        field_kwargs_create=field_kwargs_create,
        field_kwargs_update=field_kwargs_update,
        has_field_constraints=has_field_constraints,
    )

    return [(f"application/dtos/{entity.name}.py", content)]
