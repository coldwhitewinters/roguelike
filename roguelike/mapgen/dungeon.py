"""Dungeon environment generators with multiple algorithms."""
import random
from typing import TYPE_CHECKING

from roguelike.mapgen.base import MapGenerator, place_stairs_and_player

if TYPE_CHECKING:
    from roguelike.level import Level


class Room:
    """Rectangular room in a dungeon."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize a room.

        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            width: Room width in tiles
            height: Room height in tiles
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self) -> tuple[int, int]:
        """Get the center coordinates of the room.

        Returns:
            Tuple of (center_x, center_y)
        """
        return (self.x + self.width // 2, self.y + self.height // 2)

    def intersects(self, other: "Room", buffer: int = 1) -> bool:
        """Check if this room intersects another room.

        Args:
            other: Another Room instance
            buffer: Minimum distance between rooms (default 1)

        Returns:
            True if rooms intersect (including buffer), False otherwise
        """
        return not (
            self.x + self.width + buffer <= other.x
            or other.x + other.width + buffer <= self.x
            or self.y + self.height + buffer <= other.y
            or other.y + other.height + buffer <= self.y
        )


class RoomsCorridorsGenerator(MapGenerator):
    """Classic roguelike dungeon with rooms connected by corridors."""

    def __init__(self, level: "Level", width: int, height: int):
        """Initialize the rooms & corridors generator.

        Args:
            level: The level to populate
            width: Map width
            height: Map height
        """
        super().__init__(level, width, height)
        self.rooms: list[Room] = []

    def create_room(self, room: Room) -> None:
        """Carve out a room in the terrain grid.

        Args:
            room: Room to create
        """
        # Fill room interior with floor
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.set_tile(x, y, "floor")

    def try_place_room(self, min_size: int = 4, max_size: int = 12) -> bool:
        """Try to place a random room that doesn't intersect existing rooms.

        Args:
            min_size: Minimum room dimension
            max_size: Maximum room dimension

        Returns:
            True if room was placed, False otherwise
        """
        # Random room size
        width = random.randint(min_size, max_size)
        height = random.randint(min_size, max_size - 2)  # Slightly less tall

        # Random position (must be within bounds)
        x = random.randint(1, self.width - width - 2)
        y = random.randint(1, self.height - height - 2)

        # Create room
        new_room = Room(x, y, width, height)

        # Check if it intersects any existing room
        for room in self.rooms:
            if new_room.intersects(room, buffer=1):
                return False

        # Room is valid, add it
        self.create_room(new_room)
        self.rooms.append(new_room)
        return True

    def connect_rooms(self, room1: Room, room2: Room) -> None:
        """Connect two rooms with an L-shaped corridor.

        Args:
            room1: First room
            room2: Second room
        """
        x1, y1 = room1.center()
        x2, y2 = room2.center()
        self.carve_corridor(x1, y1, x2, y2)

    def build_minimum_spanning_tree(self) -> list[tuple[int, int]]:
        """Build a minimum spanning tree of room connections.

        Returns:
            List of (room1_index, room2_index) tuples representing connections
        """
        if len(self.rooms) < 2:
            return []

        # Simple greedy MST using Prim's algorithm
        connected = {0}  # Start with first room
        connections = []

        while len(connected) < len(self.rooms):
            best_dist = float("inf")
            best_pair = None

            # Find closest unconnected room to any connected room
            for i in connected:
                for j in range(len(self.rooms)):
                    if j not in connected:
                        x1, y1 = self.rooms[i].center()
                        x2, y2 = self.rooms[j].center()
                        dist = abs(x1 - x2) + abs(y1 - y2)  # Manhattan distance

                        if dist < best_dist:
                            best_dist = dist
                            best_pair = (i, j)

            if best_pair:
                connections.append(best_pair)
                connected.add(best_pair[1])

        return connections


class CellularAutomataGenerator(MapGenerator):
    """Cave-like dungeon using cellular automata (4-5 rule)."""

    def initialize_random(self, wall_probability: float = 0.45) -> None:
        """Initialize the grid with random walls.

        Args:
            wall_probability: Probability of a tile being a wall (0.0 to 1.0)
        """
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if random.random() < wall_probability:
                    self.set_tile(x, y, "wall")
                else:
                    self.set_tile(x, y, "floor")

    def ca_iteration(self) -> None:
        """Perform one cellular automata iteration using the 4-5 rule.

        If a tile has >= 5 wall neighbors, it becomes a wall.
        Otherwise, it becomes a floor.
        """
        new_grid = [row[:] for row in self.terrain_grid]

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Count wall neighbors in 3x3 area (including self)
                wall_count = sum(
                    1
                    for dy in [-1, 0, 1]
                    for dx in [-1, 0, 1]
                    if self.get_tile(x + dx, y + dy) == "wall"
                )

                # Apply 4-5 rule
                if wall_count >= 5:
                    new_grid[y][x] = "wall"
                else:
                    new_grid[y][x] = "floor"

        self.terrain_grid = new_grid

    def ensure_connectivity(self) -> None:
        """Connect all disconnected regions with corridors.

        Finds the largest connected region and connects all other regions to it.
        """
        # Find all floor positions
        floor_positions = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if not self.is_blocked(x, y)
        ]

        if not floor_positions:
            return

        # Find main (largest) connected region using flood fill
        visited_global = set()
        regions = []

        for pos in floor_positions:
            if pos not in visited_global:
                region = self.flood_fill(pos[0], pos[1])
                visited_global.update(region)
                regions.append(region)

        if len(regions) <= 1:
            return  # Already connected

        # Sort by size, largest first
        regions.sort(key=len, reverse=True)
        main_region = regions[0]

        # Connect each smaller region to main region
        for region in regions[1:]:
            # Find closest points between this region and main region
            best_dist = float("inf")
            best_pair = None

            for pos1 in region:
                for pos2 in main_region:
                    dist = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                    if dist < best_dist:
                        best_dist = dist
                        best_pair = (pos1, pos2)

            if best_pair:
                # Carve 2-tile wide corridor to connect
                self.carve_corridor(best_pair[0][0], best_pair[0][1], best_pair[1][0], best_pair[1][1], width=2)


class BSPNode:
    """Node in a Binary Space Partition tree."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize a BSP node.

        Args:
            x: Top-left X coordinate
            y: Top-left Y coordinate
            width: Node width
            height: Node height
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left: BSPNode | None = None
        self.right: BSPNode | None = None
        self.room: Room | None = None


