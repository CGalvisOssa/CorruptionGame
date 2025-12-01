"""
Sistema de creación y gestión de niveles
"""
import pygame
from config import *
from objects import Block, Fire
from entities import Enemy


def crear_nivel_1():
    """
    Crea el nivel 1 completo
    
    Returns:
        tuple: (lista_objetos, grupo_enemigos)
    """
    block_size = BLOCK_SIZE
    
    # Suelo base
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    
    
    
    # Trampa de fuego
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    
    # Crear plataformas y objetos - NIVEL EXTENDIDO
    objects = [
        *floor,
        # Zona inicial - Tutorial
        Block(0, HEIGHT - block_size * 2, block_size),
        Block(block_size * 1, HEIGHT - block_size * 2, block_size),
        
        # Primera sección - Escaleras
        Block(block_size * 3, HEIGHT - block_size * 2, block_size),
        Block(block_size * 4, HEIGHT - block_size * 3, block_size),
        Block(block_size * 5, HEIGHT - block_size * 4, block_size),
        Block(block_size * 6, HEIGHT - block_size * 4, block_size),
        
        # Plataforma alta
        Block(block_size * 8, HEIGHT - block_size * 5, block_size),
        Block(block_size * 9, HEIGHT - block_size * 5, block_size),
        Block(block_size * 10, HEIGHT - block_size * 5, block_size),
        
        # Bajada con gaps
        Block(block_size * 12, HEIGHT - block_size * 4, block_size),
        Block(block_size * 14, HEIGHT - block_size * 3, block_size),
        Block(block_size * 15, HEIGHT - block_size * 3, block_size),
        
        # Zona media - Plataformas flotantes
        Block(block_size * 17, HEIGHT - block_size * 2, block_size),
        Block(block_size * 19, HEIGHT - block_size * 3, block_size),
        Block(block_size * 21, HEIGHT - block_size * 4, block_size),
        Block(block_size * 23, HEIGHT - block_size * 3, block_size),
        Block(block_size * 25, HEIGHT - block_size * 2, block_size),
        
        # Torres altas
        Block(block_size * 27, HEIGHT - block_size * 6, block_size),
        Block(block_size * 28, HEIGHT - block_size * 6, block_size),
        Block(block_size * 27, HEIGHT - block_size * 5, block_size),
        Block(block_size * 28, HEIGHT - block_size * 5, block_size),
        
        # Zona avanzada - Laberinto vertical
        Block(block_size * 30, HEIGHT - block_size * 2, block_size),
        Block(block_size * 31, HEIGHT - block_size * 2, block_size),
        Block(block_size * 32, HEIGHT - block_size * 3, block_size),
        Block(block_size * 33, HEIGHT - block_size * 4, block_size),
        Block(block_size * 34, HEIGHT - block_size * 4, block_size),
        Block(block_size * 35, HEIGHT - block_size * 3, block_size),
        Block(block_size * 36, HEIGHT - block_size * 2, block_size),
        
        # Plataformas largas finales
        Block(block_size * 38, HEIGHT - block_size * 5, block_size),
        Block(block_size * 39, HEIGHT - block_size * 5, block_size),
        Block(block_size * 40, HEIGHT - block_size * 5, block_size),
        Block(block_size * 41, HEIGHT - block_size * 5, block_size),
        
        # Zona final elevada
        Block(block_size * 43, HEIGHT - block_size * 6, block_size),
        Block(block_size * 44, HEIGHT - block_size * 6, block_size),
        Block(block_size * 45, HEIGHT - block_size * 6, block_size),
        Block(block_size * 46, HEIGHT - block_size * 6, block_size),
        
        fire
    ]
    
    # Crear enemigos distribuidos por el nivel
    enemies = pygame.sprite.Group()
    
    # Zona inicial
    enemies.add(Enemy(300, HEIGHT - block_size * 2 - 80, 60, 80, "maletin"))
    
    # Primera sección elevada
    enemies.add(Enemy(block_size * 6 + 20, HEIGHT - block_size * 4 - 80, 60, 80, "maletin"))
    enemies.add(Enemy(block_size * 9, HEIGHT - block_size * 5 - 60, 50, 60, "contrato"))
    
    # Zona media
    enemies.add(Enemy(block_size * 15, HEIGHT - block_size * 3 - 80, 60, 80, "maletin"))
    enemies.add(Enemy(block_size * 19, HEIGHT - block_size * 3 - 60, 50, 60, "contrato"))
    enemies.add(Enemy(block_size * 23, HEIGHT - block_size * 3 - 80, 60, 80, "maletin"))
    
    # Torres
    enemies.add(Enemy(block_size * 27 + 20, HEIGHT - block_size * 6 - 80, 60, 80, "maletin"))
    
    # Zona avanzada
    enemies.add(Enemy(block_size * 31, HEIGHT - block_size * 2 - 60, 50, 60, "contrato"))
    enemies.add(Enemy(block_size * 34, HEIGHT - block_size * 4 - 80, 60, 80, "maletin"))
    
    # Zona final
    enemies.add(Enemy(block_size * 39, HEIGHT - block_size * 5 - 80, 60, 80, "maletin"))
    enemies.add(Enemy(block_size * 44, HEIGHT - block_size * 6 - 80, 60, 80, "maletin"))
    enemies.add(Enemy(block_size * 45, HEIGHT - block_size * 6 - 60, 50, 60, "contrato"))
    
    return objects, enemies