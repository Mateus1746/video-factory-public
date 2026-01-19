"""
The Arena of Algorithms - Video Generator
Wrapper that calls run_simulation_headless.py in headless mode.
"""
import os
import sys

# Force headless before imports
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["HEADLESS"] = "true"

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
if __name__ == "__main__":
    import run_simulation_headless
    # Explicitly run the simulation function
    run_simulation_headless.run_single_simulation()

