import os
import pkgutil
import importlib
import inspect
from ..entities.base import Entity

def load_algorithms(package_name='src.entities'):
    """
    Dynamically load all Entity subclasses from the specified package.
    Returns a list of tuples: (Class, Name, Color)
    """
    algorithms = []
    
    # Resolve package path
    # Assuming this is run from the root or similar context
    # package_name is 'src.entities'
    # We need to find the absolute path to src/entities
    
    # Hacky way to find the path relative to THIS file (src/utils/loader.py)
    # src/utils/../entities -> src/entities
    current_dir = os.path.dirname(os.path.abspath(__file__))
    entities_dir = os.path.join(current_dir, '..', 'entities')
    
    if not os.path.exists(entities_dir):
        # Fallback if running from a different context
        # Try to find 'src' in CWD
        if os.path.exists('src/entities'):
            entities_dir = 'src/entities'
    
    # Iterate over modules
    for _, name, _ in pkgutil.iter_modules([entities_dir]):
        if name == 'base' or name == '__init__':
            continue
            
        full_module_name = f"{package_name}.{name}"
        try:
            module = importlib.import_module(full_module_name)
            
            # Inspect module for Entity subclasses
            for member_name, member in inspect.getmembers(module):
                if inspect.isclass(member) and issubclass(member, Entity) and member is not Entity:
                    # Found one!
                    # Logic to determine Name and Color
                    # We can look for class attributes OR default values
                    # For now, we use a mapping or defaults if not present
                    # Or we just return the class and let BattleManager handle metadata
                    
                    # Ideally, Entity classes should have metadata:
                    # class MyAlgo(Entity):
                    #     NAME = "MY ALGO"
                    #     COLOR = (255, 0, 0)
                    
                    # If not present, we fallback to defaults (this allows gradual migration)
                    algo_name = getattr(member, 'NAME', name.upper().replace('_', ' '))
                    algo_color = getattr(member, 'COLOR', (255, 255, 255))
                    
                    algorithms.append((member, algo_name, algo_color))
                    
        except ImportError as e:
            print(f"Failed to load module {full_module_name}: {e}")
            
    return algorithms
