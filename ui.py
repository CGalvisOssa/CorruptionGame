"""
Sistema de interfaz de usuario: HUD, menús, pantallas
"""
import pygame
from config import *


def draw_hud(window, player, puntuacion, combo):
    """Dibuja la interfaz de usuario durante el juego"""
    fuente = pygame.font.Font(None, 36)
    
    # Vida (superior izquierda)
    texto_vida = fuente.render(f"Vida: {player.vida}/{player.vida_maxima}", True, COLOR_BLANCO)
    window.blit(texto_vida, (10, 10))
    
    # Barra de vida visual
    barra_x, barra_y = 10, 45
    barra_ancho, barra_alto = 200, 20
    pygame.draw.rect(window, (100, 0, 0), (barra_x, barra_y, barra_ancho, barra_alto))
    vida_actual = (player.vida / player.vida_maxima) * barra_ancho
    pygame.draw.rect(window, COLOR_ROJO, (barra_x, barra_y, vida_actual, barra_alto))
    pygame.draw.rect(window, COLOR_BLANCO, (barra_x, barra_y, barra_ancho, barra_alto), 2)
    
    # Munición (inferior derecha)
    texto_municion = fuente.render(f"Munición: {player.municion}", True, COLOR_BLANCO)
    window.blit(texto_municion, (WIDTH - 250, HEIGHT - 50))
    
    # Puntuación (superior derecha)
    texto_puntos = fuente.render(f"Puntos: {puntuacion}", True, COLOR_AMARILLO_COLOMBIA)
    window.blit(texto_puntos, (WIDTH - 250, 10))
    
    # Combo (superior centro)
    if combo > 1:
        texto_combo = fuente.render(f"COMBO x{combo}", True, (255, 100, 0))
        combo_x = WIDTH // 2 - texto_combo.get_width() // 2
        window.blit(texto_combo, (combo_x, 10))


