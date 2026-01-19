
import pygame

def draw_glow(surface, color, pos, radius):
    """Draws a simulated glow effect using additive blending."""
    if radius <= 0: return
    r = int(radius * 2.5)
    glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    
    # Outer soft glow
    pygame.draw.circle(glow_surf, (*color, 30), (r, r), r)
    # Inner brighter glow
    pygame.draw.circle(glow_surf, (*color, 60), (r, r), int(r * 0.6))
    
    # Blit with ADDitive blend mode
    rect = glow_surf.get_rect(center=(int(pos[0]), int(pos[1])))
    surface.blit(glow_surf, rect, special_flags=pygame.BLEND_ADD)
