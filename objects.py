"""
Objetos del nivel: bloques, plataformas, trampas
"""
import pygame
from config import *
from utils import get_block, load_sprite_sheets


class Object(pygame.sprite.Sprite):
    """Clase base para objetos del nivel"""
    
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        """Dibuja el objeto en pantalla"""
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    """Bloque de terreno sólido"""
    
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class MovingPlatform(Object):
    """Plataforma que se mueve horizontalmente o verticalmente"""
    
    def __init__(self, x, y, width, height, move_x=0, move_y=0, distance=200):
        super().__init__(x, y, width, height, "moving_platform")
        
        # Crear imagen de la plataforma
        self.image.fill((100, 100, 150))  # Color azul grisáceo
        pygame.draw.rect(self.image, (150, 150, 200), (0, 0, width, height), 3)  # Borde
        self.mask = pygame.mask.from_surface(self.image)
        
        # Movimiento
        self.start_x = x
        self.start_y = y
        self.move_x = move_x  # Velocidad horizontal
        self.move_y = move_y  # Velocidad vertical
        self.distance = distance  # Distancia máxima de movimiento
        self.traveled = 0
        self.direction = 1  # 1 o -1
        
    def loop(self):
        """Actualiza el movimiento de la plataforma"""
        # Movimiento horizontal
        if self.move_x != 0:
            movement = self.move_x * self.direction
            self.rect.x += movement
            self.traveled += abs(movement)
            
            if self.traveled >= self.distance:
                self.direction *= -1
                self.traveled = 0
        
        # Movimiento vertical
        if self.move_y != 0:
            movement = self.move_y * self.direction
            self.rect.y += movement
            self.traveled += abs(movement)
            
            if self.traveled >= self.distance:
                self.direction *= -1
                self.traveled = 0


class Fire(Object):
    """Trampa de fuego animada"""
    
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets(PATH_TRAPS, "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        """Enciende el fuego"""
        self.animation_name = "on"

    def off(self):
        """Apaga el fuego"""
        self.animation_name = "off"

    def loop(self):
        """Actualiza la animación del fuego"""
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0