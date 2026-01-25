import sys

def fix_game_final(filename):
    print(f"🔧 Fixing indentation for 'assassin_mode' block in {filename}...")
    
    with open(filename, "r") as f:
        lines = f.readlines()
        
    new_lines = []
    
    for line in lines:
        # Target the specific broken if statement
        if line.startswith("    if marble.assassin_mode and self.assets.weapon_img:"):
            print("   -> Found broken if statement. Indenting.")
            new_lines.append("        " + line.strip() + "\n")
        elif line.startswith("    self._draw_marble_weapon(marble, look_angle, pos)"):
            # This line follows the if, so it needs to be indented to 12 spaces
            print("   -> Found broken body. Indenting.")
            new_lines.append("            " + line.strip() + "\n")
        else:
            new_lines.append(line)
            
    with open(filename, "w") as f:
        f.writelines(new_lines)
        
    print("✅ File rewritten.")

if __name__ == "__main__":
    fix_game_final("game.py")
