from __future__ import annotations

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef
from fsgenerator.type_mapping import id_python_import, id_python_type


def generate(
    entity: EntityDef, env: Environment, config: AppConfig
) -> list[tuple[str, str]]:
    template = env.get_template("repository_impl.py.j2")

    imports: set[str] = set()
    id_imp = id_python_import(config)
    if id_imp:
        imports.add(id_imp)

    tenant_chain = config.tenant_chains.get(entity.name) if config.tenant else None
    has_tenant_filter = (
        config.tenant is not None
        and entity.name != config.tenant
        and tenant_chain is not None
    )

    content = template.render(
        entity=entity,
        imports=sorted(imports),
        id_type=id_python_type(config),
        has_tenant_filter=has_tenant_filter,
        tenant_chain=tenant_chain or [],
        tenant_name=config.tenant,
    )

    return [
        (
            f"infrastructure/persistence/sqlalchemy/repositories/{entity.name}.py",
            content,
        )
    ]
