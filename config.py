"""
Configuración global del juego Corruption Run
Contiene todas las constantes y parámetros del juego
"""

# Configuración de pantalla
WIDTH = 1000
HEIGHT = 800
FPS = 60
CAPTION = "Corruption Run"

# Velocidades del jugador
PLAYER_VEL = 5
PLAYER_JUMP_FORCE = 4
PLAYER_GRAVITY = 1

# Configuración de combate
PLAYER_VIDA_INICIAL = 100
PLAYER_MUNICION_INICIAL = 50
COOLDOWN_DISPARO = 200  # milisegundos
BULLET_VELOCIDAD = 12
BULLET_DANO = 25

# Configuración de enemigos
ENEMY_VIDA = 50
ENEMY_VELOCIDAD = 2
ENEMY_DANO = 5

# Sistema de puntuación
PUNTOS_POR_ENEMIGO = 100
COMBO_TIMEOUT = 2000  # milisegundos

# Tamaños
BLOCK_SIZE = 96

# Cámara
SCROLL_AREA_WIDTH = 200

# Colores (RGB)
COLOR_CIELO = (20, 20, 40)
COLOR_AMARILLO_COLOMBIA = (255, 223, 0)
COLOR_AZUL_COLOMBIA = (0, 56, 168)
COLOR_ROJO_COLOMBIA = (206, 17, 38)
COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_ROJO = (255, 0, 0)
COLOR_VERDE = (0, 255, 0)
COLOR_GRIS_OSCURO = (50, 50, 50)
COLOR_GRIS_CLARO = (150, 150, 150)

# Rutas de assets
PATH_ASSETS = "assets"
PATH_MAIN_CHARACTERS = "MainCharacters"
PATH_TERRAIN = "Terrain"
PATH_TRAPS = "Traps"
PATH_BACKGROUND = "Background"