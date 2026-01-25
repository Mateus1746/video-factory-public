
import sys

def fix_all_indentation(filename):
    print(f"🔧 Fixing ALL Indentation in {filename}...")
    
    with open(filename, "r") as f:
        lines = f.readlines()
        
    new_lines = []
    in_class = False
    in_method = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect Class
        if line.startswith("class MarbleWar"):
            in_class = True
            new_lines.append(line)
            continue
            
        if not in_class:
            new_lines.append(line)
            continue
            
        # Detect Method
        if stripped.startswith("def ") and line.startswith("    def "):
            in_method = True
            new_lines.append(line)
            continue
            
        # If we are in a method, ensure body lines have at least 8 spaces
        if in_method:
            if not stripped: # Empty lines
                new_lines.append(line)
            elif line.startswith("    ") and not line.startswith("        "):
                # It has 4 spaces but needs 8. Fix it.
                new_lines.append("    " + line)
                # print(f"Fixed line {i+1}: {stripped}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    with open(filename, "w") as f:
        f.writelines(new_lines)
        
    print("✅ File rewritten completely.")

if __name__ == "__main__":
    fix_all_indentation("game.py")
