import pygame

# Cache for glow surfaces to avoid creating them every frame
_glow_cache = {}

def draw_glow(surface, color, pos, radius):
    """Draws a simulated glow effect using pre-rendered cached surfaces."""
    if radius <= 0: return
    
    # Create a key for the cache based on color and radius
    # We round radius to avoid too many cache entries for minor differences
    r = int(radius * 2.5)
    cache_key = (color, r)
    
    if cache_key not in _glow_cache:
        glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA).convert_alpha()
        # Outer soft glow
        pygame.draw.circle(glow_surf, (*color, 30), (r, r), r)
        # Inner brighter glow
        pygame.draw.circle(glow_surf, (*color, 60), (r, r), int(r * 0.6))
        _glow_cache[cache_key] = glow_surf
    
    glow_surf = _glow_cache[cache_key]
    rect = glow_surf.get_rect(center=(int(pos[0]), int(pos[1])))
    surface.blit(glow_surf, rect, special_flags=pygame.BLEND_ADD)

def clear_glow_cache():
    """Clear the cache if memory becomes an issue."""
    global _glow_cache
    _glow_cache = {}