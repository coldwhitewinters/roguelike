#!/usr/bin/env python3
"""Main entry point for the roguelike game."""
import random
import tcod

from src.ecs import World
from src.templates import EntityTemplateManager
from src.systems import RenderSystem, InputSystem


def main():
    # Map dimensions
    map_width = 80
    map_height = 45

    # Screen dimensions
    screen_width = 80
    screen_height = 50

    # Load the tileset
    tileset = tcod.tileset.load_tilesheet(
        "data/dejavu10x10_gs_tc.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD
    )

    # Load entity templates
    template_manager = EntityTemplateManager()
    template_manager.load_templates("data/entities.yaml")

    # Create the ECS world with template manager
    world = World(template_manager=template_manager)

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
        if x == map_width // 2 and y == map_height // 2:
            continue

        world.create_entity("wall", x=x, y=y)

    # Create the player entity
    world.create_entity("player", x=map_width // 2, y=map_height // 2)

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
