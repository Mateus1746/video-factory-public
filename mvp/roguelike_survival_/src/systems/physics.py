import collections

class SpatialHash:
    def __init__(self, cell_size=200):
        self.cell_size = cell_size
        self.grid = collections.defaultdict(list)

    def _get_cell(self, x, y):
        return (int(x // self.cell_size), int(y // self.cell_size))

    def clear(self):
        self.grid.clear()

    def insert(self, entity):
        cell = self._get_cell(entity.pos.x, entity.pos.y)
        self.grid[cell].append(entity)

    def get_nearby(self, x, y, radius):
        """Returns entities in cells overlapping the given circular area."""
        nearby = []
        # Get cell range
        min_c = self._get_cell(x - radius, y - radius)
        max_c = self._get_cell(x + radius, y + radius)
        
        for cx in range(min_c[0], max_c[0] + 1):
            for cy in range(min_c[1], max_c[1] + 1):
                nearby.extend(self.grid[(cx, cy)])
        return nearby
