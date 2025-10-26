"""Components for the roguelike game."""
import numpy as np
from numpy.typing import NDArray

from src.ecs import Component


class GridComponent(Component):
    """Component that holds a 2D grid of tiles."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Initialize with floor tiles (walkable)
        # 0 = floor, 1 = wall
        self.tiles: NDArray[np.int8] = np.zeros((height, width), dtype=np.int8)


class PositionComponent(Component):
    """Component for entity position in the world."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class RenderableComponent(Component):
    """Component for entities that can be rendered."""

    def __init__(self, char: str, fg: tuple[int, int, int] = (255, 255, 255)):
        self.char = char
        self.fg = fg


class PlayerComponent(Component):
    """Tag component to identify the player entity."""
    pass


class BlocksMovementComponent(Component):
    """Tag component for entities that block movement (walls, etc.)."""
    pass
