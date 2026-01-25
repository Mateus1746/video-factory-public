import sys

def fix_run_tail(filename):
    print(f"🔧 Fixing tail of run() in {filename}...")
    
    with open(filename, "r") as f:
        lines = f.readlines()
        
    new_lines = []
    in_run = False
    
    for i, line in enumerate(lines):
        if "def run(self)" in line:
            in_run = True
            new_lines.append(line)
            continue
            
        if in_run:
            if "def _save_audio_log(self)" in line:
                in_run = False
                new_lines.append(line)
                continue
                
            # If we see the unindented calls at the end of run
            if line.strip().startswith("self._save_audio_log()") or line.strip().startswith("# Save audio log") or line.strip().startswith("print(\"Simulation complete!\")") or line.strip().startswith("pygame.quit()"):
                # If it has 4 spaces, make it 8
                if line.startswith("    ") and not line.startswith("        "):
                    new_lines.append("    " + line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    with open(filename, "w") as f:
        f.writelines(new_lines)
        
    print("✅ File rewritten.")

if __name__ == "__main__":
    fix_run_tail("game.py")
