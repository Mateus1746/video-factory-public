import json
import os

class StyleManager:
    def __init__(self):
        # The Grand Registry of 22 Visuals
        self.styles = [
            # --- Pygame Engines (3) ---
            {"type": "pygame", "name": "neon"},
            {"type": "pygame", "name": "zen"},
            {"type": "pygame", "name": "glitch"},
            
            # --- Matplotlib Engines (19) ---
            {"type": "matplotlib", "name": "arch"},
            {"type": "matplotlib", "name": "choreographer"},
            {"type": "matplotlib", "name": "cymatics"},
            {"type": "matplotlib", "name": "drone_show"},
            {"type": "matplotlib", "name": "drone_show1"},
            {"type": "matplotlib", "name": "ferrofluid"},
            {"type": "matplotlib", "name": "galactic_singularity"},
            {"type": "matplotlib", "name": "harmonic_flow"},
            {"type": "matplotlib", "name": "living_fluid"},
            {"type": "matplotlib", "name": "mandelbrot"},
            {"type": "matplotlib", "name": "precise_singularity"},
            {"type": "matplotlib", "name": "production_master"},
            {"type": "matplotlib", "name": "radiant_grid"},
            {"type": "matplotlib", "name": "shader_city_fluid"},
            {"type": "matplotlib", "name": "shader_city_real"},
            {"type": "matplotlib", "name": "slime_mold"},
            {"type": "matplotlib", "name": "spectrum"},
            {"type": "matplotlib", "name": "vortex"},
            {"type": "matplotlib", "name": "wormhole"}
        ]
        
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.state_file = os.path.join(self.data_dir, 'style_rotation.json')
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_next_style(self):
        """Returns the next style dict and updates the rotation index using a shuffled pool."""
        import random
        pool = []
        
        # Load state
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    pool = data.get('pool', [])
            except:
                pass
        
        # Refill and shuffle if pool is empty
        if not pool:
            print("🎲 Pool exhausted! Refilling and shuffling all 22 styles.")
            pool = list(range(len(self.styles)))
            random.shuffle(pool)
            
        # Pick the next index from pool
        style_index = pool.pop(0)
        selected_style = self.styles[style_index]
        
        # Save state
        with open(self.state_file, 'w') as f:
            json.dump({'pool': pool, 'last_style': selected_style['name']}, f)
            
        remaining = len(pool)
        total = len(self.styles)
        print(f"🔄 Style Rotation: [{total - remaining}/{total}] -> {selected_style['name'].upper()} ({selected_style['type']})")
        
        return selected_style
