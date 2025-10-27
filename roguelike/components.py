"""Components for the roguelike game."""
from __future__ import annotations
from abc import ABC
import numpy as np
from numpy.typing import NDArray


class Component(ABC):
    """Base class for all components."""
    pass


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
