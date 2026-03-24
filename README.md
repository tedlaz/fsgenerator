# Full-Stack Entity Generator

Generate a complete FastAPI + SQLAlchemy + Jinja2 application from JSON entity definitions.

This project uses JSON files as a single source of truth and generates:

- Domain entities (dataclasses)
- Application DTOs (Pydantic)
- Repository ports and SQLAlchemy repository implementations
- SQLAlchemy models
- API routers (CRUD) with Bearer JWT authentication
- Frontend routers and HTML templates with custom CSS
- JWT authentication system (login, register, user management)
- i18n scaffolding
- App bootstrap files

## Why this project exists

When building CRUD-heavy business apps, the same concepts are repeated in many layers:

- Domain models
- API schemas
- Persistence models
- Web forms and lists
- Authentication and authorization
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
	- PyJWT + bcrypt (authentication)
	- Custom CSS (no Bootstrap dependency)
	- SQLite (by default)

## Repository layout

```text
fsgenerator/
	cli.py                  # CLI entrypoint with argparse
	parser.py               # Parses app config and entity JSON files
	resolver.py             # Sorts entities by relation dependencies
	type_mapping.py         # Maps JSON field types to Python/SQLAlchemy/Pydantic
	writer.py               # Writes generated files and __init__.py markers
	generators/             # Per-layer file generators
	templates/              # Jinja2 templates used by generators
	sample_entities/        # Starter JSON files for -x/--init scaffolding
json_entities/            # Input JSON entity files (example)
generate.py               # Convenience wrapper for fsgenerator CLI
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

### 2. Scaffold a starter project (optional)

```bash
uv run generate.py -x
```

This creates a `json_entities/` directory in the current folder with sample JSON files and a README explaining the entity format.

### 3. Generate using the default input folder

```bash
uv run generate.py
```

### 4. Generate from a custom folder path

```bash
uv run generate.py -i ./json_entities
```

### 5. Generate into a custom destination parent directory

```bash
uv run generate.py -i ./json_entities -o ./output
```

This creates ./output/<app_name>.

You can pass any directory that contains:

- app_config.json
- one or more entity JSON files

## CLI

```text
usage: fsgenerator [-h] [-x] [-i INPUT_DIR] [-o OUTPUT_DIR]

options:
	-h, --help            show this help message and exit
	-x, --init            Create a json_entities/ directory with sample starter
	                      files, then exit
	-i INPUT_DIR, --input-dir INPUT_DIR
	                      Path to the JSON entities directory (default: ./json_entities)
	-o OUTPUT_DIR, --output-dir OUTPUT_DIR
	                      Parent directory for generated output (default: current directory)
```

If --input-dir is omitted, it defaults to ./json_entities.
If --output-dir is omitted, it defaults to the current directory.

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
- representation: Fields used for display labels in dropdowns and list views
- fields: Dictionary of scalar fields
- relations: Dictionary of relations
- unique: Named unique constraints

### Field options

| Option      | Type    | Default | Description                                          |
|-------------|---------|---------|------------------------------------------------------|
| type        | string  | —       | Required. One of the supported types below            |
| maxLength   | integer | —       | Maximum string length                                 |
| minLength   | integer | —       | Minimum string length validation                      |
| length      | integer | —       | Exact string length (sets both min and max)           |
| isnull      | boolean | false   | Whether null is allowed (makes the field optional)    |
| options     | array   | —       | Required for `select` type. List of `[value, "label"]` pairs |

### Relation options

- type: many_to_one (currently fully supported in generation)
- entity: Target entity name (must match a JSON filename)

## Supported scalar field types

| Type           | Python type        | SQLAlchemy type | Notes                          |
|----------------|--------------------|-----------------|--------------------------------|
| integer        | int                | Integer         |                                |
| string         | str                | String(N)       | Use maxLength to set length    |
| string_numeric | str                | String(N)       | Adds `^\d+$` regex validation  |
| iso-date       | datetime.date      | Date            |                                |
| iso-datetime   | datetime.datetime  | DateTime        |                                |
| time           | datetime.time      | Time            |                                |
| value          | Decimal            | Numeric(10,2)   | For monetary values            |
| float          | float              | Float           |                                |
| percent        | Decimal            | Numeric(5,2)    | For percentage values          |
| key            | int                | Integer         | Generic integer key            |
| select         | int                | Integer         | Requires options field         |

Mapping behavior is defined in fsgenerator/type_mapping.py.

## Relationship behavior

- Relation definitions are parsed for all listed relation types.
- Code generation currently emits foreign key columns and object relationships for:
	- many_to_one
	- one_to_one
- Dependency sorting is based on many_to_one and one_to_one relations.
- Relation fields are placed before data fields in all generated files (entities, DTOs, models, templates).

## Unique constraints

Named unique constraints are generated at SQLAlchemy table level.

When a unique constraint references a relation field name, the generator maps it to the corresponding foreign key column name (for example, parent -> parent_id).

## Authentication

The generated application includes a complete JWT-based authentication system:

- **Login/Register** pages with bcrypt password hashing
- **JWT tokens** stored in HTTP-only cookies (60-minute expiry)
- **Auth middleware** that redirects unauthenticated users to the login page
- **API Bearer auth** — all REST API endpoints require a valid JWT in the Authorization header
- **Admin user** seeded on first startup (email: `admin@admin.com`, password: `admin`)
- **User management** — admin users can toggle active/admin status of other users
- **Change password** — authenticated users can change their own password

Public paths (login, register, static files, API docs) are accessible without authentication.

## Generated output structure

For each entity named example, the generator produces:

- domain/entities/example.py
- application/dtos/example.py
- domain/ports/example.py
- application/use_cases/example.py
- infrastructure/persistence/sqlalchemy/models/example.py
- infrastructure/persistence/sqlalchemy/repositories/example.py
- infrastructure/web/fastapi/routers/example.py (API)
- infrastructure/web/fastapi/routers/example_frontend.py
- templates/example_list.html
- templates/example_form.html

Shared files:

- main.py (FastAPI app with auth middleware and admin seeding)
- pyproject.toml
- static/style.css (custom CSS design system)
- infrastructure/web/fastapi/dependencies.py
- infrastructure/web/fastapi/routers/i18n.py
- infrastructure/persistence/sqlalchemy/models/\_\_init\_\_.py
- infrastructure/persistence/sqlalchemy/models/auth_models.py
- auth_security.py (JWT + bcrypt utilities)
- infrastructure/web/fastapi/routers/auth.py
- templates/base.html
- templates/home.html
- templates/login.html
- templates/register.html
- templates/change_password.html
- templates/admin_users.html
- i18n_helper.py
- i18n/en.json

The generator also creates missing \_\_init\_\_.py files in generated package directories.

## i18n

The generator creates i18n/en.json with:

- Common UI and error labels
- Per-entity labels
- Per-field labels
- Labels for many_to_one and one_to_one relation selectors
- Authentication labels (login, register, password, user management)

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

Default database is SQLite at app.db. An admin user is created on first startup.

Default admin credentials:

- Email: admin@admin.com
- Password: admin

## Customizing output

Edit templates in fsgenerator/templates/ to change generated code shape:

- API behavior
- SQLAlchemy model patterns
- HTML layout and UX
- Authentication flow
- Dependency wiring
- CSS styling (static/style.css)
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
	- Check mappings in fsgenerator/type_mapping.py.
- Wrong output folder:
	- Check app_name in app_config.json.
- Delete errors showing raw JSON:
	- Entity delete endpoints display errors on the list page when a record has dependent relations.

## Version

Current version: 0.5.0