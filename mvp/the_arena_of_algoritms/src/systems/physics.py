import math

class SpatialGrid:
    def __init__(self, width, height, cell_size):
        self.cell_size = cell_size
        self.cols = int(width / cell_size) + 1
        self.rows = int(height / cell_size) + 1
        self.grid = {}

    def _get_cell(self, x, y):
        cx = int(x / self.cell_size)
        cy = int(y / self.cell_size)
        return (cx, cy)

    def clear(self):
        self.grid = {}

    def insert(self, obj, x, y):
        cell = self._get_cell(x, y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(obj)

    def retrieve(self, x, y):
        cell = self._get_cell(x, y)
        # Return objects in current cell + neighbors (3x3)
        objects = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                key = (cell[0] + i, cell[1] + j)
                if key in self.grid:
                    objects.extend(self.grid[key])
        return objects
