"""Systems for the roguelike game."""
from __future__ import annotations
from typing import TYPE_CHECKING

import tcod
from abc import ABC, abstractmethod

from src.components import (
    PositionComponent, 
    RenderableComponent, 
    PlayerComponent, 
    BlocksMovementComponent
)


if TYPE_CHECKING:
    from src.world import World


class System(ABC):
    """Base class for all systems."""

    @abstractmethod
    def update(self, world: World, *args, **kwargs) -> None:
        """Update the system. Called every frame."""
        pass


class RenderSystem(System):
    """System for rendering the game world."""

    def __init__(self, console: tcod.console.Console):
        self.console = console

    def update(self, world: World) -> None:
        """Render all entities with renderable components."""
        self.console.clear()

        # Render all entities with position and renderable components
        for entity in world.get_entities_with_component(RenderableComponent):
            renderable = entity.get_component(RenderableComponent)
            position = entity.get_component(PositionComponent)
            if renderable and position:
                self.console.print(position.x, position.y, renderable.char, fg=renderable.fg)


class InputSystem(System):
    """System for handling player input."""

    def __init__(self, map_width: int, map_height: int):
        self.map_width = map_width
        self.map_height = map_height

    def update(self, world: World, event: tcod.event.KeyDown | None = None) -> None:
        """Process input events and move the player."""
        if event is None:
            return

        # Find the player entity
        player_entities = world.get_entities_with_component(PlayerComponent)
        if not player_entities:
            return

        player = player_entities[0]
        position = player.get_component(PositionComponent)
        if position is None:
            return

        # Vim-style movement keys (using scancode for lowercase letters)
        dx, dy = 0, 0
        # Check both KeySym and scancode for letter keys
        key_char = chr(event.sym) if event.sym < 128 else None

        if key_char == 'h':  # Left
            dx = -1
        elif key_char == 'j':  # Down
            dy = 1
        elif key_char == 'k':  # Up
            dy = -1
        elif key_char == 'l':  # Right
            dx = 1

        # Calculate new position
        new_x = position.x + dx
        new_y = position.y + dy

        # Check bounds
        if not (0 <= new_x < self.map_width and 0 <= new_y < self.map_height):
            return

        # Check if the destination is blocked
        for entity in world.get_entities_with_component(BlocksMovementComponent):
            entity_pos = entity.get_component(PositionComponent)
            if entity_pos is not None and entity_pos.x == new_x and entity_pos.y == new_y:
                # Destination is blocked, don't move
                return

        # Move is valid
        position.x = new_x
        position.y = new_y
