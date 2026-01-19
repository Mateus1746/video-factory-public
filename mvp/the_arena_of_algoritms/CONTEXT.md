# PROJECT CONTEXT - Algorithm Battle

## Tech Stack
- **Language**: Python 3.13
- **Library**: Pygame 2.6.1, NumPy (Áudio), FFmpeg (Vídeo)
- **Management**: uv
- **Resolution**: 1080x1920 (Vertical 9:16) @ 60 FPS

## Project Structure
- `main.py`: Core simulation logic, entities, and frame exporter.
- `config.py`: Constants, colors, and balance settings.
- `render_preview.py`: Assembly script for 720p 30 FPS.
- `render_final.py`: Assembly script for 1080p 60 FPS.
- `frames/`: Temporary storage for raw frames (PNG).

## Core Mechanics
### 1. Rings (Shared Environment)
- 4 concentric rings with exponential HP: 1k, 10k, 100k, 1M.
- Rings are removed when HP <= 0.
- Innermost ring is the active target.

### 2. Fibonacci Algorithm (Top)
- **Concept**: Golden Spiral / Archimedean Spiral.
- **Movement**: Procedural via polar coordinates (`angle`, `radius`).
- **Damage**: High continuous DPS on contact (scraping).
- **Physics**: Non-Newtonian.

### 3. Spawner Algorithm (Bottom)
- **Concept**: Swarm / Chaos physics.
- **Entities**: Multiple balls with vector velocity.
- **Movement**: Bouncing/Reflection on ring boundaries.
- **Damage**: Discrete impact damage per collision.
- **Spawner**: Periodic creation of new balls.

## Business Rules / Variables
- `RING_HP`: [1000, 10000, 100000, 1000000]
- `RING_RADII`: [100, 180, 260, 340]
- `SPIRAL_DPS`: 5000 (Damage/sec)
- `BALL_DAMAGE`: 50 (Damage/impact)
- `MAX_BALLS`: 100

## Idea Graveyard & Future expansion (Bibliotecário)
1. **Dynamic Backgrounds**: Neon grids that react to the music beats.
2. **More Algorithms**:
    - "Primes": Entities that split into smaller ones when hitting a wall.
    - "Sorting": Horizontal barriers that are destroyed in order of value.
3. **Audio-Reactive Rings**: Rings that pulse or change thickness based on the piano note frequency.
4. **Camera Shake**: Subtle screen shake when a ring is finaly destroyed.
5. **Multiple Swarms**: Different types of balls with different physics (gravity, attraction).
