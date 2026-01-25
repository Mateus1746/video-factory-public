import unittest
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation import Simulation
from config import *

class TestVelocityOddsSimulation(unittest.TestCase):
    def setUp(self):
        self.sim = Simulation()

    def test_initialization(self):
        self.assertEqual(len(self.sim.players), 2)
        self.assertFalse(self.sim.game_over)
        self.assertIsNone(self.sim.winner_player)

    def test_update_no_error(self):
        # Test a few frames of update
        dt = 1/60
        for _ in range(10):
            self.sim.update(dt)
        self.assertFalse(self.sim.game_over)

    def test_reset(self):
        self.sim.players[0].money = 0
        self.sim.reset()
        self.assertEqual(self.sim.players[0].money, STARTING_MONEY)

    def test_player_collision_logic(self):
        # Manually move player to outer boundary of first ring
        p = self.sim.players[0]
        ring = RINGS_CONFIG[0]
        p.pos_x = ring["radius"]
        p.pos_y = 0
        
        # Update should trigger collision check
        self.sim.check_player_collision(p, 0)
        # Should either level up or bounce (depending on random angle in setUp)
        self.assertTrue(p.current_ring_index > 0 or p.vel_x != 0)

if __name__ == '__main__':
    unittest.main()
