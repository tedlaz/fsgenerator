from __future__ import annotations

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef


def generate(
    entity: EntityDef, env: Environment, config: AppConfig
) -> list[tuple[str, str]]:
    files = []

    # Determine if this entity has a direct FK to the tenant entity
    tenant_fk_field: str | None = None
    if config.tenant and entity.name != config.tenant:
        for rel in entity.relations:
            if (
                rel.type in ("many_to_one", "one_to_one")
                and rel.target_entity == config.tenant
            ):
                tenant_fk_field = rel.field_name
                break

    list_template = env.get_template("html_list.html.j2")
    list_content = list_template.render(entity=entity)
    files.append((f"templates/{entity.name}_list.html", list_content))

    form_template = env.get_template("html_form.html.j2")
    form_content = form_template.render(entity=entity, tenant_fk_field=tenant_fk_field)
    files.append((f"templates/{entity.name}_form.html", form_content))

    return files
