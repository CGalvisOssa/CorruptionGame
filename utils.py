"""
Funciones de utilidad para cargar sprites y recursos
"""
import pygame
from os import listdir
from os.path import isfile, join
from config import *


def flip(sprites):
    """Voltea una lista de sprites horizontalmente"""
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    """
    Carga sprite sheets desde una carpeta
    
    Args:
        dir1: Primera carpeta (ej: "MainCharacters")
        dir2: Segunda carpeta (ej: "MaskDude")
        width: Ancho de cada frame
        height: Alto de cada frame
        direction: Si True, crea versiones left y right
    
    Returns:
        dict: Diccionario con nombre_accion: [sprites]
    """
    path = join(PATH_ASSETS, dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    """Carga un bloque de terreno"""
    path = join(PATH_ASSETS, PATH_TERRAIN, "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def get_background(name):
    """
    Carga un fondo y crea tiles para cubrir la pantalla
    
    Returns:
        tuple: (lista_de_posiciones, imagen)
    """
    image = pygame.image.load(join(PATH_ASSETS, PATH_BACKGROUND, name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image