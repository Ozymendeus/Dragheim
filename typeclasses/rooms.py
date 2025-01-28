import math
"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    pass

class GridRoom(DefaultRoom):
    """
    A room with a grid-based map for visual navigation.
    """
    def at_object_creation(self):
        super().at_object_creation()
        if not self.db.grid:
            self.db.grid = {}  # Initialize the grid
        if not self.db.doors:
            self.db.doors = {}  # Initialize the doors

    def add_door(self, direction, grid_position, destination):
        """
        Add a door to the room, linking it to a grid position and a room exit.
        
        Args:
            direction (str): The direction of the door (e.g., "north", "up", "southwest").
            grid_position (tuple): The (x, y) position of the door in the grid.
            destination (str): The key or location of the destination room.
        """
        # Limit doors to 10 max
        if len(self.db.doors) >= 10:
            raise ValueError("Maximum number of doors (10) reached.")

        # Ensure the direction is valid
        valid_directions = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down"]
        if direction not in valid_directions:
            raise ValueError(f"Invalid direction: {direction}. Valid directions are: {', '.join(valid_directions)}.")

        # Add the door
        self.db.doors[direction] = {
            "grid_position": grid_position,
            "destination": destination
        }

        # Create the Evennia room exit
        self.create_exit(direction, destination)

    def create_exit(self, direction, destination):
        """
        Create a room exit in the given direction.
        
        Args:
            direction (str): The direction for the exit (e.g., "north").
            destination (str): The key or location of the destination room.
        """
        from evennia.utils import create
        if not self.exits.get(direction):
            create.create_object(
                "typeclasses.exits.Exit",  # Use the default Exit typeclass
                key=direction,
                location=self,
                destination=destination
            )

    def set_grid_cell(self, x, y, content):
        """
        Set the content of a specific grid cell.
        """
        if (x, y) not in self.db.grid:
            self.db.grid[(x, y)] = content
        else:
            self.db.grid[(x, y)] = content

    def get_grid_cell(self, x, y):
        """
        Get the content of a specific grid cell.
        """
        return self.db.grid.get((x, y), None)

    def render_grid(self):
        """
        Create a text-based representation of the grid, showing doors.
        """
        if not self.db.grid:
            return "The grid is empty."

        # Get the max grid size
        max_x = max(k[0] for k in self.db.grid.keys())
        max_y = max(k[1] for k in self.db.grid.keys())

        # Add doors to the grid for rendering
        door_positions = {v["grid_position"]: k.upper()[0] for k, v in self.db.doors.items()}

        output = ""
        for y in range(max_y, -1, -1):
            row = ""
            for x in range(max_x + 1):
                cell = self.db.grid.get((x, y), " ")  # Default to an empty space
                if (x, y) in door_positions:
                    row += f"{door_positions[(x, y)]}"  # Show the door (e.g., "N" for north)
                else:
                    row += f"{cell}"
            output += f"{row}\n"
        return output

    
    def auto_build_grid(self, width, height):
        """
        Automatically generate a grid of the specified size.
        Unwalkable spaces are marked as `#` (edges) and walkable as `.` (interior).
        """
        grid = {}
        for y in range(height):
            for x in range(width):
                # Use '#' for the edges and '.' for interior cells
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    grid[(x, y)] = "#"
                else:
                    grid[(x, y)] = "."
        self.db.grid = grid

    def build_circle(self, radius):
        """
        Generate a circular layout with a given radius.
        The circle is centered and has a tight, uniform shape.
        """
        grid = {}
        center = radius  # The center of the circle (offset for grid coordinates)

        for y in range(2 * radius + 1):  # Height of the grid
            for x in range(2 * radius + 1):  # Width of the grid
                # Calculate distance from the center
                distance = math.sqrt((x - center)**2 + (y - center)**2)
                if distance <= radius:
                    grid[(x, y)] = "."  # Walkable space
                else:
                    grid[(x, y)] = "#"  # Unwalkable space
        self.db.grid = grid

    def build_l_shape(self, width, height, leg_length):
        """
        Generate an L-shaped layout with the specified dimensions.

        Args:
            width (int): The width of the horizontal hallway.
            height (int): The height of the vertical hallway.
            leg_length (int): The length of the intersecting "L" part.
        """
        grid = {}

        # Create horizontal hallway (top of the "L")
        for y in range(height):
            for x in range(width):
                grid[(x, y)] = "."

        # Create vertical hallway (left of the "L")
        for y in range(height):
            for x in range(leg_length):
                grid[(x, y)] = "."

        # Fill the rest of the grid with walls
        max_x = max(k[0] for k in grid.keys())
        max_y = max(k[1] for k in grid.keys())
        for y in range(max_y + 1):
            for x in range(max_x + 1):
                if (x, y) not in grid:
                    grid[(x, y)] = "#"

        self.db.grid = grid

    def build_custom_floorplan(self, floorplan):
        """
        Generate a layout based on a list of strings.
        Each character represents a cell (e.g., "#" for wall, "." for walkable).
        Example:
            floorplan = [
                "#####",
                "#...#",
                "##..#",
                "#####"
            ]
        """
        grid = {}
        for y, row in enumerate(reversed(floorplan)):  # Reverse to start from bottom-left
            for x, cell in enumerate(row):
                grid[(x, y)] = cell
        self.db.grid = grid

        
    def reset_grid(self, width, height):
        """
        Clear and regenerate the grid with the specified dimensions.
        """
        self.db.grid = {}  # Clear the existing grid
        for y in range(height):
            for x in range(width):
                # '#' for edges, '.' for walkable spaces
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    self.db.grid[(x, y)] = "#"
                else:
                    self.db.grid[(x, y)] = "."
        return f"The grid has been reset to {width}x{height}."
    
    def return_appearance(self, looker):
        """
        Override the default appearance to include the grid.
        """
        description = super().return_appearance(looker)
        grid_view = self.render_grid()
        return f"{description}\n\n{grid_view}"