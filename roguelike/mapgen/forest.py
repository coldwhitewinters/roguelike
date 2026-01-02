"""Forest environment generator with organic terrain features."""
import random
from typing import TYPE_CHECKING

from roguelike.mapgen.base import MapGenerator, place_stairs_and_player

if TYPE_CHECKING:
    from roguelike.level import Level


class ForestGenerator(MapGenerator):
    """Generates organic forest environments with trees, water, and clearings."""

    def generate_tree_cluster(self, seed_x: int, seed_y: int, iterations: int) -> None:
        """Generate an organic tree cluster from a seed point.

        Uses iterative expansion where trees spread to neighboring tiles.

        Args:
            seed_x: Starting X coordinate
            seed_y: Starting Y coordinate
            iterations: Number of expansion iterations (controls cluster size)
        """
        trees = {(seed_x, seed_y)}

        for _ in range(iterations):
            new_trees = set()
            for tx, ty in trees:
                # Check 8 neighbors (including diagonals)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue

                        nx, ny = tx + dx, ty + dy

                        # 60% chance to expand to this neighbor
                        if (nx, ny) not in trees and random.random() < 0.6:
                            if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1:
                                new_trees.add((nx, ny))

            trees.update(new_trees)

        # Place trees with some gaps for organic feel (70% density)
        for tx, ty in trees:
            if random.random() < 0.7:
                self.set_tile(tx, ty, "trees")

    def generate_pond(self, center_x: int, center_y: int, radius: int) -> None:
        """Generate a circular pond with slightly irregular edges.

        Args:
            center_x: Center X coordinate
            center_y: Center Y coordinate
            radius: Pond radius in tiles
        """
        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                # Calculate distance with small random variation for irregular edges
                dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                variation = random.uniform(-0.5, 0.5)

                if dist <= radius + variation:
                    if 1 <= x < self.width - 1 and 1 <= y < self.height - 1:
                        self.set_tile(x, y, "water")

    def generate_stream(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Generate a winding stream using drunk walk algorithm.

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Target X coordinate
            end_y: Target Y coordinate
        """
        x, y = start_x, start_y
        positions = [(x, y)]
        max_steps = self.width * 2  # Safety limit

        while (x, y) != (end_x, end_y) and len(positions) < max_steps:
            # Bias toward destination
            dx = 1 if x < end_x else -1 if x > end_x else 0
            dy = 1 if y < end_y else -1 if y > end_y else 0

            # 70% chance to move toward destination, 30% random
            if random.random() < 0.7:
                if dx != 0 and dy != 0:
                    # Choose one direction
                    if random.random() < 0.5:
                        x += dx
                    else:
                        y += dy
                elif dx != 0:
                    x += dx
                elif dy != 0:
                    y += dy
            else:
                # Random walk
                x += random.choice([-1, 0, 1])
                y += random.choice([-1, 0, 1])

            # Keep in bounds
            x = max(1, min(x, self.width - 2))
            y = max(1, min(y, self.height - 2))

            positions.append((x, y))

            # Stop if we're close enough
            if abs(x - end_x) <= 1 and abs(y - end_y) <= 1:
                break

        # Draw stream (1-2 tiles wide)
        for sx, sy in positions:
            self.set_tile(sx, sy, "water")
            # Randomly make it 2 tiles wide
            if random.random() < 0.3:
                for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    if random.random() < 0.5:
                        self.set_tile(sx + dx, sy + dy, "water")

    def add_grass_patches(self) -> None:
        """Add grass patches, primarily near trees for organic distribution."""
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.get_tile(x, y) == "floor":
                    # Check for nearby trees (within 5 tiles)
                    nearby_trees = sum(
                        1
                        for dx in range(-5, 6)
                        for dy in range(-5, 6)
                        if self.get_tile(x + dx, y + dy) == "trees"
                    )

                    # Higher chance of grass near trees
                    if nearby_trees > 0:
                        if random.random() < 0.2:  # 20% near trees
                            self.set_tile(x, y, "grass")
                    else:
                        if random.random() < 0.05:  # 5% in open areas
                            self.set_tile(x, y, "grass")

    def create_clearing(self, center_x: int, center_y: int, radius: int) -> None:
        """Create a clearing by removing trees and obstacles.

        Args:
            center_x: Center X coordinate
            center_y: Center Y coordinate
            radius: Clearing radius
        """
        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if dist <= radius:
                    if 1 <= x < self.width - 1 and 1 <= y < self.height - 1:
                        if self.get_tile(x, y) != "water":
                            self.set_tile(x, y, "floor")


def generate_forest(
    level: "Level",
    width: int,
    height: int,
    player_x: int,
    player_y: int,
    has_upstairs: bool = False,
    has_downstairs: bool = False,
    create_player: bool = True,
) -> None:
    """Generate a forest environment with organic features.

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
    gen = ForestGenerator(level, width, height)

    # 1. Generate tree clusters (8-15 clusters of varying sizes)
    num_clusters = random.randint(8, 15)
    for _ in range(num_clusters):
        seed_x = random.randint(5, width - 5)
        seed_y = random.randint(5, height - 5)
        iterations = random.randint(3, 6)
        gen.generate_tree_cluster(seed_x, seed_y, iterations)

    # 2. Generate water features - ponds
    num_ponds = random.randint(2, 4)
    for _ in range(num_ponds):
        center_x = random.randint(10, width - 10)
        center_y = random.randint(10, height - 10)
        radius = random.randint(2, 4)
        gen.generate_pond(center_x, center_y, radius)

    # 3. Generate streams (1-2 winding streams)
    if random.random() < 0.7:  # 70% chance of stream
        # Stream from one edge to another
        if random.random() < 0.5:
            # Horizontal stream
            start_x = random.randint(1, 5)
            start_y = random.randint(height // 4, 3 * height // 4)
            end_x = random.randint(width - 5, width - 2)
            end_y = random.randint(height // 4, 3 * height // 4)
        else:
            # Vertical stream
            start_x = random.randint(width // 4, 3 * width // 4)
            start_y = random.randint(1, 5)
            end_x = random.randint(width // 4, 3 * width // 4)
            end_y = random.randint(height - 5, height - 2)

        gen.generate_stream(start_x, start_y, end_x, end_y)

    # 4. Create clearings (2-3 large open areas)
    num_clearings = random.randint(2, 3)
    for _ in range(num_clearings):
        center_x = random.randint(15, width - 15)
        center_y = random.randint(15, height - 15)
        radius = random.randint(5, 8)
        gen.create_clearing(center_x, center_y, radius)

    # 5. Add grass patches near trees
    gen.add_grass_patches()

    # 6. Add border walls
    gen.add_border_walls()

    # 7. Create entities from terrain grid
    gen.create_entities()

    # 8. Place stairs and player
    place_stairs_and_player(gen, player_x, player_y, has_upstairs, has_downstairs, create_player)
