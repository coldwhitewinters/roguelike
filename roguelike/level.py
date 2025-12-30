"""Level class for managing entities in a single dungeon level."""
from __future__ import annotations
from typing import TYPE_CHECKING

from roguelike.entities import Entity

if TYPE_CHECKING:
    from typing import TypeVar
    from roguelike.components import Component
    C = TypeVar('C', bound=Component)


class Level:
    """A single level containing entities."""

    def __init__(self, width: int = 0, height: int = 0, depth: int = 0):
        """Initialize a level.

        Args:
            width: Width of the level in tiles
            height: Height of the level in tiles
            depth: Depth/floor number of this level (0 = ground floor)
        """
        self.entities: list[Entity] = []
        self.width = width
        self.height = height
        self.depth = depth

    def create_entity(self, name: str | None = None, **kwargs) -> Entity:
        """Create a new entity and add it to the level.

        Args:
            name: Optional template name to apply to the entity
            **kwargs: Parameters to pass to the template (e.g., x, y for position)

        Returns:
            The created entity
        """
        entity = Entity(name, **kwargs)
        self.entities.append(entity)
        return entity

    def get_entities_with_component(self, component_type: type[C]) -> list[Entity]:
        """Get all entities that have a specific component type.

        Args:
            component_type: The type of component to search for

        Returns:
            List of entities that have the specified component
        """
        return [e for e in self.entities if e.has_component(component_type)]

    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the level.

        Args:
            entity: The entity to remove
        """
        if entity in self.entities:
            self.entities.remove(entity)
