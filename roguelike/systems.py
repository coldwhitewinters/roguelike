"""Systems for the roguelike game."""
from __future__ import annotations
from typing import TYPE_CHECKING

import tcod
from abc import ABC, abstractmethod

from roguelike.components import (
    PositionComponent,
    RenderableComponent,
    PlayerComponent,
    BlocksMovementComponent,
    StairComponent
)


if TYPE_CHECKING:
    from roguelike.world import World


class System(ABC):
    """Base class for all systems."""

    @abstractmethod
    def update(self, world: World) -> None:
        """Update the system. Called every frame.

        Args:
            world: The game world
        """
        pass


class RenderSystem(System):
    """System for rendering the game world."""

    def __init__(self, console: tcod.console.Console):
        self.console = console

    def update(self, world: World) -> None:
        """Render all entities with renderable components.

        Args:
            world: The game world
        """
        level = world.get_active_level()
        if level is None:
            return

        self.console.clear()

        # Render all entities with position and renderable components
        for entity in level.get_entities_with_component(RenderableComponent):
            renderable = entity.get_component(RenderableComponent)
            position = entity.get_component(PositionComponent)
            if renderable and position:
                self.console.print(position.x, position.y, renderable.char, fg=renderable.fg)


class LevelTransitionSystem(System):
    """System for handling level transitions via stairs."""

    def update(self, world: World) -> None:
        """Process pending level transition requests.

        Args:
            world: The game world
        """
        # Check if there's a pending transition request
        if world.transition_request is None:
            return

        level = world.get_active_level()
        if level is None:
            world.transition_request = None
            return

        # Find the player
        player_entities = level.get_entities_with_component(PlayerComponent)
        if not player_entities:
            world.transition_request = None
            return

        player = player_entities[0]
        player_pos = player.get_component(PositionComponent)
        if player_pos is None:
            world.transition_request = None
            return

        # Check if player is on stairs that match the transition direction
        for entity in level.get_entities_with_component(StairComponent):
            entity_pos = entity.get_component(PositionComponent)
            stair = entity.get_component(StairComponent)

            if entity_pos and stair and entity_pos.x == player_pos.x and entity_pos.y == player_pos.y:
                # Player is on stairs, check if direction matches request
                if world.transition_request == stair.direction:
                    # Execute the transition
                    self._execute_transition(world, level, player, player_pos, stair.direction)
                    break

        # Clear the transition request
        world.transition_request = None

    def _execute_transition(self, world: World, current_level, player, player_pos, direction: str) -> None:
        """Execute a level transition.

        Args:
            world: The game world
            current_level: The current level
            player: The player entity
            player_pos: The player's position component
            direction: The direction of transition ('up' or 'down')
        """
        # Determine target level index
        current_index = world.active_level_index
        target_index = current_index + 1 if direction == 'down' else current_index - 1

        # Check if target level exists
        if not (0 <= target_index < len(world.levels)):
            return

        # Remove player from current level
        current_level.remove_entity(player)

        # Change to target level
        world.set_active_level(target_index)
        target_level = world.get_active_level()

        # Find the corresponding stairs in the target level (opposite direction)
        opposite_direction = 'up' if direction == 'down' else 'down'
        for target_entity in target_level.get_entities_with_component(StairComponent):
            target_stair = target_entity.get_component(StairComponent)
            target_pos = target_entity.get_component(PositionComponent)

            if target_stair and target_pos and target_stair.direction == opposite_direction:
                # Move player to the stairs position
                player_pos.x = target_pos.x
                player_pos.y = target_pos.y
                break

        # Add player to target level
        target_level.entities.append(player)


class InputSystem(System):
    """System for handling player input."""

    def update(self, world: World, event: tcod.event.KeyDown | None = None) -> None:
        """Process input events and move the player.

        Args:
            world: The game world
            event: The keyboard event to process
        """
        if event is None:
            return

        level = world.get_active_level()
        if level is None:
            return

        # Find the player entity
        player_entities = level.get_entities_with_component(PlayerComponent)
        if not player_entities:
            return

        player = player_entities[0]
        position = player.get_component(PositionComponent)
        if position is None:
            return

        # Check for shift modifier
        shift_held = event.mod & (tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT)

        # Handle stair transition requests
        # On some keyboards, < and > share the same key, so we check the sym for '<' (60)
        # and use the shift modifier to distinguish between them
        if event.sym == 60:  # '<' character
            if shift_held:
                world.transition_request = 'down'
                return
            else:
                world.transition_request = 'up'
                return

        # Get key character for movement
        key_char = chr(event.sym) if event.sym < 128 else None

        # Vim-style movement keys (including diagonals)
        dx, dy = 0, 0
        if key_char == 'h':  # Left
            dx = -1
        elif key_char == 'j':  # Down
            dy = 1
        elif key_char == 'k':  # Up
            dy = -1
        elif key_char == 'l':  # Right
            dx = 1
        elif key_char == 'y':  # Up-left
            dx = -1
            dy = -1
        elif key_char == 'u':  # Up-right
            dx = 1
            dy = -1
        elif key_char == 'b':  # Down-left
            dx = -1
            dy = 1
        elif key_char == 'n':  # Down-right
            dx = 1
            dy = 1

        # Calculate new position
        new_x = position.x + dx
        new_y = position.y + dy

        # Check bounds
        if not (0 <= new_x < level.width and 0 <= new_y < level.height):
            return

        # Check if the destination is blocked
        for entity in level.get_entities_with_component(BlocksMovementComponent):
            entity_pos = entity.get_component(PositionComponent)
            if entity_pos is not None and entity_pos.x == new_x and entity_pos.y == new_y:
                # Destination is blocked, don't move
                return

        # Move is valid
        position.x = new_x
        position.y = new_y
