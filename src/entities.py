"""Entity template system for loading and applying entity definitions from YAML."""
from __future__ import annotations
from typing import Any, TypeVar

import yaml
from pathlib import Path

from src.components import (
    Component,
    PositionComponent,
    RenderableComponent,
    PlayerComponent,
    BlocksMovementComponent,
)


C = TypeVar('C', bound=Component)

TEMPLATES_PATH = Path(__file__).parent.parent / "data" / "entities.yaml"
with open(TEMPLATES_PATH, 'r') as f:
    TEMPLATES: dict = yaml.safe_load(f)


class Entity:
    """Entity that can have components attached to it."""

    _next_id = 0

    def __init__(self, name: str | None = None, **kwargs):
        """Initialize an entity.

        Args:
            template: Optional template name to apply to the entity
            **params: Parameters to pass to the template (e.g., x, y for position)
        """
        self.id = Entity._next_id
        Entity._next_id += 1
        self._components: dict[type[Component], Component] = {}

        if name is not None:
            self.apply_template(name, **kwargs)

    def add_component(self, component: Component) -> 'Entity':
        """Add a component to this entity."""
        self._components[type(component)] = component
        return self
    
    def remove_component(self, component_type: type[Component]) -> None:
        """Remove a component from this entity."""
        self._components.pop(component_type, None)
        return self

    def get_component(self, component_type: type[C]) -> C | None:
        """Get a component of the specified type."""
        return self._components.get(component_type)

    def has_component(self, component_type: type[Component]) -> bool:
        """Check if entity has a component of the specified type."""
        return component_type in self._components

    def apply_template(self, name: str, **kwargs) -> 'Entity':
        """Apply a template to an entity with optional parameter overrides."""
        template = TEMPLATES.get(name)

        if template is None:
            raise ValueError(f"Entity '{name}' not found")

        components = template.get('components', [])
        for component_def in components:
            self.add_component_from_def(component_def, **kwargs)

        return self
    
    def add_component_from_def(
        self, 
        component_def: dict[str, Any], 
        **kwargs: dict[str, Any]
    ) -> None:
        """Add a component to an entity based on the component definition."""
        component_type = component_def.get('type')

        if component_type == 'Position':
            # Position can be overridden by kwargs
            x = kwargs.get('x', component_def.get('x', 0))
            y = kwargs.get('y', component_def.get('y', 0))
            self.add_component(PositionComponent(x=x, y=y))

        elif component_type == 'Renderable':
            char = component_def.get('char', '?')
            fg = tuple(component_def.get('fg', [255, 255, 255]))
            self.add_component(RenderableComponent(char=char, fg=fg))

        elif component_type == 'Player':
            self.add_component(PlayerComponent())

        elif component_type == 'BlocksMovement':
            self.add_component(BlocksMovementComponent())

        else:
            raise ValueError(f"Unknown component type: {component_type}")
