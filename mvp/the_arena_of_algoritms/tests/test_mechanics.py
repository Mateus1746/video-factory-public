import unittest
import math
from src.systems.physics import SpatialGrid
from src.entities.base import Entity, Ring

class TestPhysics(unittest.TestCase):
    def test_grid_insertion(self):
        grid = SpatialGrid(1000, 1000, 100)
        obj = "entity"
        grid.insert(obj, 50, 50)
        
        retrieved = grid.retrieve(50, 50)
        self.assertIn(obj, retrieved)
        
        # Check neighbor retrieval
        retrieved_near = grid.retrieve(10, 10) # Same cell
        self.assertIn(obj, retrieved_near)
        
        # Check far
        retrieved_far = grid.retrieve(900, 900)
        self.assertNotIn(obj, retrieved_far)

class TestRingMechanics(unittest.TestCase):
    def test_damage(self):
        ring = Ring(100, 1000, (0,0), (255,255,255))
        ring.take_damage(100)
        self.assertEqual(ring.hp, 900)
        
    def test_death(self):
        ring = Ring(100, 10, (0,0), (255,255,255))
        ring.take_damage(20)
        self.assertEqual(ring.hp, 0)
        self.assertFalse(ring.alive)

if __name__ == '__main__':
    unittest.main()
