from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    app_name: str = "generated_app"
    id_type: str = "integer"  # "integer" or "uuid"

    @classmethod
    def load(cls, path: Path) -> AppConfig:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            app_name=data.get("app_name", "generated_app"),
            id_type=data.get("id_type", "integer"),
        )


@dataclass
class FieldDef:
    name: str
    type: str
    max_length: int | None = None
    min_length: int | None = None
    length: int | None = None
    is_null: bool = False
    primary_key: bool = False
    options: list[list] | None = None


@dataclass
class RelationDef:
    field_name: str
    type: str  # "many_to_one", "one_to_many", "one_to_one", "many_to_many"
    target_entity: str


@dataclass
class UniqueDef:
    name: str
    columns: list[str]


@dataclass
class EntityDef:
    name: str
    fields: list[FieldDef] = field(default_factory=list)
    relations: list[RelationDef] = field(default_factory=list)
    uniques: list[UniqueDef] = field(default_factory=list)
    representation: list[str] = field(default_factory=list)

    @property
    def class_name(self) -> str:
        return self.name.capitalize()

    @property
    def relation_names(self) -> set[str]:
        return {r.field_name for r in self.relations}


def _normalize_type(type_name: str) -> str:
    return type_name.replace("-", "_")


def _parse_entity(data: dict) -> EntityDef:
    name = data["name"]

    fields = []
    for field_name, field_data in data.get("fields", {}).items():
        fields.append(FieldDef(
            name=field_name,
            type=_normalize_type(field_data["type"]),
            max_length=field_data.get("maxLength"),
            min_length=field_data.get("minLength"),
            length=field_data.get("length"),
            is_null=field_data.get("isnull", False),
            primary_key=field_data.get("primary_key", False),
            options=field_data.get("options"),
        ))

    relations = []
    for rel_name, rel_data in data.get("relations", {}).items():
        relations.append(RelationDef(
            field_name=rel_name,
            type=rel_data["type"],
            target_entity=rel_data["entity"],
        ))

    relation_names = {r.field_name for r in relations}

    uniques = []
    for uq_name, uq_cols in data.get("unique", {}).items():
        resolved_cols = [
            f"{col}_id" if col in relation_names else col
            for col in uq_cols
        ]
        uniques.append(UniqueDef(name=uq_name, columns=resolved_cols))

    representation = data.get("representation", [])

    return EntityDef(name=name, fields=fields, relations=relations, uniques=uniques, representation=representation)


def load_entities(directory: str | Path) -> list[EntityDef]:
    directory = Path(directory)
    entities = []
    for path in sorted(directory.glob("*.json")):
        if path.name == "app_config.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        entities.append(_parse_entity(data))
    return entities
