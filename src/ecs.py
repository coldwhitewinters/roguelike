"""Entity-Component-System framework for the roguelike game."""
from abc import ABC, abstractmethod
from typing import TypeVar


class Component:
    """Base class for all components."""
    pass


C = TypeVar('C', bound=Component)


class Entity:
    """Entity that can have components attached to it."""

    _next_id = 0

    def __init__(self):
        self.id = Entity._next_id
        Entity._next_id += 1
        self._components: dict[type[Component], Component] = {}

    def add_component(self, component: Component) -> 'Entity':
        """Add a component to this entity."""
        self._components[type(component)] = component
        return self

    def get_component(self, component_type: type[C]) -> C | None:
        """Get a component of the specified type."""
        return self._components.get(component_type)

    def has_component(self, component_type: type[Component]) -> bool:
        """Check if entity has a component of the specified type."""
        return component_type in self._components

    def remove_component(self, component_type: type[Component]) -> None:
        """Remove a component from this entity."""
        self._components.pop(component_type, None)


class World:
    """Container for all entities and systems."""

    def __init__(self, template_manager=None):
        self.entities: list[Entity] = []
        self.systems: list['System'] = []
        self.template_manager = template_manager

    def create_entity(self, template: str = None, **params) -> Entity:
        """Create a new entity and add it to the world.

        Args:
            template: Optional template name to apply to the entity
            **params: Parameters to pass to the template (e.g., x, y for position)

        Returns:
            The created entity
        """
        entity = Entity()
        self.entities.append(entity)

        # Apply template if provided
        if template and self.template_manager:
            self.template_manager.apply_template(entity, template, **params)

        return entity

    def add_system(self, system: 'System') -> None:
        """Add a system to the world."""
        self.systems.append(system)

    def update(self, *args, **kwargs) -> None:
        """Update all systems."""
        for system in self.systems:
            system.update(self, *args, **kwargs)

    def get_entities_with_component(self, component_type: type[C]) -> list[Entity]:
        """Get all entities that have a specific component type."""
        return [e for e in self.entities if e.has_component(component_type)]


class System(ABC):
    """Base class for all systems."""

    @abstractmethod
    def update(self, world: World, *args, **kwargs) -> None:
        """Update the system. Called every frame."""
        pass
