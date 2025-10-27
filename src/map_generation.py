"""Map generation functions for the roguelike game."""
import random
from src.world import World


def generate_map(world: World, map_width: int, map_height: int, player_x: int, player_y: int) -> None:
    """Generate a basic map with floors, walls, and random obstacles.

    Args:
        world: The ECS world to populate with map entities
        map_width: Width of the map in tiles
        map_height: Height of the map in tiles
        player_x: X coordinate for player starting position (walls won't spawn here)
        player_y: Y coordinate for player starting position (walls won't spawn here)
    """
    # Create floor tile entities for the entire map
    for y in range(map_height):
        for x in range(map_width):
            world.create_entity("floor", x=x, y=y)

    # Create wall entities around the map border
    for x in range(map_width):
        # Top wall
        world.create_entity("wall", x=x, y=0)
        # Bottom wall
        world.create_entity("wall", x=x, y=map_height - 1)

    for y in range(map_height):
        # Left wall
        world.create_entity("wall", x=0, y=y)
        # Right wall
        world.create_entity("wall", x=map_width - 1, y=y)

    # Create random walls inside the map for testing
    num_random_walls = 100
    for _ in range(num_random_walls):
        # Generate random position inside the map (not on border)
        x = random.randint(1, map_width - 2)
        y = random.randint(1, map_height - 2)

        # Skip player starting position
        if x == player_x and y == player_y:
            continue

        world.create_entity("wall", x=x, y=y)

    # Create the player entity
    world.create_entity("player", x=player_x, y=player_y)
