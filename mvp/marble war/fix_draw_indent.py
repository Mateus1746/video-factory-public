
import sys

def fix_draw_indent(filename):
    print(f"🔧 Fixing _draw Indentation in {filename}...")
    
    with open(filename, "r") as f:
        lines = f.readlines()
        
    new_lines = []
    in_draw_block = False
    
    for i, line in enumerate(lines):
        # Start of _draw method (we assume we already fixed the definition line to 4 spaces via replace, 
        # OR we catch it here if it's still 8)
        
        # Actually, let's catch the 8-space definition too just in case.
        if "        def _draw(self)" in line:
            in_draw_block = True
            new_lines.append(line.replace("        def", "    def", 1))
            continue
            
        # Or the 4-space definition if I already fixed it
        if "    def _draw(self)" in line:
            in_draw_block = True
            new_lines.append(line)
            continue
            
        # Stop when we hit the next method (indent 4)
        if in_draw_block and line.strip().startswith("def "):
            in_draw_block = False
            
        if in_draw_block:
            # If line has 12 spaces, make it 8. 
            if line.startswith("            "):
                new_lines.append(line[4:])
            # If line has 8 spaces (and it's not the def), it might be correct or under-indented relative to 12.
            # But in our case, the whole block was shifted right.
            elif line.startswith("        ") and not line.strip() == "":
                 new_lines.append(line) # Keep as is? No, if the def is at 4, body must be at 8.
                 # Wait, the previous replace put body at 12?
                 # Let's assume body is at 12.
                 pass
                 
            # Let's just blindly unindent by 4 spaces if it starts with 8 spaces inside this block
            if line.startswith("        "):
                new_lines.append(line[4:])
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    with open(filename, "w") as f:
        f.writelines(new_lines)
        
    print("✅ File rewritten.")

if __name__ == "__main__":
    fix_draw_indent("game.py")
