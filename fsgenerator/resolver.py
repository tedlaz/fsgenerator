from __future__ import annotations

from collections import deque
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


def compute_tenant_chains(
    entities: list[EntityDef],
    tenant_name: str,
) -> dict[str, list[str] | None]:
    """For each entity compute the join chain to reach the tenant entity.

    Returns a dict mapping entity name to:
      - ``[]`` if entity IS the tenant or has a direct FK to the tenant
      - a list of entity names to join through (for indirect relations)
      - ``None`` if the entity has no relation path to the tenant

    When the chain is non-empty the **last** entity in the list holds the
    direct FK to the tenant.  When the chain is empty *and* the entity is
    not the tenant itself, the entity's own model has the FK.
    """
    lookup = build_entity_lookup(entities)
    result: dict[str, list[str] | None] = {}

    for entity in entities:
        if entity.name == tenant_name:
            result[entity.name] = []
            continue

        visited: set[str] = set()
        queue: deque[tuple[str, list[str]]] = deque([(entity.name, [])])
        found = False

        while queue and not found:
            current_name, path = queue.popleft()
            if current_name in visited:
                continue
            visited.add(current_name)

            current_ent = lookup.get(current_name)
            if current_ent is None:
                continue

            for rel in current_ent.relations:
                if rel.type not in ("many_to_one", "one_to_one"):
                    continue
                if rel.target_entity == tenant_name:
                    result[entity.name] = path
                    found = True
                    break
                if rel.target_entity not in visited:
                    queue.append((rel.target_entity, path + [rel.target_entity]))

        if not found:
            result[entity.name] = None

    return result
