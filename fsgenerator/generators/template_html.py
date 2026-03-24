from __future__ import annotations

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef


def generate(entity: EntityDef, env: Environment, config: AppConfig) -> list[tuple[str, str]]:
    files = []

    list_template = env.get_template("html_list.html.j2")
    list_content = list_template.render(entity=entity)
    files.append((f"templates/{entity.name}_list.html", list_content))

    form_template = env.get_template("html_form.html.j2")
    form_content = form_template.render(entity=entity)
    files.append((f"templates/{entity.name}_form.html", form_content))

    return files
