# Full stack entity generator

Trying to simplify full stack application creation, i need a single source of truth for my entities. In order to create a backend with fastapi and sqlalchemy, i need to have the core entities as dataclasses, the fastapi route input output data as pydantic schemas and sqlachemy layer model objects. For the frontend jinja2 templates. All these objects could have a single source of truth, json objects one json per entity.

So i need a python application to read the json files from json_entities folder and create a backend application using the previous requests.


At the database layer all entities have a unique key called id which could be either integer or uuid

## Descriptors
- type: the type of the field
- primary_key: useful mostly for database layer
- maxLength: The maximum length of a string field
- minLength: The minimum length of a string field
- length: The exact length of a string field
- isnull: If it is allowed for the field to be null. Default is false

## Types
- integer: integer
- string: string
- string_numeric: string but with numbers only
- iso_date: string containing iso date (yyy-mm-dd)
- iso_datetime: string containing iso datetime
- time: string containing time (hh:mm)
- value: numeric with two decimal places
- float: float
- percent: numeric percent value
- key: foreign key

## Relations

- one_to_one
- one_to_many
- many_to_one
- many_to_many


## Translation

The generator must create a folder keeping translation data