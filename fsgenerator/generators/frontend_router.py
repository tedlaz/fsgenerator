from __future__ import annotations

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef
from fsgenerator.type_mapping import id_python_import, id_python_type


def generate(
    entity: EntityDef, env: Environment, config: AppConfig
) -> list[tuple[str, str]]:
    template = env.get_template("frontend_router.py.j2")

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

    # Determine which relation targets should be filtered by tenant
    tenant_filtered_relations: set[str] = set()
    tenant_fk_field: str | None = None
    if config.tenant and config.tenant_chains:
        for rel in entity.relations:
            if rel.type in ("many_to_one", "one_to_one"):
                if rel.target_entity == config.tenant and entity.name != config.tenant:
                    tenant_fk_field = rel.field_name
                target_chain = config.tenant_chains.get(rel.target_entity)
                if target_chain is not None and rel.target_entity != config.tenant:
                    tenant_filtered_relations.add(rel.field_name)

    content = template.render(
        entity=entity,
        imports=sorted(imports),
        id_type=id_python_type(config),
        has_tenant_filter=has_tenant_filter,
        tenant_name=config.tenant,
        tenant_filtered_relations=tenant_filtered_relations,
        tenant_fk_field=tenant_fk_field,
    )

    return [(f"infrastructure/web/fastapi/routers/{entity.name}_frontend.py", content)]
