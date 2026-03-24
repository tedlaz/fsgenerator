from __future__ import annotations

from graphlib import TopologicalSorter

from fsgenerator.parser import EntityDef


def build_entity_lookup(entities: list[EntityDef]) -> dict[str, EntityDef]:
    return {e.name: e for e in entities}


def validate_relations(entities: list[EntityDef], lookup: dict[str, EntityDef]) -> None:
    for entity in entities:
        for rel in entity.relations:
            if rel.target_entity not in lookup:
                raise ValueError(
                    f"Entity '{entity.name}' has relation '{rel.field_name}' "
                    f"referencing unknown entity '{rel.target_entity}'"
                )


def topological_sort(entities: list[EntityDef]) -> list[EntityDef]:
    lookup = build_entity_lookup(entities)
    validate_relations(entities, lookup)

    graph: dict[str, set[str]] = {e.name: set() for e in entities}
    for entity in entities:
        for rel in entity.relations:
            if rel.type in ("many_to_one", "one_to_one"):
                graph[entity.name].add(rel.target_entity)

    sorter = TopologicalSorter(graph)
    sorted_names = list(sorter.static_order())
    return [lookup[name] for name in sorted_names]
