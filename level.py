"""
Sistema de creación y gestión de niveles
"""
import pygame
from config import *
from objects import Block, Fire, MovingPlatform
from entities import Enemy, Boss, PowerUp


def crear_nivel_1():
    """
    Crea el nivel 1 completo con boss final
    
    Returns:
        tuple: (lista_objetos, grupo_enemigos, grupo_powerups, boss)
    """
    block_size = BLOCK_SIZE
    
    # Suelo base
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 5) // block_size)]
    
    # Trampas de fuego (varias, activas)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    fire2 = Fire(block_size * 16, HEIGHT - block_size - 64, 16, 32)
    fire2.on()
    fire3 = Fire(block_size * 20, HEIGHT - block_size * 3 - 64, 16, 32)
    fire3.on()
    fire4 = Fire(block_size * 29, HEIGHT - block_size * 4 - 64, 16, 32)
    fire4.on()
    fire5 = Fire(block_size * 38, HEIGHT - block_size * 5 - 64, 16, 32)
    fire5.on()
    fire6 = Fire(block_size * 43, HEIGHT - block_size * 6 - 64, 16, 32)
    fire6.on()
    
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
        
        # PLATAFORMA MÓVIL 1 (horizontal)
        MovingPlatform(block_size * 12, HEIGHT - block_size * 4, block_size, 20, move_x=2, distance=150),
        
        # Bajada con gaps
        Block(block_size * 14, HEIGHT - block_size * 3, block_size),
        Block(block_size * 15, HEIGHT - block_size * 3, block_size),
        
        # Zona media - Plataformas flotantes
        Block(block_size * 17, HEIGHT - block_size * 2, block_size),
        Block(block_size * 19, HEIGHT - block_size * 3, block_size),
        
        # PLATAFORMA MÓVIL 2 (vertical)
        MovingPlatform(block_size * 21, HEIGHT - block_size * 2, block_size, 20, move_y=2, distance=100),
        
        Block(block_size * 23, HEIGHT - block_size * 3, block_size),
        Block(block_size * 25, HEIGHT - block_size * 2, block_size),
        
        # Torres altas
        Block(block_size * 27, HEIGHT - block_size * 6, block_size),
        Block(block_size * 28, HEIGHT - block_size * 6, block_size),
        Block(block_size * 27, HEIGHT - block_size * 5, block_size),
        Block(block_size * 28, HEIGHT - block_size * 5, block_size),
        
        # PLATAFORMA MÓVIL 3 (horizontal rápida)
        MovingPlatform(block_size * 30, HEIGHT - block_size * 4, block_size, 20, move_x=3, distance=200),
        
        # Zona avanzada - Laberinto vertical
        Block(block_size * 32, HEIGHT - block_size * 2, block_size),
        Block(block_size * 33, HEIGHT - block_size * 3, block_size),
        Block(block_size * 34, HEIGHT - block_size * 4, block_size),
        Block(block_size * 35, HEIGHT - block_size * 4, block_size),
        Block(block_size * 36, HEIGHT - block_size * 3, block_size),
        Block(block_size * 37, HEIGHT - block_size * 2, block_size),
        
        # Plataformas largas finales
        Block(block_size * 39, HEIGHT - block_size * 5, block_size),
        Block(block_size * 40, HEIGHT - block_size * 5, block_size),
        Block(block_size * 41, HEIGHT - block_size * 5, block_size),
        Block(block_size * 42, HEIGHT - block_size * 5, block_size),
        
        # ZONA DEL BOSS - Plataforma final elevada
        Block(block_size * 44, HEIGHT - block_size * 6, block_size),
        Block(block_size * 45, HEIGHT - block_size * 6, block_size),
        Block(block_size * 46, HEIGHT - block_size * 6, block_size),
        Block(block_size * 47, HEIGHT - block_size * 6, block_size),
        Block(block_size * 48, HEIGHT - block_size * 6, block_size),
        
        # Plataformas para pelear con el boss
        Block(block_size * 44, HEIGHT - block_size * 3, block_size),
        Block(block_size * 48, HEIGHT - block_size * 3, block_size),
        
        # traps scattered across level
        fire,
        fire2,
        fire3,
        fire4,
        fire5,
        fire6
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
    enemies.add(Enemy(block_size * 33, HEIGHT - block_size * 3 - 60, 50, 60, "contrato"))
    enemies.add(Enemy(block_size * 35, HEIGHT - block_size * 4 - 80, 60, 80, "maletin"))
    # Enemigos voladores - mermelada
    enemies.add(Enemy(block_size * 22, HEIGHT - block_size * 5 - 90, 50, 50, "mermelada"))
    enemies.add(Enemy(block_size * 37, HEIGHT - block_size * 6 - 120, 50, 50, "mermelada"))
    
    # Zona pre-boss
    enemies.add(Enemy(block_size * 40, HEIGHT - block_size * 5 - 80, 60, 80, "maletin"))
    enemies.add(Enemy(block_size * 41, HEIGHT - block_size * 5 - 60, 50, 60, "contrato"))
    
    # Crear power-ups estratégicamente ubicados
    powerups = pygame.sprite.Group()
    powerups.add(PowerUp(block_size * 5, HEIGHT - block_size * 4 - 50, "municion"))
    powerups.add(PowerUp(block_size * 10, HEIGHT - block_size * 5 - 50, "vida"))
    powerups.add(PowerUp(block_size * 19, HEIGHT - block_size * 3 - 50, "cafe"))
    powerups.add(PowerUp(block_size * 27, HEIGHT - block_size * 6 - 50, "municion"))
    powerups.add(PowerUp(block_size * 36, HEIGHT - block_size * 3 - 50, "vida"))
    powerups.add(PowerUp(block_size * 42, HEIGHT - block_size * 5 - 50, "municion"))
    
    # Crear BOSS
    # Poner el boss más abajo en el mapa para que quede visible en la plataforma final
    boss = Boss(block_size * 46, HEIGHT - block_size * 3 - 300)
    
    return objects, enemies, powerups, boss