def draw_menu(window):
    """
    Dibuja el menú principal
    
    Returns:
        int o None: Índice de la opción sobre la que está el mouse
    """
    window.fill(COLOR_CIELO)
    
    fuente_titulo = pygame.font.Font(None, 100)
    fuente_subtitulo = pygame.font.Font(None, 40)
    fuente_opciones = pygame.font.Font(None, 50)
    
    # Título con colores de Colombia
    titulo = fuente_titulo.render("CORRUPTION RUN", True, COLOR_AMARILLO_COLOMBIA)
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, 150))
    window.blit(titulo, titulo_rect)
    
    # Subtítulo
    subtitulo = fuente_subtitulo.render("Huye de la corrupción", True, COLOR_BLANCO)
    subtitulo_rect = subtitulo.get_rect(center=(WIDTH // 2, 230))
    window.blit(subtitulo, subtitulo_rect)
    
    # Opciones del menú
    opciones = ["JUGAR", "INSTRUCCIONES", "SALIR"]
    mouse_pos = pygame.mouse.get_pos()
    opcion_seleccionada = None
    
    for i, opcion in enumerate(opciones):
        y_pos = 350 + i * 80
        texto = fuente_opciones.render(opcion, True, COLOR_BLANCO)
        texto_rect = texto.get_rect(center=(WIDTH // 2, y_pos))
        
        if texto_rect.collidepoint(mouse_pos):
            texto = fuente_opciones.render(opcion, True, COLOR_AMARILLO_COLOMBIA)
            pygame.draw.rect(window, COLOR_GRIS_OSCURO, texto_rect.inflate(40, 20), border_radius=10)
            opcion_seleccionada = i
        
        window.blit(texto, texto_rect)
    
    # Créditos
    fuente_pequeña = pygame.font.Font(None, 24)
    creditos = fuente_pequeña.render("Presiona ESC en cualquier momento para volver al menú", True, COLOR_GRIS_CLARO)
    creditos_rect = creditos.get_rect(center=(WIDTH // 2, HEIGHT - 30))
    window.blit(creditos, creditos_rect)
    
    pygame.display.update()
    return opcion_seleccionada


def draw_instructions(window):
    """
    Dibuja la pantalla de instrucciones
    
    Returns:
        bool: True si el mouse está sobre el botón volver
    """
    window.fill(COLOR_CIELO)
    
    fuente_titulo = pygame.font.Font(None, 80)
    fuente_texto = pygame.font.Font(None, 36)
    fuente_pequeña = pygame.font.Font(None, 28)
    
    # Título
    titulo = fuente_titulo.render("INSTRUCCIONES", True, COLOR_AMARILLO_COLOMBIA)
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, 80))
    window.blit(titulo, titulo_rect)
    
    # Controles
    controles = [
        "CONTROLES:",
        "",
        "A / ← : Mover izquierda",
        "D / → : Mover derecha",
        "ESPACIO : Saltar (doble salto disponible)",
        "CLICK IZQ / CTRL : Disparar",
        "ESC : Menú principal",
        "",
        "OBJETIVO:",
        "",
        "Elimina a los enemigos corruptos mientras",
        "atraviesas el nivel. Mantén tu combo para",
        "obtener más puntos. ¡No te quedes sin munición!",
        "",
        "ENEMIGOS:",
        "• Maletines con piernas (cafés)",
        "• Contratos fantasma (blancos)",
    ]
    
    y_pos = 180
    for linea in controles:
        if linea.endswith(":"):
            texto = fuente_texto.render(linea, True, COLOR_AMARILLO_COLOMBIA)
        elif linea.startswith("•"):
            texto = fuente_pequeña.render(linea, True, (200, 200, 200))
        else:
            texto = fuente_texto.render(linea, True, COLOR_BLANCO)
        
        texto_rect = texto.get_rect(center=(WIDTH // 2, y_pos))
        window.blit(texto, texto_rect)
        y_pos += 35
    
    # Botón volver
    fuente_boton = pygame.font.Font(None, 50)
    mouse_pos = pygame.mouse.get_pos()
    
    volver_texto = fuente_boton.render("VOLVER", True, COLOR_BLANCO)
    volver_rect = volver_texto.get_rect(center=(WIDTH // 2, HEIGHT - 80))
    
    if volver_rect.collidepoint(mouse_pos):
        volver_texto = fuente_boton.render("VOLVER", True, COLOR_AMARILLO_COLOMBIA)
        pygame.draw.rect(window, COLOR_GRIS_OSCURO, volver_rect.inflate(40, 20), border_radius=10)
    
    window.blit(volver_texto, volver_rect)
    
    pygame.display.update()
    return volver_rect.collidepoint(mouse_pos)


def draw_game_over(window, puntuacion):
    """
    Dibuja la pantalla de Game Over
    
    Returns:
        str: "menu" o "salir" según lo que elija el jugador
    """
    fuente_grande = pygame.font.Font(None, 72)
    fuente_mediana = pygame.font.Font(None, 48)
    
    # Overlay oscuro
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(COLOR_NEGRO)
    window.blit(overlay, (0, 0))
    
    # Textos
    texto_game_over = fuente_grande.render("GAME OVER", True, COLOR_ROJO)
    texto_puntos = fuente_mediana.render(f"Puntuación Final: {puntuacion}", True, COLOR_AMARILLO_COLOMBIA)
    texto_continuar = fuente_mediana.render("Presiona ESC para volver al menú", True, COLOR_BLANCO)
    
    window.blit(texto_game_over, (WIDTH//2 - texto_game_over.get_width()//2, HEIGHT//2 - 100))
    window.blit(texto_puntos, (WIDTH//2 - texto_puntos.get_width()//2, HEIGHT//2))
    window.blit(texto_continuar, (WIDTH//2 - texto_continuar.get_width()//2, HEIGHT//2 + 80))
    
    pygame.display.update()
    
    # Esperar input del jugador
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "menu"