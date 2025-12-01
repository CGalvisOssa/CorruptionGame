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