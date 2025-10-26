"""Entity template system for loading and applying entity definitions from YAML."""
import yaml
from pathlib import Path
from typing import Any

from src.ecs import Entity
from src.components import (
    PositionComponent,
    RenderableComponent,
    PlayerComponent,
    BlocksMovementComponent,
)


class EntityTemplateManager:
    """Manages entity templates loaded from YAML files."""

    def __init__(self):
        self.templates: dict[str, dict[str, Any]] = {}

    def load_templates(self, yaml_path: str | Path) -> None:
        """Load entity templates from a YAML file."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            if data:
                self.templates.update(data)

    def get_template(self, template_name: str) -> dict[str, Any] | None:
        """Get a template by name."""
        return self.templates.get(template_name)

    def apply_template(self, entity: Entity, template_name: str, **params) -> Entity:
        """Apply a template to an entity with optional parameter overrides."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        components = template.get('components', [])
        for component_def in components:
            self._add_component(entity, component_def, params)

        return entity

    def _add_component(self, entity: Entity, component_def: dict[str, Any], params: dict[str, Any]) -> None:
        """Add a component to an entity based on the component definition."""
        component_type = component_def.get('type')

        if component_type == 'Position':
            # Position can be overridden by params
            x = params.get('x', component_def.get('x', 0))
            y = params.get('y', component_def.get('y', 0))
            entity.add_component(PositionComponent(x=x, y=y))

        elif component_type == 'Renderable':
            char = component_def.get('char', '?')
            fg = tuple(component_def.get('fg', [255, 255, 255]))
            entity.add_component(RenderableComponent(char=char, fg=fg))

        elif component_type == 'Player':
            entity.add_component(PlayerComponent())

        elif component_type == 'BlocksMovement':
            entity.add_component(BlocksMovementComponent())

        else:
            raise ValueError(f"Unknown component type: {component_type}")
