"""Entity-Component-System framework for the roguelike game."""
from __future__ import annotations
from typing import TYPE_CHECKING

from roguelike.entities import Entity

if TYPE_CHECKING:
     from typing import TypeVar
     from roguelike.systems import System
     from roguelike.components import Component
     C = TypeVar('C', bound=Component)
     S = TypeVar('S', bound=System)


class World:
    """Container for all entities and systems."""

    def __init__(self):
        self.entities: list[Entity] = []
        self.systems: list[System] = []

    def create_entity(self, name: str | None = None, **kwargs) -> Entity:
        """Create a new entity and add it to the world.

        Args:
            template: Optional template name to apply to the entity
            **params: Parameters to pass to the template (e.g., x, y for position)

        Returns:
            The created entity
        """
        entity = Entity(name, **kwargs)        
        self.entities.append(entity)
        return entity
    
    def get_entities_with_component(self, component_type: type[C]) -> list[Entity]:
        """Get all entities that have a specific component type."""
        return [e for e in self.entities if e.has_component(component_type)]

    def add_system(self, system: System) -> None:
        """Add a system to the world."""
        self.systems.append(system)

    def get_system(self, system_type: type[S]) -> S | None:
        """Get a system of the specified type.

        Args:
            system_type: The type of system to retrieve

        Returns:
            The system instance if found, None otherwise
        """
        for system in self.systems:
            if isinstance(system, system_type):
                return system
        return None

    def update(self, *args, **kwargs) -> None:
        """Update all systems."""
        for system in self.systems:
            system.update(self, *args, **kwargs)
