from __future__ import annotations

import json

from fsgenerator.parser import AppConfig, EntityDef


def _label(name: str) -> str:
    """Convert snake_case name to Title Case label: first_name -> First Name"""
    return name.replace("_", " ").title()


def generate(entities: list[EntityDef], config: AppConfig) -> list[tuple[str, str]]:
    data: dict = {
        "common": {
            "save": "Save",
            "cancel": "Cancel",
            "edit": "Edit",
            "delete": "Delete",
            "add_new": "Add New",
            "actions": "Actions",
            "id": "ID",
            "list": "List",
            "new": "New",
            "select": "-- Select --",
            "manage": "Manage",
            "error_unique": "A record with the same unique value already exists",
            "error_foreign": "Referenced record does not exist",
            "error_notnull": "A required field is missing",
            "error_check": "Validation failed",
            "error_integrity": "Data integrity error",
            "error_generic": "An error occurred",
        },
    }

    for entity in entities:
        section: dict[str, str] = {"_label": _label(entity.name)}
        for field in entity.fields:
            section[field.name] = _label(field.name)
        for rel in entity.relations:
            if rel.type in ("many_to_one", "one_to_one"):
                section[rel.field_name] = _label(rel.field_name)
        data[entity.name] = section

    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return [("i18n/en.json", content)]
