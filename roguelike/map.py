"""Map generation functions for the roguelike game."""
import random
from roguelike.level import Level


def generate_map(
    level: Level,
    map_width: int,
    map_height: int,
    player_x: int,
    player_y: int,
    has_upstairs: bool = False,
    has_downstairs: bool = False,
    upstairs_pos: tuple[int, int] | None = None,
    downstairs_pos: tuple[int, int] | None = None,
    create_player: bool = True
) -> None:
    """Generate a basic map with floors, walls, and random obstacles.

    Args:
        level: The level to populate with map entities
        map_width: Width of the map in tiles
        map_height: Height of the map in tiles
        player_x: X coordinate for player starting position (walls won't spawn here)
        player_y: Y coordinate for player starting position (walls won't spawn here)
        has_upstairs: Whether to place upstairs
        has_downstairs: Whether to place downstairs
        upstairs_pos: Position for upstairs (if None, will be randomly placed)
        downstairs_pos: Position for downstairs (if None, will be randomly placed)
        create_player: Whether to create the player entity (default True)
    """
    # Create floor tile entities for the entire map
    for y in range(map_height):
        for x in range(map_width):
            level.create_entity("floor", x=x, y=y)

    # Create wall entities around the map border
    for x in range(map_width):
        # Top wall
        level.create_entity("wall", x=x, y=0)
        # Bottom wall
        level.create_entity("wall", x=x, y=map_height - 1)

    for y in range(map_height):
        # Left wall
        level.create_entity("wall", x=0, y=y)
        # Right wall
        level.create_entity("wall", x=map_width - 1, y=y)

    # Collect reserved positions (player and stairs)
    reserved_positions = {(player_x, player_y)}

    # Determine stair positions
    if has_upstairs:
        if upstairs_pos is None:
            # Random position for upstairs
            up_x = random.randint(1, map_width - 2)
            up_y = random.randint(1, map_height - 2)
            while (up_x, up_y) in reserved_positions:
                up_x = random.randint(1, map_width - 2)
                up_y = random.randint(1, map_height - 2)
        else:
            up_x, up_y = upstairs_pos
        reserved_positions.add((up_x, up_y))
        level.create_entity("upstairs", x=up_x, y=up_y)

    if has_downstairs:
        if downstairs_pos is None:
            # Random position for downstairs
            down_x = random.randint(1, map_width - 2)
            down_y = random.randint(1, map_height - 2)
            while (down_x, down_y) in reserved_positions:
                down_x = random.randint(1, map_width - 2)
                down_y = random.randint(1, map_height - 2)
        else:
            down_x, down_y = downstairs_pos
        reserved_positions.add((down_x, down_y))
        level.create_entity("downstairs", x=down_x, y=down_y)

    # Create random walls inside the map for testing
    num_random_walls = 100
    for _ in range(num_random_walls):
        # Generate random position inside the map (not on border)
        x = random.randint(1, map_width - 2)
        y = random.randint(1, map_height - 2)

        # Skip reserved positions
        if (x, y) in reserved_positions:
            continue

        level.create_entity("wall", x=x, y=y)

    # Create the player entity (only if requested)
    if create_player:
        level.create_entity("player", x=player_x, y=player_y)
