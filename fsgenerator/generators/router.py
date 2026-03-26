from __future__ import annotations

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef
from fsgenerator.type_mapping import id_python_import, id_python_type


def generate(
    entity: EntityDef, env: Environment, config: AppConfig
) -> list[tuple[str, str]]:
    template = env.get_template("router.py.j2")

    imports: set[str] = set()
    id_imp = id_python_import(config)
    if id_imp:
        imports.add(id_imp)

    has_tenant_filter = (
        config.tenant is not None
        and entity.name != config.tenant
        and config.tenant_chains.get(entity.name) is not None
    )

    content = template.render(
        entity=entity,
        imports=sorted(imports),
        id_type=id_python_type(config),
        has_tenant_filter=has_tenant_filter,
    )

    return [(f"infrastructure/web/fastapi/routers/{entity.name}.py", content)]
