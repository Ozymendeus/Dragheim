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
        self.db.grid = {}

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
        Create a text-based representation of the grid.
        """
        if not self.db.grid:
            return "The grid is empty."
        # Determine grid size
        max_x = max(k[0] for k in self.db.grid.keys())
        max_y = max(k[1] for k in self.db.grid.keys())
        output = ""
        for y in range(max_y, -1, -1):
            row = ""
            for x in range(max_x + 1):
                cell = self.db.grid.get((x, y), " ")  # Default to empty cell
                row += f"[{cell}]"
            output += f"{row}\n"
        return output