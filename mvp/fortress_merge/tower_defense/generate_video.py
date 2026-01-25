"""
Tower Defense - Video Generator Wrapper
Calls main.py with appropriate arguments for batch generation.
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main
from main import main

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output_render.mp4"
    
    # Ensure output is in current directory for batch_pipeline compatibility
    if not os.path.isabs(output_file):
        output_file = os.path.join(os.getcwd(), output_file)
    
    main(output_file)
