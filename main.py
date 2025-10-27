#!/usr/bin/env python3
"""Main entry point for the roguelike game."""
import tcod

from src.world import World
from src.systems import RenderSystem, InputSystem
from src.map_generation import generate_map


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

    # Generate the map with floor tiles, walls, and player
    player_x = map_width // 2
    player_y = map_height // 2
    generate_map(world, map_width, map_height, player_x, player_y)

    # Create the console
    console = tcod.console.Console(screen_width, screen_height, order="F")

    # Create and add systems
    input_system = InputSystem(map_width, map_height)
    render_system = RenderSystem(console)
    world.add_system(input_system)
    world.add_system(render_system)

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
            # Render
            console.clear()
            render_system.update(world)

            # Draw UI separator and instructions
            console.print(0, map_height, "-" * screen_width, fg=(150, 150, 150))
            console.print(0, map_height + 1, "Press ESC to quit | hjkl to move", fg=(200, 200, 200))

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
                        # Pass key event to input system
                        input_system.update(world, event)


if __name__ == "__main__":
    main()
