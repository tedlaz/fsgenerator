from __future__ import annotations

from pathlib import Path

from jinja2 import Environment

from fsgenerator.parser import AppConfig, EntityDef


def generate(entities: list[EntityDef], env: Environment, config: AppConfig) -> list[tuple[str, str]]:
    files = []

    # Base SQLAlchemy model
    base_template = env.get_template("base_model.py.j2")
    files.append((
        "infrastructure/persistence/sqlalchemy/models/__init__.py",
        base_template.render(),
    ))

    # Auth model
    auth_models_template = env.get_template("auth_models.py.j2")
    files.append((
        "infrastructure/persistence/sqlalchemy/models/auth.py",
        auth_models_template.render(),
    ))

    # Auth security module
    auth_security_template = env.get_template("auth_security.py.j2")
    files.append((
        "auth_security.py",
        auth_security_template.render(),
    ))

    # Auth frontend router
    auth_router_template = env.get_template("auth_router.py.j2")
    files.append((
        "infrastructure/web/fastapi/routers/auth.py",
        auth_router_template.render(),
    ))

    # Dependencies (session, engine)
    deps_template = env.get_template("dependencies.py.j2")
    files.append((
        "infrastructure/web/fastapi/dependencies.py",
        deps_template.render(),
    ))

    # Main app
    main_template = env.get_template("main_app.py.j2")
    entity_names = [e.name for e in entities]
    files.append((
        "main.py",
        main_template.render(entities=entities, entity_names=entity_names, app_name=config.app_name),
    ))

    # Generated pyproject.toml
    pyproject_template = env.get_template("pyproject_toml.j2")
    files.append((
        "pyproject.toml",
        pyproject_template.render(app_name=config.app_name),
    ))

    # Base HTML template
    base_html_template = env.get_template("html_base.html.j2")
    files.append((
        "templates/base.html",
        base_html_template.render(entities=entities, app_name=config.app_name),
    ))

    # Home page template
    home_template = env.get_template("html_home.html.j2")
    files.append((
        "templates/home.html",
        home_template.render(entities=entities, app_name=config.app_name),
    ))

    # Auth HTML templates
    for tpl_name, out_name in [
        ("html_login.html.j2", "templates/login.html"),
        ("html_register.html.j2", "templates/register.html"),
        ("html_change_password.html.j2", "templates/change_password.html"),
        ("html_admin_users.html.j2", "templates/admin_users.html"),
    ]:
        tpl = env.get_template(tpl_name)
        files.append((out_name, tpl.render(app_name=config.app_name)))

    # i18n runtime helper
    i18n_helper_template = env.get_template("i18n_helper.py.j2")
    files.append((
        "i18n_helper.py",
        i18n_helper_template.render(),
    ))

    # i18n language-switch router
    i18n_router_template = env.get_template("i18n_router.py.j2")
    files.append((
        "infrastructure/web/fastapi/routers/i18n.py",
        i18n_router_template.render(),
    ))

    # Custom CSS
    css_path = Path(__file__).resolve().parent.parent / "templates" / "style.css"
    files.append((
        "static/style.css",
        css_path.read_text(encoding="utf-8"),
    ))

    return files
