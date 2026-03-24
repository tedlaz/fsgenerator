from __future__ import annotations

from fsgenerator.parser import AppConfig, FieldDef

# Maps JSON type -> (python_type, python_import, sqlalchemy_type, sqlalchemy_import)
TYPE_MAP: dict[str, dict] = {
    "integer": {
        "python": "int",
        "python_import": None,
        "sqla": "Integer",
        "sqla_import": "Integer",
    },
    "string": {
        "python": "str",
        "python_import": None,
        "sqla": "String({length})",
        "sqla_import": "String",
    },
    "string_numeric": {
        "python": "str",
        "python_import": None,
        "sqla": "String({length})",
        "sqla_import": "String",
    },
    "iso_date": {
        "python": "datetime.date",
        "python_import": "import datetime",
        "sqla": "Date",
        "sqla_import": "Date",
    },
    "iso_datetime": {
        "python": "datetime.datetime",
        "python_import": "import datetime",
        "sqla": "DateTime",
        "sqla_import": "DateTime",
    },
    "time": {
        "python": "datetime.time",
        "python_import": "import datetime",
        "sqla": "Time",
        "sqla_import": "Time",
    },
    "value": {
        "python": "Decimal",
        "python_import": "from decimal import Decimal",
        "sqla": "Numeric(10, 2)",
        "sqla_import": "Numeric",
    },
    "float": {
        "python": "float",
        "python_import": None,
        "sqla": "Float",
        "sqla_import": "Float",
    },
    "percent": {
        "python": "Decimal",
        "python_import": "from decimal import Decimal",
        "sqla": "Numeric(5, 2)",
        "sqla_import": "Numeric",
    },
    "key": {
        "python": "int",
        "python_import": None,
        "sqla": "Integer",
        "sqla_import": "Integer",
    },
    "select": {
        "python": "int",
        "python_import": None,
        "sqla": "Integer",
        "sqla_import": "Integer",
    },
}


def python_type(f: FieldDef, config: AppConfig) -> str:
    mapping = TYPE_MAP.get(f.type, TYPE_MAP["string"])
    return mapping["python"]


def python_type_annotation(f: FieldDef, config: AppConfig) -> str:
    base = python_type(f, config)
    if f.is_null:
        return f"{base} | None"
    return base


def python_imports(f: FieldDef, config: AppConfig) -> str | None:
    mapping = TYPE_MAP.get(f.type, TYPE_MAP["string"])
    return mapping["python_import"]


def sqla_column_type(f: FieldDef, config: AppConfig) -> str:
    mapping = TYPE_MAP.get(f.type, TYPE_MAP["string"])
    sqla = mapping["sqla"]
    length = f.length or f.max_length
    if "{length}" in sqla:
        if length:
            return sqla.format(length=length)
        return sqla.format(length="")
    return sqla


def sqla_import_type(f: FieldDef, config: AppConfig) -> str:
    mapping = TYPE_MAP.get(f.type, TYPE_MAP["string"])
    return mapping["sqla_import"]


def pydantic_field_kwargs(f: FieldDef, config: AppConfig) -> dict:
    kwargs = {}
    if f.max_length or f.length:
        kwargs["max_length"] = f.length or f.max_length
    if f.min_length:
        kwargs["min_length"] = f.min_length
    if f.length and not f.min_length:
        kwargs["min_length"] = f.length
    if f.type == "string_numeric":
        kwargs["pattern"] = r"^\d+$"
    return kwargs


def id_python_type(config: AppConfig) -> str:
    return "UUID" if config.id_type == "uuid" else "int"


def id_python_import(config: AppConfig) -> str | None:
    if config.id_type == "uuid":
        return "from uuid import UUID"
    return None


def id_sqla_type(config: AppConfig) -> str:
    if config.id_type == "uuid":
        return "Uuid"
    return "Integer"


def id_sqla_import(config: AppConfig) -> str:
    if config.id_type == "uuid":
        return "Uuid"
    return "Integer"


def id_sqla_default(config: AppConfig) -> str:
    if config.id_type == "uuid":
        return "default=uuid4"
    return "autoincrement=True"


def id_uuid4_import_needed(config: AppConfig) -> bool:
    return config.id_type == "uuid"
