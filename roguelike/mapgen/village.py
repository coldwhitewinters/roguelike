"""Village environment generator with buildings and roads."""
import random
from typing import TYPE_CHECKING

from roguelike.mapgen.base import MapGenerator, place_stairs_and_player

if TYPE_CHECKING:
    from roguelike.level import Level


class VillageGenerator(MapGenerator):
    """Generates village settlements with buildings, roads, and open spaces."""

    def create_road(self, x1: int, y1: int, x2: int, y2: int, width: int = 2, vertical: bool = False) -> None:
        """Create a straight road (horizontal or vertical).

        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            width: Road width in tiles
            vertical: If True, create vertical road; otherwise horizontal
        """
        if vertical:
            # Vertical road
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for w in range(width):
                    x = x1 + w
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.set_tile(x, y, "dirt")
        else:
            # Horizontal road
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for w in range(width):
                    y = y1 + w
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.set_tile(x, y, "dirt")

    def create_building(self, x: int, y: int, width: int, height: int) -> None:
        """Create a building with walls, floor interior, and a door.

        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            width: Building width
            height: Building height
        """
        # Create perimeter walls
        for bx in range(x, x + width):
            if 0 <= bx < self.width and 0 <= y < self.height:
                self.set_tile(bx, y, "wall")  # Top wall
            if 0 <= bx < self.width and 0 <= y + height - 1 < self.height:
                self.set_tile(bx, y + height - 1, "wall")  # Bottom wall

        for by in range(y, y + height):
            if 0 <= x < self.width and 0 <= by < self.height:
                self.set_tile(x, by, "wall")  # Left wall
            if 0 <= x + width - 1 < self.width and 0 <= by < self.height:
                self.set_tile(x + width - 1, by, "wall")  # Right wall

        # Create floor interior
        for by in range(y + 1, y + height - 1):
            for bx in range(x + 1, x + width - 1):
                if 0 <= bx < self.width and 0 <= by < self.height:
                    self.set_tile(bx, by, "floor")

        # Add a door (80% chance)
        if random.random() < 0.8 and width > 2 and height > 2:
            door_side = random.choice(["top", "bottom", "left", "right"])

            if door_side == "top":
                door_x = x + width // 2
                door_y = y
            elif door_side == "bottom":
                door_x = x + width // 2
                door_y = y + height - 1
            elif door_side == "left":
                door_x = x
                door_y = y + height // 2
            else:  # right
                door_x = x + width - 1
                door_y = y + height // 2

            if 0 <= door_x < self.width and 0 <= door_y < self.height:
                self.set_tile(door_x, door_y, "floor")

    def add_vegetation(self) -> None:
        """Add trees and grass to empty areas."""
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                tile = self.get_tile(x, y)

                # Add vegetation only to floor tiles
                if tile == "floor":
                    # Small chance of tree cluster near buildings
                    if random.random() < 0.02:
                        self.set_tile(x, y, "trees")
                        # Maybe add neighboring trees
                        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                            if random.random() < 0.4:
                                nx, ny = x + dx, y + dy
                                if self.get_tile(nx, ny) == "floor":
                                    self.set_tile(nx, ny, "trees")
                    # Grass in open areas
                    elif random.random() < 0.15:
                        self.set_tile(x, y, "grass")


def generate_village(
    level: "Level",
    width: int,
    height: int,
    player_x: int,
    player_y: int,
    has_upstairs: bool = False,
    has_downstairs: bool = False,
    create_player: bool = True,
) -> None:
    """Generate a village environment with buildings and roads.

    Args:
        level: The level to populate
        width: Map width in tiles
        height: Map height in tiles
        player_x: Preferred player X position
        player_y: Preferred player Y position
        has_upstairs: Whether to place upstairs
        has_downstairs: Whether to place downstairs
        create_player: Whether to place player entity
    """
    gen = VillageGenerator(level, width, height)

    # 1. Create main road (horizontal or vertical through center)
    main_road_horizontal = random.choice([True, False])

    if main_road_horizontal:
        # Horizontal main road
        road_y = height // 2
        gen.create_road(1, road_y, width - 2, road_y, width=3, vertical=False)
    else:
        # Vertical main road
        road_x = width // 2
        gen.create_road(road_x, 1, road_x, height - 2, width=3, vertical=True)

    # 2. Create cross roads (2-3 perpendicular roads)
    num_cross_roads = random.randint(2, 3)
    for _ in range(num_cross_roads):
        if main_road_horizontal:
            # Create vertical cross roads
            road_x = random.randint(width // 4, 3 * width // 4)
            gen.create_road(road_x, 1, road_x, height - 2, width=2, vertical=True)
        else:
            # Create horizontal cross roads
            road_y = random.randint(height // 4, 3 * height // 4)
            gen.create_road(1, road_y, width - 2, road_y, width=2, vertical=False)

    # 3. Create town square (large open area near center)
    square_size = random.randint(12, 18)
    square_x = (width - square_size) // 2
    square_y = (height - square_size) // 2

    for y in range(square_y, square_y + square_size):
        for x in range(square_x, square_x + square_size):
            if 1 <= x < width - 1 and 1 <= y < height - 1:
                if gen.get_tile(x, y) != "dirt":  # Don't override roads
                    gen.set_tile(x, y, "floor")

    # 4. Place buildings in available spaces
    # Try to place 8-12 buildings
    num_buildings_target = random.randint(8, 12)
    buildings_placed = 0
    attempts = 0
    max_attempts = num_buildings_target * 5

    while buildings_placed < num_buildings_target and attempts < max_attempts:
        attempts += 1

        # Random building size
        building_width = random.randint(5, 12)
        building_height = random.randint(5, 10)

        # Random position
        building_x = random.randint(5, width - building_width - 5)
        building_y = random.randint(5, height - building_height - 5)

        # Check if area is clear (not in town square, not on roads)
        clear = True
        for by in range(building_y - 1, building_y + building_height + 1):
            for bx in range(building_x - 1, building_x + building_width + 1):
                if not (0 <= bx < width and 0 <= by < height):
                    clear = False
                    break
                tile = gen.get_tile(bx, by)
                # Avoid placing on dirt (roads) or within town square
                if tile == "dirt" or (square_x <= bx < square_x + square_size and square_y <= by < square_y + square_size):
                    clear = False
                    break
            if not clear:
                break

        if clear:
            gen.create_building(building_x, building_y, building_width, building_height)
            buildings_placed += 1

    # 5. Add vegetation (trees and grass)
    gen.add_vegetation()

    # 6. Add border walls
    gen.add_border_walls()

    # 7. Create entities from terrain grid
    gen.create_entities()

    # 8. Place stairs and player
    place_stairs_and_player(gen, player_x, player_y, has_upstairs, has_downstairs, create_player)
