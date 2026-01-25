import sys

def deep_analyze(filename):
    print(f"🕵️ Deep Analysis of: {filename}")
    
    with open(filename, "r") as f:
        lines = f.readlines()
        
    class_def_found = False
    class_indent = 0
    current_method = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped: continue
        
        # Detect Class Start
        if line.startswith("class MarbleWar"):
            class_def_found = True
            print(f"✅ Class defined at line {i+1}")
            continue
            
        if not class_def_found: continue
        
        indent = len(line) - len(line.lstrip())
        
        # Detect Method Start
        if stripped.startswith("def "):
            current_method = stripped
            print(f"   🔹 Method defined at line {i+1}: {stripped} (Indent: {indent})")
            if indent == 0:
                print("      ❌ CRITICAL: Method defined at root level (0 indent)!")
            continue
            
        # Detect Loose Code in Class Body (Indent 4 usually)
        # We look for statements using 'self.' which MUST be inside a method (Indent >= 8)
        if "self." in stripped and indent <= 4:
            print(f"   ❌ SUSPICIOUS CODE at line {i+1}: {stripped}")
            print(f"      -> Usage of 'self' at indent level {indent}. Should be inside a method (level 8+).")
            # Show context
            print(f"      -> Context: Last seen method was '{current_method}'")
            return # Stop at first error to fix it

if __name__ == "__main__":
    deep_analyze("game.py")