class BSPGenerator(MapGenerator):
    """BSP tree-based dungeon generator with structured layout."""

    def __init__(self, level: "Level", width: int, height: int):
        """Initialize the BSP generator.

        Args:
            level: The level to populate
            width: Map width
            height: Map height
        """
        super().__init__(level, width, height)
        self.root = BSPNode(1, 1, width - 2, height - 2)
        self.rooms: list[Room] = []

    def split_node(self, node: BSPNode, min_size: int = 8) -> bool:
        """Recursively split a BSP node.

        Args:
            node: Node to split
            min_size: Minimum dimension for a node

        Returns:
            True if split was successful, False otherwise
        """
        # Check if node is too small to split
        if node.width < min_size * 2 and node.height < min_size * 2:
            return False

        # Determine split direction
        split_horizontal = None
        if node.width < min_size * 2:
            split_horizontal = True
        elif node.height < min_size * 2:
            split_horizontal = False
        else:
            # Random choice
            split_horizontal = random.choice([True, False])

        # Perform the split
        if split_horizontal:
            # Split horizontally (top and bottom)
            split_pos = random.randint(min_size, node.height - min_size)
            node.left = BSPNode(node.x, node.y, node.width, split_pos)
            node.right = BSPNode(node.x, node.y + split_pos, node.width, node.height - split_pos)
        else:
            # Split vertically (left and right)
            split_pos = random.randint(min_size, node.width - min_size)
            node.left = BSPNode(node.x, node.y, split_pos, node.height)
            node.right = BSPNode(node.x + split_pos, node.y, node.width - split_pos, node.height)

        return True

    def split_tree(self, node: BSPNode, depth: int = 0, max_depth: int = 4) -> None:
        """Recursively split the BSP tree.

        Args:
            node: Current node to split
            depth: Current recursion depth
            max_depth: Maximum recursion depth
        """
        if depth >= max_depth:
            return

        if self.split_node(node):
            if node.left:
                self.split_tree(node.left, depth + 1, max_depth)
            if node.right:
                self.split_tree(node.right, depth + 1, max_depth)

    def create_rooms_in_leaves(self, node: BSPNode) -> None:
        """Create rooms in leaf nodes of the BSP tree.

        Args:
            node: Current node to process
        """
        if node.left or node.right:
            # Not a leaf, recurse
            if node.left:
                self.create_rooms_in_leaves(node.left)
            if node.right:
                self.create_rooms_in_leaves(node.right)
        else:
            # Leaf node - create a room
            # Room should be smaller than the node (60-90% of node size)
            room_width = random.randint(int(node.width * 0.6), int(node.width * 0.9))
            room_height = random.randint(int(node.height * 0.6), int(node.height * 0.9))

            # Center the room within the node
            room_x = node.x + (node.width - room_width) // 2
            room_y = node.y + (node.height - room_height) // 2

            room = Room(room_x, room_y, room_width, room_height)
            node.room = room
            self.rooms.append(room)

            # Carve the room
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.set_tile(x, y, "floor")

    def connect_siblings(self, node: BSPNode) -> None:
        """Connect sibling rooms with corridors.

        Args:
            node: Current node to process
        """
        if node.left and node.right:
            # Get rooms from left and right subtrees
            left_room = self.get_room_from_tree(node.left)
            right_room = self.get_room_from_tree(node.right)

            if left_room and right_room:
                # Connect the rooms
                x1, y1 = left_room.center()
                x2, y2 = right_room.center()
                self.carve_corridor(x1, y1, x2, y2, width=random.randint(1, 2))

            # Recurse
            self.connect_siblings(node.left)
            self.connect_siblings(node.right)

    def get_room_from_tree(self, node: BSPNode) -> Room | None:
        """Get a room from a BSP subtree.

        Args:
            node: Root of subtree

        Returns:
            A room from the subtree, or None if none exists
        """
        if node.room:
            return node.room
        if node.left:
            left_room = self.get_room_from_tree(node.left)
            if left_room:
                return left_room
        if node.right:
            right_room = self.get_room_from_tree(node.right)
            if right_room:
                return right_room
        return None


