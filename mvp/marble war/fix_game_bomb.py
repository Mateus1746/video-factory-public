
import sys

def fix_bomb_block(filename):
    print(f"🔧 Fixing Bomb Block Indentation in {filename}...")
    
    with open(filename, "r") as f:
        lines = f.readlines()
        
    new_lines = []
    in_bomb_block = False
    
    for i, line in enumerate(lines):
        # Start of _update_bomb method
        if "def _update_bomb(self)" in line:
            in_bomb_block = True
            new_lines.append(line)
            continue
            
        # Stop when we hit the next method
        if in_bomb_block and line.strip().startswith("def "):
            in_bomb_block = False
            
        if in_bomb_block:
            # Check if line is under-indented (starts with only 4 spaces but has content)
            if line.startswith("    ") and not line.startswith("        ") and line.strip():
                # Fix: Add 4 spaces
                new_lines.append("    " + line)
                # print(f"Fixed line {i+1}: {line.strip()}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    with open(filename, "w") as f:
        f.writelines(new_lines)
        
    print("✅ File rewritten.")

if __name__ == "__main__":
    fix_bomb_block("game.py")
