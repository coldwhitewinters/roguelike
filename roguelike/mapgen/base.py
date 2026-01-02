"""Base classes and utilities for procedural map generation."""
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roguelike.level import Level


class MapGenerator:
    """Base class for procedural map generators.

    All environment generators should inherit from this class and use the
    terrain_grid to build their maps before creating entities.
    """

    def __init__(self, level: "Level", width: int, height: int):
        """Initialize the map generator.

        Args:
            level: The level to populate with entities
            width: Map width in tiles
            height: Map height in tiles
        """
        self.level = level
        self.width = width
        self.height = height
        # Initialize terrain grid with floors
        self.terrain_grid = [["floor" for _ in range(width)] for _ in range(height)]

    def set_tile(self, x: int, y: int, tile_type: str) -> None:
        """Set a tile type in the terrain grid.

        Args:
            x: X coordinate
            y: Y coordinate
            tile_type: Entity template name (e.g., "floor", "wall", "trees")
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.terrain_grid[y][x] = tile_type

    def get_tile(self, x: int, y: int) -> str:
        """Get tile type at a position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Entity template name, or "wall" if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.terrain_grid[y][x]
        return "wall"

    def is_blocked(self, x: int, y: int) -> bool:
        """Check if a tile blocks movement.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if tile blocks movement, False otherwise
        """
        tile = self.get_tile(x, y)
        return tile in ["wall", "water", "trees"]

    def create_entities(self) -> None:
        """Create all entities from the terrain grid.

        This should be called after the terrain grid is fully populated.
        """
        for y in range(self.height):
            for x in range(self.width):
                self.level.create_entity(self.terrain_grid[y][x], x=x, y=y)

    def add_border_walls(self) -> None:
        """Add walls around the map border."""
        for x in range(self.width):
            self.set_tile(x, 0, "wall")
            self.set_tile(x, self.height - 1, "wall")
        for y in range(self.height):
            self.set_tile(0, y, "wall")
            self.set_tile(self.width - 1, y, "wall")

    def flood_fill(self, start_x: int, start_y: int) -> set[tuple[int, int]]:
        """Find all reachable floor positions from a starting point.

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate

        Returns:
            Set of (x, y) tuples representing all reachable positions
        """
        visited = set()
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()

            if (x, y) in visited:
                continue

            if self.is_blocked(x, y):
                continue

            if not (0 <= x < self.width and 0 <= y < self.height):
                continue

            visited.add((x, y))

            # Check 4 cardinal directions
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    stack.append((nx, ny))

        return visited

    def carve_corridor(self, x1: int, y1: int, x2: int, y2: int, width: int = 1) -> None:
        """Carve an L-shaped corridor between two points.

        Args:
            x1: Starting X coordinate
            y1: Starting Y coordinate
            x2: Ending X coordinate
            y2: Ending Y coordinate
            width: Corridor width (default 1)
        """
        # Randomly choose horizontal-then-vertical or vertical-then-horizontal
        if random.random() < 0.5:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for w in range(width):
                    self.set_tile(x, y1 + w, "floor")
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for w in range(width):
                    self.set_tile(x2 + w, y, "floor")
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for w in range(width):
                    self.set_tile(x1 + w, y, "floor")
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for w in range(width):
                    self.set_tile(x, y2 + w, "floor")


def place_stairs_and_player(
    generator: MapGenerator,
    player_x: int,
    player_y: int,
    has_upstairs: bool,
    has_downstairs: bool,
    create_player: bool,
) -> dict:
    """Place stairs and player entities on the map.

    This function ensures stairs and player are placed on valid floor positions.
    It should be called after create_entities() has been called.

    Args:
        generator: The MapGenerator instance
        player_x: Preferred X coordinate for player
        player_y: Preferred Y coordinate for player
        has_upstairs: Whether to place upstairs
        has_downstairs: Whether to place downstairs
        create_player: Whether to place player entity

    Returns:
        Dictionary with 'reserved' key containing set of reserved positions
    """
    reserved = set()

    # Find all valid floor positions (not blocked)
    valid_positions = [
        (x, y)
        for y in range(1, generator.height - 1)
        for x in range(1, generator.width - 1)
        if not generator.is_blocked(x, y)
    ]

    if not valid_positions:
        raise ValueError("No valid floor positions for stair/player placement")

    # Place upstairs
    if has_upstairs:
        up_pos = random.choice(valid_positions)
        reserved.add(up_pos)
        generator.level.create_entity("upstairs", x=up_pos[0], y=up_pos[1])

    # Place downstairs (different position from upstairs)
    if has_downstairs:
        down_candidates = [p for p in valid_positions if p not in reserved]
        if down_candidates:
            # Try to place far from upstairs if possible
            if reserved:
                up_x, up_y = list(reserved)[0]
                # Sort by distance from upstairs, take farthest
                down_candidates.sort(key=lambda p: -(abs(p[0] - up_x) + abs(p[1] - up_y)))
            down_pos = down_candidates[0]
        else:
            down_pos = random.choice(valid_positions)
        reserved.add(down_pos)
        generator.level.create_entity("downstairs", x=down_pos[0], y=down_pos[1])

    # Place player
    if create_player:
        # Try to use preferred position if it's not blocked
        if not generator.is_blocked(player_x, player_y) and (player_x, player_y) not in reserved:
            player_pos = (player_x, player_y)
        else:
            # Fall back to random valid position
            player_candidates = [p for p in valid_positions if p not in reserved]
            if player_candidates:
                player_pos = random.choice(player_candidates)
            else:
                # Use any valid position if all are reserved (shouldn't happen normally)
                player_pos = random.choice(valid_positions)

        reserved.add(player_pos)
        generator.level.create_entity("player", x=player_pos[0], y=player_pos[1])

    return {"reserved": reserved}
