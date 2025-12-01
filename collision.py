"""
Sistema de colisiones del juego
"""
import pygame
from config import PLAYER_VEL


def handle_vertical_collision(player, objects, dy):
    """
    Maneja las colisiones verticales del jugador
    
    Returns:
        list: Objetos con los que colisionó
    """
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:  # Cayendo
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:  # Subiendo
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    """
    Detecta si el jugador colisionaría al moverse dx pixeles
    
    Returns:
        Object o None: El objeto con el que colisionó, o None
    """
    player.move(dx, 0)
    player.update()
    collided_object = None
    
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    """
    Maneja el movimiento del jugador con colisiones
    """
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    # Verificar colisiones con trampas
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()