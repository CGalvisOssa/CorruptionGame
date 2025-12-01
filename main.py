"""
CORRUPTION RUN
Plataformero de acción donde un político colombiano huye de la corrupción

Punto de entrada principal del juego
"""
import pygame
import sys
from config import *
import traceback
from datetime import datetime
from player import Player
from os.path import join
from utils import get_background
from collision import handle_move
from level import crear_nivel_1
from ui import draw_hud, draw_menu, draw_instructions, draw_game_over

# Inicialización
pygame.init()
# inicializar audio (si es posible)
try:
    pygame.mixer.init()
except Exception:
    pass

# Cargar efectos de sonido y música de fondo (si existen)
shot_sound = None
explosion_sound = None
bg_music_path = None
try:
    shot_sound = pygame.mixer.Sound(join(PATH_ASSETS, PATH_SOUNDS, "disparo.mp3"))
except Exception:
    shot_sound = None
try:
    explosion_sound = pygame.mixer.Sound(join(PATH_ASSETS, PATH_SOUNDS, "explosion.mp3"))
except Exception:
    explosion_sound = None

try:
    bg_music_path = join(PATH_ASSETS, PATH_MUSIC, "fondo.mp3")
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except Exception:
    pass
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


def draw(window, background, bg_image, player, objects, bullets, boss_bullets, enemies, powerups, boss, offset_x, puntuacion, combo, boss_derrotado):
    """Dibuja todos los elementos del juego en pantalla"""
    # Fondo
    for tile in background:
        window.blit(bg_image, tile)

    # Objetos del nivel
    for obj in objects:
        obj.draw(window, offset_x)
    
    # Power-ups
    for powerup in powerups:
        powerup.draw(window, offset_x)
    
    # Proyectiles del jugador
    for bullet in bullets:
        bullet.draw(window, offset_x)
    
    # Proyectiles del boss
    for bullet in boss_bullets:
        bullet.draw(window, offset_x)
    
    # Enemigos
    for enemy in enemies:
        enemy.draw(window, offset_x)
    
    # Boss (si no está derrotado)
    if boss and not boss_derrotado:
        boss.draw(window, offset_x)

    # Jugador
    player.draw(window, offset_x)
    
    # HUD
    draw_hud(window, player, puntuacion, combo)
    
    # Mensaje de victoria si el boss fue derrotado
    if boss_derrotado:
        fuente = pygame.font.Font(None, 72)
        texto = fuente.render("¡VICTORIA!", True, COLOR_AMARILLO_COLOMBIA)
        window.blit(texto, (WIDTH//2 - texto.get_width()//2, HEIGHT//2 - 100))

    pygame.display.update()


def jugar(window):
    """
    Loop principal del juego
    
    Returns:
        str: "menu" o "salir"
    """
    clock = pygame.time.Clock()
    background, bg_image = get_background("ciudad.png")

    # Vamos a permitir reiniciar el nivel sin volver al menú: bucle exterior para reinicios
    while True:
        try:
            # Crear jugador
            player = Player(100, 100, 50, 50)

            # Crear nivel
            objects, enemies, powerups, boss = crear_nivel_1()

            # Grupos de proyectiles
            bullets = pygame.sprite.Group()
            boss_bullets = pygame.sprite.Group()

            # Variables de juego
            puntuacion = 0
            combo = 0
            ultimo_golpe_tiempo = 0
            boss_derrotado = False
            tiempo_victoria = 0

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
                        # reproducir sonido de disparo si disponible
                        try:
                            if shot_sound:
                                shot_sound.play()
                        except Exception:
                            pass

                player.actualizar_cooldown(tiempo_actual)
                # Actualizar estado del boost de velocidad si aplica
                try:
                    player.update_speed_boost(tiempo_actual)
                except Exception:
                    pass

                # Actualizar entidades
                player.loop(FPS)

                # Actualizar objetos animados y plataformas móviles
                for obj in objects:
                    if hasattr(obj, 'loop'):
                        obj.loop()

                handle_move(player, objects)
                bullets.update()
                boss_bullets.update()
                enemies.update(objects)

                # Actualizar power-ups
                for powerup in powerups:
                    powerup.loop()

                # Actualizar boss
                if boss and not boss_derrotado:
                    boss.update(objects, player.rect.centerx)
                    boss.actualizar_cooldown(tiempo_actual)

                    # Boss dispara
                    nuevas_balas = boss.disparar(tiempo_actual)
                    for bala in nuevas_balas:
                        boss_bullets.add(bala)

                # Colisiones balas del jugador - enemigos
                for bullet in bullets:
                    # Eliminar balas fuera de pantalla
                    if bullet.rect.right < offset_x - 100 or bullet.rect.left > offset_x + WIDTH + 100:
                        bullet.kill()
                        continue

                    enemigos_golpeados = pygame.sprite.spritecollide(bullet, enemies, False)
                    if enemigos_golpeados:
                        enemigo = enemigos_golpeados[0]
                        died = enemigo.recibir_dano(bullet.dano)
                        # eliminar la bala siempre
                        bullet.kill()

                        if died:
                            # iniciar animación de muerte en enemigo y reproducir explosion
                            try:
                                enemigo.start_death()
                            except Exception:
                                enemigo.kill()

                            try:
                                if explosion_sound:
                                    explosion_sound.play()
                            except Exception:
                                pass

                            puntuacion += PUNTOS_POR_ENEMIGO * (combo + 1)
                            combo += 1
                            ultimo_golpe_tiempo = tiempo_actual

                        # después de procesar impacto con un enemigo, continuar con la siguiente bala
                        continue

                    # Colisión con boss
                    if boss and not boss_derrotado and pygame.sprite.collide_mask(bullet, boss):
                        if boss.recibir_dano(bullet.dano):
                            boss_derrotado = True
                            tiempo_victoria = tiempo_actual
                            puntuacion += 5000
                            try:
                                if explosion_sound:
                                    explosion_sound.play()
                            except Exception:
                                pass
                        bullet.kill()
                        continue

                # Colisiones balas del boss - jugador
                balas_jugador = pygame.sprite.spritecollide(player, boss_bullets, True)
                for bala in balas_jugador:
                    player.make_hit(bala.dano)
                    combo = 0

                # Reset combo si pasa mucho tiempo
                if tiempo_actual - ultimo_golpe_tiempo > COMBO_TIMEOUT and combo > 0:
                    combo = 0

                # Colisiones jugador-enemigos
                enemigos_tocados = pygame.sprite.spritecollide(player, enemies, False)
                for enemigo in enemigos_tocados:
                    player.make_hit(enemigo.dano_al_jugador)
                    combo = 0

                # Colisión jugador-boss
                if boss and not boss_derrotado and pygame.sprite.collide_mask(player, boss):
                    player.make_hit(boss.dano_al_jugador)
                    combo = 0

                # Colisiones jugador-powerups
                powerups_recolectados = pygame.sprite.spritecollide(player, powerups, True)
                for powerup in powerups_recolectados:
                    if powerup.tipo == "municion":
                        player.municion = min(player.municion + 20, player.municion_maxima)
                    elif powerup.tipo == "vida":
                        player.vida = min(player.vida + 30, player.vida_maxima)
                    elif powerup.tipo == "cafe":
                        # Aplica velocidad temporal de 10 segundos (1.5x)
                        player.apply_speed_boost(10000, 1.5, tiempo_actual)
                        puntuacion += 50

                # Muerte por caída
                if player.rect.top > DEATH_ZONE:
                    player.vida = 0

                # Game Over
                if player.vida <= 0:
                    # Mostrar pantalla de game over (permitir reintento)
                    draw(window, background, bg_image, player, objects, bullets, boss_bullets, enemies, powerups, boss, offset_x, puntuacion, combo, boss_derrotado)
                    resultado = draw_game_over(window, puntuacion, allow_retry=True)
                    if resultado == "salir":
                        return "salir"
                    if resultado == "menu":
                        return "menu"
                    if resultado == "retry":
                        # Reiniciar el nivel: romper el bucle interior para recrear todo en la siguiente iteración
                        break

                # Victoria - esperar 3 segundos antes de volver al menú
                if boss_derrotado and tiempo_actual - tiempo_victoria > 3000:
                    draw(window, background, bg_image, player, objects, bullets, boss_bullets, enemies, powerups, boss, offset_x, puntuacion, combo, boss_derrotado)
                    pygame.time.delay(2000)
                    return "menu"

                # Dibujar todo
                draw(window, background, bg_image, player, objects, bullets, boss_bullets, enemies, powerups, boss, offset_x, puntuacion, combo, boss_derrotado)

                # Scroll de cámara
                if ((player.rect.right - offset_x >= WIDTH - SCROLL_AREA_WIDTH) and player.x_vel > 0) or (
                        (player.rect.left - offset_x <= SCROLL_AREA_WIDTH) and player.x_vel < 0):
                    offset_x += player.x_vel

        except Exception:
            # Loggear error en disco para diagnosticar
            tb = traceback.format_exc()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = f"crash_log_{timestamp}.txt"
            try:
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write(tb)
            except Exception:
                # No interrumpir si no podemos escribir el log
                pass

            # Mostrar pantalla de error, permitir volver al menú
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill((20, 20, 30))
            window.blit(overlay, (0, 0))

            fuente = pygame.font.Font(None, 48)
            mensaje = fuente.render("Se produjo un error. Presiona ESC para volver al menú.", True, COLOR_BLANCO)
            sub = pygame.font.Font(None, 28).render(f"Registro guardado en: {log_path}", True, COLOR_GRIS_CLARO)

            window.blit(mensaje, (WIDTH//2 - mensaje.get_width()//2, HEIGHT//2 - 20))
            window.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 40))
            pygame.display.update()

            # Esperar que el jugador cierre o vuelva al menú
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "salir"
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return "menu"
        
        # Victoria - esperar 3 segundos antes de volver al menú
        if boss_derrotado and tiempo_actual - tiempo_victoria > 3000:
            draw(window, background, bg_image, player, objects, bullets, boss_bullets, enemies, powerups, boss, offset_x, puntuacion, combo, boss_derrotado)
            pygame.time.delay(2000)
            return "menu"

        # Dibujar todo
        draw(window, background, bg_image, player, objects, bullets, boss_bullets, enemies, powerups, boss, offset_x, puntuacion, combo, boss_derrotado)

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