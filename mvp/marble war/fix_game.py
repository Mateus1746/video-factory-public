import sys

def fix_indentation(filename):
    print(f"🔧 Fixing indentation in {filename}...")
    
    with open(filename, "r") as f:
        lines = f.readlines()
        
    new_lines = []
    indenting = False
    
    # Target: methods that should be inside MarbleWar class but are global.
    # In the NEW version with Themes, the first method after __init__ is still _create_walls.
    
    for line in lines:
        # Check if we hit the start of the broken block
        if line.startswith("def _create_walls(self)"):
            indenting = True
            print("   -> Found start of broken block at: " + line.strip())
            
        if indenting:
            if line.strip(): # If not empty
                new_lines.append("    " + line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    with open(filename, "w") as f:
        f.writelines(new_lines)
        
    print("✅ File rewritten.")

if __name__ == "__main__":
    fix_indentation("game.py")