"""
CORRUPTION RUN
Plataformero de acción donde un político colombiano huye de la corrupción

Punto de entrada principal del juego
"""
import pygame
import sys
from config import *
from player import Player
from utils import get_background
from collision import handle_move
from level import crear_nivel_1
from ui import draw_hud, draw_menu, draw_instructions, draw_game_over

# Inicialización
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)


def menu_principal(window):
    """
    Loop del menú principal
    
    Returns:
        str: "jugar", "salir"
    """
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(FPS)
        opcion_hover = draw_menu(window)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if opcion_hover == 0:  # JUGAR
                    return "jugar"
                elif opcion_hover == 1:  # INSTRUCCIONES
                    resultado = mostrar_instrucciones(window)
                    if resultado == "salir":
                        return "salir"
                elif opcion_hover == 2:  # SALIR
                    return "salir"
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return "jugar"
                if evento.key == pygame.K_ESCAPE:
                    return "salir"


def mostrar_instrucciones(window):
    """
    Loop de la pantalla de instrucciones
    
    Returns:
        str: "menu" o "salir"
    """
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(FPS)
        volver_hover = draw_instructions(window)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if volver_hover:
                    return "menu"
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_BACKSPACE:
                    return "menu"


def draw(window, background, bg_image, player, objects, bullets, enemies, offset_x, puntuacion, combo):
    """Dibuja todos los elementos del juego en pantalla"""
    # Fondo
    for tile in background:
        window.blit(bg_image, tile)

    # Objetos del nivel
    for obj in objects:
        obj.draw(window, offset_x)
    
    # Proyectiles
    for bullet in bullets:
        bullet.draw(window, offset_x)
    
    # Enemigos
    for enemy in enemies:
        enemy.draw(window, offset_x)

    # Jugador
    player.draw(window, offset_x)
    
    # HUD
    draw_hud(window, player, puntuacion, combo)

    pygame.display.update()


def jugar(window):
    """
    Loop principal del juego
    
    Returns:
        str: "menu" o "salir"
    """
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    # Crear jugador
    player = Player(100, 100, 50, 50)
    
    # Crear nivel
    objects, enemies = crear_nivel_1()
    
    # Grupo de balas
    bullets = pygame.sprite.Group()
    
    # Variables de juego
    puntuacion = 0
    combo = 0
    ultimo_golpe_tiempo = 0

    offset_x = 0

    run = True
    while run:
        clock.tick(FPS)
        tiempo_actual = pygame.time.get_ticks()

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        
        # Disparar
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        if mouse_buttons[0] or keys[pygame.K_LCTRL]:
            bala = player.disparar(tiempo_actual)
            if bala:
                bullets.add(bala)
        
        player.actualizar_cooldown(tiempo_actual)

        # Actualizar entidades
        player.loop(FPS)
        
        # Actualizar trampas animadas
        for obj in objects:
            if hasattr(obj, 'loop'):
                obj.loop()
        
        handle_move(player, objects)
        bullets.update()
        enemies.update(objects)
        
        # Colisiones balas-enemigos
        for bullet in bullets:
            # Eliminar balas fuera de pantalla
            if bullet.rect.right < offset_x - 100 or bullet.rect.left > offset_x + WIDTH + 100:
                bullet.kill()
                continue
                
            enemigos_golpeados = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemigo in enemigos_golpeados:
                if enemigo.recibir_dano(bullet.dano):
                    enemigo.kill()
                    puntuacion += PUNTOS_POR_ENEMIGO * (combo + 1)
                    combo += 1
                    ultimo_golpe_tiempo = tiempo_actual
                bullet.kill()
                break
        
        # Reset combo si pasa mucho tiempo
        if tiempo_actual - ultimo_golpe_tiempo > COMBO_TIMEOUT and combo > 0:
            combo = 0
        
        # Colisiones jugador-enemigos
        enemigos_tocados = pygame.sprite.spritecollide(player, enemies, False)
        for enemigo in enemigos_tocados:
            player.recibir_dano(enemigo.dano_al_jugador)
            combo = 0
        
        # Game Over
        if player.vida <= 0:
            draw(window, background, bg_image, player, objects, bullets, enemies, offset_x, puntuacion, combo)
            resultado = draw_game_over(window, puntuacion)
            return resultado

        # Dibujar todo
        draw(window, background, bg_image, player, objects, bullets, enemies, offset_x, puntuacion, combo)

        # Scroll de cámara
        if ((player.rect.right - offset_x >= WIDTH - SCROLL_AREA_WIDTH) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= SCROLL_AREA_WIDTH) and player.x_vel < 0):
            offset_x += player.x_vel
    
    return "menu"


def main():
    """Función principal - Controla el flujo del juego"""
    while True:
        accion = menu_principal(window)
        
        if accion == "salir":
            pygame.quit()
            sys.exit()
        elif accion == "jugar":
            resultado = jugar(window)
            if resultado == "salir":
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()