def generate_dungeon(
    level: "Level",
    width: int,
    height: int,
    player_x: int,
    player_y: int,
    algorithm: str = "rooms_corridors",
    has_upstairs: bool = False,
    has_downstairs: bool = False,
    create_player: bool = True,
) -> None:
    """Generate a dungeon using the specified algorithm.

    Args:
        level: The level to populate
        width: Map width in tiles
        height: Map height in tiles
        player_x: Preferred player X position
        player_y: Preferred player Y position
        algorithm: Generation algorithm: "rooms_corridors", "cellular", or "bsp"
        has_upstairs: Whether to place upstairs
        has_downstairs: Whether to place downstairs
        create_player: Whether to place player entity
    """
    if algorithm == "rooms_corridors":
        # Initialize generator
        gen = RoomsCorridorsGenerator(level, width, height)

        # Fill with walls initially
        for y in range(height):
            for x in range(width):
                gen.set_tile(x, y, "wall")

        # Try to place 15-25 rooms
        num_rooms_target = random.randint(15, 25)
        attempts = 0
        max_attempts = num_rooms_target * 3  # More attempts to reach target

        while len(gen.rooms) < num_rooms_target and attempts < max_attempts:
            gen.try_place_room(min_size=4, max_size=12)
            attempts += 1

        # Connect rooms using MST
        if len(gen.rooms) >= 2:
            connections = gen.build_minimum_spanning_tree()

            # Connect rooms along MST
            for i, j in connections:
                gen.connect_rooms(gen.rooms[i], gen.rooms[j])

            # Add some extra connections for loops (20% of MST connections)
            num_extra = max(1, len(connections) // 5)
            for _ in range(num_extra):
                i = random.randint(0, len(gen.rooms) - 1)
                j = random.randint(0, len(gen.rooms) - 1)
                if i != j:
                    gen.connect_rooms(gen.rooms[i], gen.rooms[j])

        # Add border walls (already walls, but ensure consistency)
        gen.add_border_walls()

        # Create entities from terrain grid
        gen.create_entities()

        # Place stairs and player
        place_stairs_and_player(gen, player_x, player_y, has_upstairs, has_downstairs, create_player)

    elif algorithm == "cellular":
        # Initialize generator
        gen = CellularAutomataGenerator(level, width, height)

        # Fill with walls initially
        for y in range(height):
            for x in range(width):
                gen.set_tile(x, y, "wall")

        # Initialize with random walls/floors (45% walls)
        gen.initialize_random(wall_probability=0.45)

        # Run cellular automata iterations (4-5 times)
        num_iterations = random.randint(4, 5)
        for _ in range(num_iterations):
            gen.ca_iteration()

        # Ensure all regions are connected
        gen.ensure_connectivity()

        # Add border walls
        gen.add_border_walls()

        # Create entities from terrain grid
        gen.create_entities()

        # Place stairs and player
        place_stairs_and_player(gen, player_x, player_y, has_upstairs, has_downstairs, create_player)

    elif algorithm == "bsp":
        # Initialize generator
        gen = BSPGenerator(level, width, height)

        # Fill with walls initially
        for y in range(height):
            for x in range(width):
                gen.set_tile(x, y, "wall")

        # Split the BSP tree
        gen.split_tree(gen.root, depth=0, max_depth=4)

        # Create rooms in leaf nodes
        gen.create_rooms_in_leaves(gen.root)

        # Connect sibling rooms
        gen.connect_siblings(gen.root)

        # Add border walls
        gen.add_border_walls()

        # Create entities from terrain grid
        gen.create_entities()

        # Place stairs and player
        place_stairs_and_player(gen, player_x, player_y, has_upstairs, has_downstairs, create_player)

    else:
        raise ValueError(f"Unknown dungeon algorithm: {algorithm}")
