import pygame
import math
import time
import os
import ctypes
from ctypes import windll

# --- Configuration ---
FPS = 60
# Reduced window size for a tighter look
WIDTH, HEIGHT = 350, 350 
BG_COLOR = (5, 0, 10)     # Dark background (transparent key)

# --- Colors (Siri "Liquid" Palette) ---
CYAN    = (40, 200, 255)
BLUE    = (20, 50, 255)
PURPLE  = (180, 10, 220)
MAGENTA = (255, 40, 160)
WHITE   = (200, 240, 255) # For the hot core

def make_window_transparent(hwnd):
    try:
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        LWA_COLORKEY = 0x00000001
        
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
        
        r, g, b = BG_COLOR
        color_key = b << 16 | g << 8 | r
        windll.user32.SetLayeredWindowAttributes(hwnd, color_key, 0, LWA_COLORKEY)
    except Exception as e:
        print(f"Transparency Error: {e}")

class LiquidBlob:
    def __init__(self, color, max_radius, speed_x, speed_y, offset, wobble_amount):
        self.color = color
        self.max_radius = max_radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.offset = offset
        self.wobble_amount = wobble_amount
        
        # Pre-render the glow texture
        self.surface = self._create_glow_texture(max_radius, color)

    def _create_glow_texture(self, radius, color):
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw soft gradient
        # We use more steps (density) for a smoother look
        for i in range(radius, 0, -1):
            # Calculate Alpha: Center is opaque, edges are transparent
            dist_norm = (radius - i) / radius
            alpha = int(40 * (dist_norm**2)) # Soft quadratic falloff
            
            draw_color = (*color, alpha) 
            pygame.draw.circle(surf, draw_color, (radius, radius), i)
        return surf

    def draw(self, surface, center, t):
        cx, cy = center
        
        # --- COMPLEX MOVEMENT (Lissajous Figure) ---
        # Instead of a perfect circle, x and y move at different speeds
        # This creates a "random" organic liquid motion
        move_x = math.sin(t * self.speed_x + self.offset) * self.wobble_amount
        move_y = math.cos(t * self.speed_y + self.offset) * (self.wobble_amount * 0.8)
        
        # Breathing effect (Size changes slightly)
        breath = math.sin(t * 3 + self.offset) * 5
        
        # Final Position
        x = cx + move_x
        y = cy + move_y
        
        # Draw centered
        radius_now = self.max_radius + int(breath)
        
        # Scale texture slightly for the breathing effect
        if abs(breath) > 1:
            try:
                # Fast scaling
                new_size = int(radius_now * 2)
                scaled_surf = pygame.transform.scale(self.surface, (new_size, new_size))
                surface.blit(scaled_surf, (x - radius_now, y - radius_now), special_flags=pygame.BLEND_ADD)
            except:
                pass
        else:
            surface.blit(self.surface, (x - self.max_radius, y - self.max_radius), special_flags=pygame.BLEND_ADD)

def main():
    # 1. Setup
    user32 = ctypes.windll.user32
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)
    
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    
    pygame.init()
    # Create screen using smaller WIDTH/HEIGHT if we wanted, but full screen transparent is safer for positioning
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.NOFRAME)
    hwnd = pygame.display.get_wm_info()["window"]
    
    make_window_transparent(hwnd)
    
    # 2. Define the "Liquid" Blobs
    # We mix different speeds (speed_x vs speed_y) to create chaotic movement
    blobs = [
        # Large slow background glow (Purple)
        LiquidBlob(PURPLE,  max_radius=80, speed_x=1.2, speed_y=1.5, offset=0, wobble_amount=40),
        
        # Main body (Cyan/Blue) - Moving opposite ways
        LiquidBlob(CYAN,    max_radius=60, speed_x=2.0, speed_y=1.8, offset=2, wobble_amount=35),
        LiquidBlob(BLUE,    max_radius=65, speed_x=-1.8, speed_y=2.2, offset=1, wobble_amount=30),
        
        # Fast "Hot" Highlights (Magenta/White) - Tighter movement
        LiquidBlob(MAGENTA, max_radius=50, speed_x=3.5, speed_y=3.0, offset=4, wobble_amount=20),
        LiquidBlob(WHITE,   max_radius=30, speed_x=4.0, speed_y=4.5, offset=5, wobble_amount=10)
    ]
    
    # Position: Bottom Center, raised up by 200px
    center_pos = (screen_w // 2, screen_h - 200)
    
    clock = pygame.time.Clock()
    start_time = time.time()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
        # Force TopMost
        user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)

        screen.fill(BG_COLOR)
        t = time.time() - start_time
        
        for blob in blobs:
            blob.draw(screen, center_pos, t)
            
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()