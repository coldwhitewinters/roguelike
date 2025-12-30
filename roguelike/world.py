"""World class for managing multiple levels and game systems."""
from __future__ import annotations
from typing import TYPE_CHECKING

from roguelike.level import Level

if TYPE_CHECKING:
    from typing import TypeVar
    from roguelike.systems import System
    S = TypeVar('S', bound=System)


class World:
    """Container for all levels and systems."""

    def __init__(self):
        self.levels: list[Level] = []
        self.systems: list[System] = []
        self.active_level_index: int = 0
        self.transition_request: str | None = None  # 'up', 'down', or None

    def add_level(self, level: Level) -> None:
        """Add a level to the world.

        Args:
            level: The level to add
        """
        self.levels.append(level)

    def get_active_level(self) -> Level | None:
        """Get the currently active level.

        Returns:
            The active level, or None if no levels exist
        """
        if 0 <= self.active_level_index < len(self.levels):
            return self.levels[self.active_level_index]
        return None

    def set_active_level(self, index: int) -> None:
        """Set the active level by index.

        Args:
            index: The index of the level to activate

        Raises:
            IndexError: If the index is out of bounds
        """
        if not 0 <= index < len(self.levels):
            raise IndexError(f"Level index {index} out of bounds (0-{len(self.levels)-1})")
        self.active_level_index = index

    def add_system(self, system: System) -> None:
        """Add a system to the world.

        Args:
            system: The system to add
        """
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

    def update(self) -> None:
        """Update all frame-based systems."""
        for system in self.systems:
            system.update(self)

    def handle_input(self, event) -> None:
        """Handle input events for input-based systems.

        Args:
            event: The input event to process
        """
        from roguelike.systems import InputSystem
        for system in self.systems:
            if isinstance(system, InputSystem):
                system.update(self, event)
