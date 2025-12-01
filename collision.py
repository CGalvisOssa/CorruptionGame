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
                
                # Si es plataforma móvil, mover al jugador con ella
                if hasattr(obj, 'name') and obj.name == "moving_platform":
                    if obj.move_x != 0:
                        player.rect.x += obj.move_x * obj.direction
                        
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
    # use player speed if available (for speed boosts), otherwise fallback
    try:
        player_speed = player.get_speed()
    except Exception:
        player_speed = PLAYER_VEL

    collide_left = collide(player, objects, -player_speed * 2)
    collide_right = collide(player, objects, player_speed * 2)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(player_speed)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(player_speed)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    # Verificar colisiones con trampas
    for obj in to_check:
        if obj and hasattr(obj, 'name') and obj.name == "fire":
            player.make_hit()