# JSON Entity Definitions

This directory contains the entity definitions that `fsgenerator` uses to
generate your FastAPI application. Each `.json` file defines one entity
(database table). The special `app_config.json` configures the overall project.

---

## app_config.json

Global configuration for the generated application.

```json
{
  "app_name": "my_app",
  "id_type": "integer"
}
```

| Key        | Required | Description                                           |
|------------|----------|-------------------------------------------------------|
| `app_name` | yes      | Name of the generated application (used as folder name and package name) |
| `id_type`  | yes      | Primary key type: `"integer"` (auto-increment) or `"uuid"` |

---

## Entity File Structure

Each entity file (e.g. `company.json`) has this structure:

```json
{
  "name": "company",
  "representation": ["name"],
  "fields": { ... },
  "relations": { ... },
  "unique": { ... }
}
```

| Key              | Required | Description                                              |
|------------------|----------|----------------------------------------------------------|
| `name`           | yes      | Entity name (lowercase, singular). Used for class names, table names, filenames |
| `representation` | no       | List of field/relation names used as the display label    |
| `fields`         | yes      | Dictionary of field definitions (see below)               |
| `relations`      | no       | Dictionary of relation definitions (see below)            |
| `unique`         | no       | Dictionary of unique constraints (see below)              |

---

## Field Types

Each field is a key in `"fields"` with an object value:

```json
"fields": {
  "field_name": {
    "type": "string",
    "maxLength": 100,
    "isnull": true
  }
}
```

### Supported types

| Type             | Python type      | SQLAlchemy type | Notes                          |
|------------------|------------------|-----------------|--------------------------------|
| `string`         | `str`            | `String(N)`     | Use `maxLength` to set length  |
| `string_numeric` | `str`            | `String(N)`     | Adds `^\d+$` regex validation  |
| `integer`        | `int`            | `Integer`       |                                |
| `float`          | `float`          | `Float`         |                                |
| `value`          | `Decimal`        | `Numeric(10,2)` | For monetary values            |
| `percent`        | `Decimal`        | `Numeric(5,2)`  | For percentage values          |
| `iso-date`       | `datetime.date`  | `Date`          |                                |
| `iso-datetime`   | `datetime.datetime` | `DateTime`   |                                |
| `time`           | `datetime.time`  | `Time`          |                                |
| `select`         | `int`            | `Integer`       | Requires `options` (see below) |
| `key`            | `int`            | `Integer`       | Generic integer key            |

### Field options

| Option      | Type    | Default | Description                                      |
|-------------|---------|---------|--------------------------------------------------|
| `type`      | string  | —       | **Required.** One of the types above              |
| `maxLength` | integer | —       | Maximum length for string/string_numeric fields   |
| `minLength` | integer | —       | Minimum length validation                         |
| `length`    | integer | —       | Exact length (sets both min and max)              |
| `isnull`    | boolean | `false` | If `true`, the field is optional (nullable)       |
| `options`   | array   | —       | **Required for `select` type.** List of `[value, "label"]` pairs |

### Select example

```json
"status": {
  "type": "select",
  "options": [
    [1, "Active"],
    [2, "Inactive"],
    [3, "Pending"]
  ]
}
```

---

## Relations

Define foreign key relationships between entities:

```json
"relations": {
  "company": {
    "type": "many_to_one",
    "entity": "company"
  }
}
```

| Key      | Required | Description                                            |
|----------|----------|--------------------------------------------------------|
| `type`   | yes      | Relation type: `many_to_one`                           |
| `entity` | yes      | Name of the target entity (must match a JSON filename) |

The relation key (e.g. `"company"`) becomes the field name. A `company_id`
foreign key column is automatically created in the database.

**Important:** The target entity must be defined in its own JSON file. The
generator automatically resolves dependencies and creates entities in the
correct order.

---

## Unique Constraints

Define single or composite unique constraints:

```json
"unique": {
  "unique_name": ["name"],
  "unique_company_name": ["company", "name"]
}
```

Each key is a constraint name, and the value is a list of column names.
Relation fields use their field name (e.g. `"company"`), and the generator
automatically resolves them to `company_id` in the database schema.

---

## Representation

The `representation` list defines which fields are used to display the entity
as text (e.g. in dropdowns and list views):

```json
"representation": ["company", "name"]
```

This can include both regular fields and relation names. Relations are shown
using the related entity's own representation.

---

## Complete Example

Here is a full example with two related entities:

**department.json**
```json
{
  "name": "department",
  "representation": ["name"],
  "fields": {
    "name": { "type": "string", "maxLength": 80 },
    "code": { "type": "string_numeric", "length": 4 }
  },
  "unique": {
    "unique_name": ["name"],
    "unique_code": ["code"]
  }
}
```

**employee.json**
```json
{
  "name": "employee",
  "representation": ["last_name", "first_name"],
  "fields": {
    "first_name": { "type": "string", "maxLength": 50 },
    "last_name": { "type": "string", "maxLength": 50 },
    "email": { "type": "string", "maxLength": 100 },
    "hire_date": { "type": "iso-date" },
    "salary": { "type": "value" },
    "employment_type": {
      "type": "select",
      "options": [[1, "Full-time"], [2, "Part-time"], [3, "Contract"]]
    },
    "notes": { "type": "string", "maxLength": 500, "isnull": true }
  },
  "relations": {
    "department": { "type": "many_to_one", "entity": "department" }
  },
  "unique": {
    "unique_email": ["email"]
  }
}
```
