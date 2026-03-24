# Full-Stack Entity Generator

Generate a complete FastAPI + SQLAlchemy + Jinja2 application from JSON entity definitions.

This project uses JSON files as a single source of truth and generates:

- Domain entities (dataclasses)
- Application DTOs (Pydantic)
- Repository ports and SQLAlchemy repository implementations
- SQLAlchemy models
- API routers (CRUD)
- Frontend routers and HTML templates
- i18n scaffolding
- App bootstrap files

## Why this project exists

When building CRUD-heavy business apps, the same concepts are repeated in many layers:

- Domain models
- API schemas
- Persistence models
- Web forms and lists
- Basic translations

This generator removes repetitive boilerplate by deriving those layers from JSON entity specs.

## Tech stack

- Python 3.14+ for the generator itself
- Jinja2 templates for code generation
- Generated project stack:
	- FastAPI
	- SQLAlchemy
	- Pydantic
	- Jinja2 templates
	- SQLite (by default)

## Repository layout

```text
generator/
	parser.py               # Parses app config and entity JSON files
	resolver.py             # Sorts entities by relation dependencies
	type_mapping.py         # Maps JSON field types to Python/SQLAlchemy/Pydantic
	writer.py               # Writes generated files and __init__.py markers
	generators/             # Per-layer file generators
templates/                # Jinja2 templates used by generators
json_entities/            # Input JSON entity files
main.py                   # CLI entrypoint
```

## How generation works

1. Load app config from app_config.json.
2. Load all entity JSON files in the target directory.
3. Validate relation targets.
4. Topologically sort entities (based on many_to_one and one_to_one dependencies).
5. Render templates for each entity and shared files.
6. Write output into a generated project folder named by app_name.

## Quick start

### 1. Install dependencies

```bash
uv sync
```

### 2. Generate using the default input folder

```bash
uv run generate.py
```

### 3. Generate from a custom folder path

```bash
uv run generate.py -i ./json_entities
```

### 4. Generate into a custom destination parent directory

```bash
uv run generate -i ./json_entities -o ./output
```

This creates ./output/<app_name>.

You can pass any directory that contains:

- app_config.json
- one or more entity JSON files

## CLI

```text
usage: generate [-h] [-i JSON_ENTITIES_DIR] [-o DESTINATION_PARENT_DIR]

options:
	-h, --help            show this help message and exit
	-i JSON_ENTITIES_DIR, --input JSON_ENTITIES_DIR
	                      Path to the directory containing app_config.json and entity JSON files
	-o DESTINATION_PARENT_DIR, --output-parent DESTINATION_PARENT_DIR
	                      Parent directory where the generated app folder will be created
```

If --input is omitted, it defaults to ./json_entities.
If --output-parent is omitted, it defaults to this repository root.

## Input format

### app_config.json

```json
{
	"app_name": "my_app",
	"id_type": "integer"
}
```

Fields:

- app_name: Output directory name for the generated app
- id_type: Global ID type for primary and foreign keys
	- integer
	- uuid

### Entity JSON example

```json
{
	"name": "company",
	"representation": ["name"],
	"fields": {
		"name": {"type": "string", "maxLength": 80},
		"afm": {"type": "string_numeric", "length": 9}
	},
	"relations": {
		"parent": {"type": "many_to_one", "entity": "company"}
	},
	"unique": {
		"unique_name": ["name"],
		"unique_parent_name": ["parent", "name"]
	}
}
```

## Entity schema details

### Root keys

- name: Entity name (used for filenames, routes, table name)
- representation: Fields used for string-style representation in generated UI/repositories
- fields: Dictionary of scalar fields
- relations: Dictionary of relations
- unique: Named unique constraints

### Field options

- type: Required field type
- maxLength: Maximum string length
- minLength: Minimum string length
- length: Exact string length
- isnull: Whether null is allowed (default false)
- primary_key: Parsed from input (the generator uses global id from app_config)
- options: Used for select fields in HTML forms

### Relation options

- type: one_to_one, one_to_many, many_to_one, many_to_many
- entity: Target entity name

## Supported scalar field types

- integer
- string
- string_numeric
- iso_date
- iso_datetime
- time
- value
- float
- percent
- key
- select

Mapping behavior is defined in generator/type_mapping.py.

## Relationship behavior

- Relation definitions are parsed for all listed relation types.
- Code generation currently emits foreign key columns and object relationships for:
	- many_to_one
	- one_to_one
- Dependency sorting is based on many_to_one and one_to_one relations.

## Unique constraints

Named unique constraints are generated at SQLAlchemy table level.

When a unique constraint references a relation field name, the generator maps it to the corresponding foreign key column name (for example, parent -> parent_id).

## Generated output structure

For each entity named example, the generator produces:

- domain/entities/example.py
- application/dtos/example.py
- domain/ports/example.py
- application/use_cases/example.py
- infrastructure/persistence/sqlalchemy/models/example.py
- infrastructure/persistence/sqlalchemy/repositories/example.py
- infrastructure/web/fastapi/routers/example.py
- infrastructure/web/fastapi/routers/example_frontend.py
- templates/example_list.html
- templates/example_form.html

Shared files also include:

- main.py
- pyproject.toml
- infrastructure/web/fastapi/dependencies.py
- infrastructure/web/fastapi/routers/i18n.py
- infrastructure/persistence/sqlalchemy/models/__init__.py
- templates/base.html
- templates/home.html
- i18n_helper.py
- i18n/en.json

The generator also creates missing __init__.py files in generated package directories.

## i18n

The generator creates i18n/en.json with:

- Common UI and error labels
- Per-entity labels
- Per-field labels
- Labels for many_to_one and one_to_one relation selectors

The generated app includes:

- Translation loading helper
- Language-switch router
- HTML templates that call translation keys

## Running the generated app

After generation, change into the generated app folder (the folder named by app_name), install dependencies, and run with uvicorn.

Typical flow:

```bash
cd my_app
uv sync
uv run uvicorn main:app --reload
```

Default database is SQLite at app.db.

## Customizing output

Edit templates in the templates folder to change generated code shape:

- API behavior
- SQLAlchemy model patterns
- HTML layout and UX
- Dependency wiring
- i18n runtime helper

After template changes, run the generator again.

## Known limitations

- The generator focuses on CRUD scaffolding.
- many_to_many and one_to_many relations are parsed but are not fully emitted as SQLAlchemy relationship collections in current templates.
- primary_key inside field definitions is parsed but global ID generation from app_config.id_type is used.
- No migration generation is included (for example, Alembic).

## Troubleshooting

- Error about unknown relation target:
	- Ensure each relation entity points to an existing entity JSON file name.
- Missing app_config.json:
	- Ensure the target input folder contains app_config.json.
- Unexpected type behavior:
	- Check mappings in generator/type_mapping.py.
- Wrong output folder:
	- Check app_name in app_config.json.

## Version

Current package metadata in pyproject.toml:

- name: generator
- version: 0.1.1

