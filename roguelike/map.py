"""Map generation dispatcher for procedural environments."""
import random
from roguelike.level import Level
from roguelike.mapgen.dungeon import generate_dungeon
from roguelike.mapgen.forest import generate_forest
from roguelike.mapgen.village import generate_village


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
    create_player: bool = True,
    environment: str | None = None,
    dungeon_algorithm: str = "rooms_corridors",
) -> None:
    """Generate a map with procedural environment generation.

    Args:
        level: The level to populate with map entities
        map_width: Width of the map in tiles
        map_height: Height of the map in tiles
        player_x: X coordinate for player starting position
        player_y: Y coordinate for player starting position
        has_upstairs: Whether to place upstairs
        has_downstairs: Whether to place downstairs
        upstairs_pos: Position for upstairs (currently ignored - placed randomly)
        downstairs_pos: Position for downstairs (currently ignored - placed randomly)
        create_player: Whether to create the player entity (default True)
        environment: Environment type ("dungeon", "forest", "village") or None for random
        dungeon_algorithm: Algorithm for dungeon generation ("rooms_corridors", "cellular", "bsp")
    """
    # Choose random environment if not specified
    if environment is None:
        environment = random.choice(["forest", "dungeon", "village"])

    # Dispatch to appropriate generator
    if environment == "dungeon":
        generate_dungeon(
            level,
            map_width,
            map_height,
            player_x,
            player_y,
            algorithm=dungeon_algorithm,
            has_upstairs=has_upstairs,
            has_downstairs=has_downstairs,
            create_player=create_player,
        )

    elif environment == "forest":
        generate_forest(
            level,
            map_width,
            map_height,
            player_x,
            player_y,
            has_upstairs=has_upstairs,
            has_downstairs=has_downstairs,
            create_player=create_player,
        )

    elif environment == "village":
        generate_village(
            level,
            map_width,
            map_height,
            player_x,
            player_y,
            has_upstairs=has_upstairs,
            has_downstairs=has_downstairs,
            create_player=create_player,
        )

    else:
        raise ValueError(f"Unknown environment type: {environment}")
