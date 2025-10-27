#!/usr/bin/env python3
"""Main entry point for the roguelike game."""
import tcod

from roguelike.world import World
from roguelike.level import Level
from roguelike.systems import RenderSystem, InputSystem, LevelTransitionSystem
from roguelike.map import generate_map


def initialize_systems(world: World, console: tcod.console.Console) -> None:
    """Initialize and add game systems to the world.

    Args:
        world: The ECS world to add systems to
        console: The console for rendering
    """
    input_system = InputSystem()
    level_transition_system = LevelTransitionSystem()
    render_system = RenderSystem(console)
    world.add_system(input_system)
    world.add_system(level_transition_system)
    world.add_system(render_system)


def main():
    # Map dimensions
    map_width = 80
    map_height = 45

    # Screen dimensions
    screen_width = 80
    screen_height = 50

    # Load the tileset
    tileset = tcod.tileset.load_tilesheet(
        "fonts/dejavu10x10_gs_tc.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD
    )

    # Create the ECS world
    world = World()

    # Create the first level (depth 0)
    level_1 = Level(width=map_width, height=map_height, depth=0)
    player_x = map_width // 2
    player_y = map_height // 2
    generate_map(level_1, map_width, map_height, player_x, player_y, has_downstairs=True)
    world.add_level(level_1)

    # Create the second level (depth 1)
    level_2 = Level(width=map_width, height=map_height, depth=1)
    # Player won't start on level 2, so we just need a placeholder position
    generate_map(level_2, map_width, map_height, map_width // 2, map_height // 2, has_upstairs=True)
    world.add_level(level_2)

    # Create the console
    console = tcod.console.Console(screen_width, screen_height, order="F")

    # Initialize game systems
    initialize_systems(world, console)

    # Create the context (window)
    with tcod.context.new(
        columns=console.width,
        rows=console.height,
        tileset=tileset,
        title="Roguelike",
        vsync=True,
    ) as context:
        # Main game loop
        running = True
        while running:
            # Update all frame-based systems (including rendering)
            console.clear()
            world.update()

            # Draw UI separator and instructions
            console.print(0, map_height, "-" * screen_width, fg=(150, 150, 150))
            console.print(0, map_height + 1, "ESC: quit | hjkl: move | <>: stairs", fg=(200, 200, 200))

            # Present the console to the screen
            context.present(console)

            # Handle input
            for event in tcod.event.wait():
                if event.type == "QUIT":
                    running = False
                elif event.type == "KEYDOWN":
                    if event.sym == tcod.event.KeySym.ESCAPE:
                        running = False
                    else:
                        # Pass key event to input systems
                        world.handle_input(event)


if __name__ == "__main__":
    main()
