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
    # Map dimensions (independent of screen size)
    map_width = 100
    map_height = 55

    # Console/viewport dimensions (what you see on screen)
    console_width = 100
    console_height = 60

    # Set nearest-neighbor filtering for sharp, pixel-perfect rendering
    # CRITICAL: Must be called BEFORE creating the context
    tcod.lib.SDL_SetHint(b"SDL_RENDER_SCALE_QUALITY", b"0")

    # Load bitmap tileset for crisp, pixel-perfect rendering (like NetHack/DCSS)
    # Using pre-rendered bitmap instead of TrueType to avoid scaling artifacts
    tileset = tcod.tileset.load_tilesheet(
        "fonts/dejavu16x16_gs_tc.png",
        columns=32,
        rows=8,
        charmap=tcod.tileset.CHARMAP_TCOD
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
    # Player won't start on level 2, so we don't create a player entity
    generate_map(level_2, map_width, map_height, map_width // 2, map_height // 2, has_upstairs=True, create_player=False)
    world.add_level(level_2)

    # Create the console
    console = tcod.console.Console(console_width, console_height, order="F")

    # Initialize game systems
    initialize_systems(world, console)

    # Create the context (window) - resizable with smooth vector font scaling
    with tcod.context.new(
        columns=console.width,
        rows=console.height,
        tileset=tileset,
        title="Roguelike",
        vsync=True,
        sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE,
    ) as context:
        # Main game loop
        running = True
        while running:
            # Update all frame-based systems (including rendering)
            world.update()

            # Draw UI separator and instructions
            console.print(0, map_height, "-" * console_width, fg=(150, 150, 150))

            # Get current floor for display
            active_level = world.get_active_level()
            floor_text = f"Floor: {active_level.depth}" if active_level else "Floor: ?"

            console.print(0, map_height + 1, f"{floor_text} | ESC: quit | hjkl/yubn: move | <>: stairs", fg=(200, 200, 200))

            # Present the console to the screen with pixel-perfect scaling
            context.present(
                console,
                integer_scaling=True,  # Prevents sub-pixel distortion
                keep_aspect=True,      # Maintains aspect ratio with letterbox
                clear_color=(0, 0, 0)  # Black letterbox borders
            )

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
