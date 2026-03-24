from __future__ import annotations

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef
from fsgenerator.type_mapping import (
    id_python_type,
    id_sqla_default,
    id_sqla_import,
    id_sqla_type,
    id_uuid4_import_needed,
    python_imports,
    python_type_annotation,
    sqla_column_type,
    sqla_import_type,
)


def _quote(value: str) -> str:
    return f'"{value}"'


def generate(entity: EntityDef, env: Environment, config: AppConfig) -> list[tuple[str, str]]:
    template = env.get_template("sqlalchemy_model.py.j2")

    sqla_imports: set[str] = set()
    sqla_imports.add(id_sqla_import(config))
    for f in entity.fields:
        sqla_imports.add(sqla_import_type(f, config))

    has_relationships = any(
        r.type in ("many_to_one", "one_to_one") for r in entity.relations
    )
    if has_relationships:
        sqla_imports.add("ForeignKey")

    has_length_checks = any(f.length for f in entity.fields)
    table_args = len(entity.uniques) > 0 or has_length_checks
    if entity.uniques:
        sqla_imports.add("UniqueConstraint")
    if has_length_checks:
        sqla_imports.add("CheckConstraint")

    extra_imports: set[str] = set()
    for f in entity.fields:
        imp = python_imports(f, config)
        if imp:
            extra_imports.add(imp)

    field_types = {
        f.name: python_type_annotation(f, config)
        for f in entity.fields
    }
    sqla_column_types = {
        f.name: sqla_column_type(f, config)
        for f in entity.fields
    }

    fk_sqla_type = id_sqla_type(config)

    env.filters["quote"] = _quote

    content = template.render(
        entity=entity,
        sqla_imports=sorted(sqla_imports),
        extra_imports=sorted(extra_imports),
        id_type=id_python_type(config),
        id_sqla_type=id_sqla_type(config),
        id_sqla_default=id_sqla_default(config),
        fk_sqla_type=fk_sqla_type,
        uuid_import=id_uuid4_import_needed(config),
        has_relationships=has_relationships,
        field_types=field_types,
        sqla_column_types=sqla_column_types,
        table_args=table_args,
    )

    return [(f"infrastructure/persistence/sqlalchemy/models/{entity.name}.py", content)]
