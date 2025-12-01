import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Corruption Run")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
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
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        
        # Nuevas propiedades para combate
        self.vida = 100
        self.vida_maxima = 100
        self.municion = 50
        self.municion_maxima = 50
        self.puede_disparar = True
        self.tiempo_ultimo_disparo = 0
        self.cooldown_disparo = 200  # milisegundos

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.recibir_dano(10)

    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0
    
    def disparar(self, tiempo_actual):
        if self.municion > 0 and self.puede_disparar:
            self.municion -= 1
            self.puede_disparar = False
            self.tiempo_ultimo_disparo = tiempo_actual
            # Crear bala en la dirección correcta
            direccion = 1 if self.direction == "right" else -1
            offset_x = 30 if self.direction == "right" else -30
            return Bullet(self.rect.centerx + offset_x, self.rect.centery, direccion)
        return None
    
    def actualizar_cooldown(self, tiempo_actual):
        if not self.puede_disparar:
            if tiempo_actual - self.tiempo_ultimo_disparo > self.cooldown_disparo:
                self.puede_disparar = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direccion):
        super().__init__()
        self.image = pygame.Surface((20, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 223, 0), (0, 0, 20, 8))  # Amarillo Colombia
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 12 * direccion
        self.mask = pygame.mask.from_surface(self.image)
        self.dano = 25
    
    def update(self):
        self.rect.x += self.velocidad
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Enemy(pygame.sprite.Sprite):
    ANIMATION_DELAY = 5
    
    def __init__(self, x, y, width, height, tipo="maletin"):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.tipo = tipo
        self.vida = 50
        self.vida_maxima = 50
        self.velocidad = 2
        self.direccion = -1
        self.animation_count = 0
        
        # Crear sprite simple (placeholder hasta tener sprites propios)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        if tipo == "maletin":
            # Maletín café con detalles
            pygame.draw.rect(self.image, (101, 67, 33), (0, 10, width, height-20))
            pygame.draw.rect(self.image, (139, 90, 43), (5, 15, width-10, height-30))
            # "Piernas"
            pygame.draw.rect(self.image, (50, 50, 50), (10, height-12, 8, 12))
            pygame.draw.rect(self.image, (50, 50, 50), (width-18, height-12, 8, 12))
        elif tipo == "contrato":
            # Papel volador
            pygame.draw.rect(self.image, (255, 255, 255), (5, 0, width-10, height))
            pygame.draw.line(self.image, (0, 0, 0), (10, 15), (width-10, 15), 2)
            pygame.draw.line(self.image, (0, 0, 0), (10, 25), (width-10, 25), 2)
        
        self.mask = pygame.mask.from_surface(self.image)
        self.dano_al_jugador = 15
        
    def update(self, plataformas):
        # Movimiento horizontal
        nueva_x = self.rect.x + (self.velocidad * self.direccion)
        self.rect.x = nueva_x
        
        # Colisión horizontal con plataformas
        colision_horizontal = False
        for plataforma in plataformas:
            if pygame.sprite.collide_mask(self, plataforma):
                # Retroceder y cambiar dirección
                self.rect.x -= self.velocidad * self.direccion
                self.direccion *= -1
                colision_horizontal = True
                break
        
        # Detectar borde de plataforma (para no caerse)
        if not colision_horizontal:
            # Verificar si hay suelo adelante
            check_x = self.rect.centerx + (self.direccion * self.rect.width // 2 + self.direccion * 5)
            check_y = self.rect.bottom + 10
            hay_suelo_adelante = False
            
            for plataforma in plataformas:
                if plataforma.rect.collidepoint(check_x, check_y):
                    hay_suelo_adelante = True
                    break
            
            # Si no hay suelo adelante, cambiar dirección
            if not hay_suelo_adelante:
                self.direccion *= -1
        
        # Cambiar dirección en bordes del mundo
        if self.rect.left < 0 or self.rect.right > WIDTH * 4:
            self.direccion *= -1
            
        self.animation_count += 1
        
    def recibir_dano(self, cantidad):
        self.vida -= cantidad
        return self.vida <= 0
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        # Barra de vida
        if self.vida < self.vida_maxima:
            barra_ancho = self.rect.width
            barra_alto = 5
            barra_x = self.rect.x - offset_x
            barra_y = self.rect.y - 10
            # Fondo rojo
            pygame.draw.rect(win, (255, 0, 0), (barra_x, barra_y, barra_ancho, barra_alto))
            # Vida verde
            vida_ancho = (self.vida / self.vida_maxima) * barra_ancho
            pygame.draw.rect(win, (0, 255, 0), (barra_x, barra_y, vida_ancho, barra_alto))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw_hud(window, player, puntuacion, combo):
    """Dibuja la interfaz de usuario"""
    fuente = pygame.font.Font(None, 36)
    fuente_pequeña = pygame.font.Font(None, 28)
    
    # Vida (superior izquierda)
    texto_vida = fuente.render(f"Vida: {player.vida}/{player.vida_maxima}", True, (255, 255, 255))
    window.blit(texto_vida, (10, 10))
    
    # Barra de vida visual
    barra_x, barra_y = 10, 45
    barra_ancho, barra_alto = 200, 20
    pygame.draw.rect(window, (100, 0, 0), (barra_x, barra_y, barra_ancho, barra_alto))
    vida_actual = (player.vida / player.vida_maxima) * barra_ancho
    pygame.draw.rect(window, (255, 0, 0), (barra_x, barra_y, vida_actual, barra_alto))
    pygame.draw.rect(window, (255, 255, 255), (barra_x, barra_y, barra_ancho, barra_alto), 2)
    
    # Munición (inferior derecha)
    texto_municion = fuente.render(f"Munición: {player.municion}", True, (255, 255, 255))
    window.blit(texto_municion, (WIDTH - 250, HEIGHT - 50))
    
    # Puntuación (superior derecha)
    texto_puntos = fuente.render(f"Puntos: {puntuacion}", True, (255, 223, 0))
    window.blit(texto_puntos, (WIDTH - 250, 10))
    
    # Combo (superior centro)
    if combo > 1:
        texto_combo = fuente.render(f"COMBO x{combo}", True, (255, 100, 0))
        combo_x = WIDTH // 2 - texto_combo.get_width() // 2
        window.blit(texto_combo, (combo_x, 10))


def draw_menu(window):
    """Dibuja el menú principal"""
    window.fill((20, 20, 40))  # Fondo azul oscuro
    
    # Título del juego
    fuente_titulo = pygame.font.Font(None, 100)
    fuente_subtitulo = pygame.font.Font(None, 40)
    fuente_opciones = pygame.font.Font(None, 50)
    
    # Título con colores de Colombia
    titulo = fuente_titulo.render("CORRUPTION RUN", True, (255, 223, 0))  # Amarillo
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, 150))
    window.blit(titulo, titulo_rect)
    
    # Subtítulo
    subtitulo = fuente_subtitulo.render("Huye de la corrupción", True, (255, 255, 255))
    subtitulo_rect = subtitulo.get_rect(center=(WIDTH // 2, 230))
    window.blit(subtitulo, subtitulo_rect)
    
    # Opciones del menú
    opciones = [
        "JUGAR",
        "INSTRUCCIONES",
        "SALIR"
    ]
    
    mouse_pos = pygame.mouse.get_pos()
    opcion_seleccionada = None
    
    for i, opcion in enumerate(opciones):
        y_pos = 350 + i * 80
        
        # Detectar hover
        texto = fuente_opciones.render(opcion, True, (255, 255, 255))
        texto_rect = texto.get_rect(center=(WIDTH // 2, y_pos))
        
        if texto_rect.collidepoint(mouse_pos):
            # Efecto hover - texto más grande y amarillo
            texto = fuente_opciones.render(opcion, True, (255, 223, 0))
            # Dibujar rectángulo detrás
            pygame.draw.rect(window, (50, 50, 50), texto_rect.inflate(40, 20), border_radius=10)
            opcion_seleccionada = i
        
        window.blit(texto, texto_rect)
    
    # Créditos
    fuente_pequeña = pygame.font.Font(None, 24)
    creditos = fuente_pequeña.render("Presiona ESC en cualquier momento para volver al menú", True, (150, 150, 150))
    creditos_rect = creditos.get_rect(center=(WIDTH // 2, HEIGHT - 30))
    window.blit(creditos, creditos_rect)
    
    pygame.display.update()
    return opcion_seleccionada


def draw_instructions(window):
    """Dibuja la pantalla de instrucciones"""
    window.fill((20, 20, 40))
    
    fuente_titulo = pygame.font.Font(None, 80)
    fuente_texto = pygame.font.Font(None, 36)
    fuente_pequeña = pygame.font.Font(None, 28)
    
    # Título
    titulo = fuente_titulo.render("INSTRUCCIONES", True, (255, 223, 0))
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
            # Títulos en amarillo
            texto = fuente_texto.render(linea, True, (255, 223, 0))
        elif linea.startswith("•"):
            # Bullets en blanco más pequeño
            texto = fuente_pequeña.render(linea, True, (200, 200, 200))
        else:
            texto = fuente_texto.render(linea, True, (255, 255, 255))
        
        texto_rect = texto.get_rect(center=(WIDTH // 2, y_pos))
        window.blit(texto, texto_rect)
        y_pos += 35
    
    # Botón volver
    fuente_boton = pygame.font.Font(None, 50)
    mouse_pos = pygame.mouse.get_pos()
    
    volver_texto = fuente_boton.render("VOLVER", True, (255, 255, 255))
    volver_rect = volver_texto.get_rect(center=(WIDTH // 2, HEIGHT - 80))
    
    if volver_rect.collidepoint(mouse_pos):
        volver_texto = fuente_boton.render("VOLVER", True, (255, 223, 0))
        pygame.draw.rect(window, (50, 50, 50), volver_rect.inflate(40, 20), border_radius=10)
    
    window.blit(volver_texto, volver_rect)
    
    pygame.display.update()
    return volver_rect.collidepoint(mouse_pos)


def menu_principal(window):
    """Loop del menú principal"""
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(60)
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
    """Loop de la pantalla de instrucciones"""
    clock = pygame.time.Clock()
    
    while True:
        clock.tick(60)
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
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)
    
    for bullet in bullets:
        bullet.draw(window, offset_x)
    
    for enemy in enemies:
        enemy.draw(window, offset_x)

    player.draw(window, offset_x)
    
    draw_hud(window, player, puntuacion, combo)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
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

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


def main(window):
    # Mostrar menú principal primero
    while True:
        accion = menu_principal(window)
        
        if accion == "salir":
            pygame.quit()
            quit()
        elif accion == "jugar":
            resultado = jugar(window)
            if resultado == "salir":
                pygame.quit()
                quit()
            # Si resultado es "menu", vuelve al loop del menú


def jugar(window):
    """Función principal del juego"""
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    
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
        
        # Trampas
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
    
    # Grupo de balas
    bullets = pygame.sprite.Group()
    
    # Variables de juego
    puntuacion = 0
    combo = 0
    ultimo_golpe_tiempo = 0
    combo_timeout = 2000  # 2 segundos para mantener combo

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)
        tiempo_actual = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_ESCAPE:
                    return "menu"  # Volver al menú
        
        # Disparar con click izquierdo o Ctrl
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        if mouse_buttons[0] or keys[pygame.K_LCTRL]:
            bala = player.disparar(tiempo_actual)
            if bala:
                bullets.add(bala)
        
        player.actualizar_cooldown(tiempo_actual)

        # Actualizar todo
        player.loop(FPS)
        fire.loop()
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
                    puntuacion += 100 * (combo + 1)
                    combo += 1
                    ultimo_golpe_tiempo = tiempo_actual
                bullet.kill()
                break
        
        # Reset combo si pasa mucho tiempo
        if tiempo_actual - ultimo_golpe_tiempo > combo_timeout and combo > 0:
            combo = 0
        
        # Colisiones jugador-enemigos
        enemigos_tocados = pygame.sprite.spritecollide(player, enemies, False)
        for enemigo in enemigos_tocados:
            player.recibir_dano(enemigo.dano_al_jugador)
            combo = 0  # Perder combo al recibir daño
        
        # Game Over
        if player.vida <= 0:
            fuente_grande = pygame.font.Font(None, 72)
            fuente_mediana = pygame.font.Font(None, 48)
            
            # Pantalla de Game Over
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            window.blit(overlay, (0, 0))
            
            texto_game_over = fuente_grande.render("GAME OVER", True, (255, 0, 0))
            texto_puntos = fuente_mediana.render(f"Puntuación Final: {puntuacion}", True, (255, 223, 0))
            texto_continuar = fuente_mediana.render("Presiona ESC para volver al menú", True, (255, 255, 255))
            
            window.blit(texto_game_over, (WIDTH//2 - texto_game_over.get_width()//2, HEIGHT//2 - 100))
            window.blit(texto_puntos, (WIDTH//2 - texto_puntos.get_width()//2, HEIGHT//2))
            window.blit(texto_continuar, (WIDTH//2 - texto_continuar.get_width()//2, HEIGHT//2 + 80))
            
            pygame.display.update()
            
            # Esperar input del jugador
            esperando = True
            while esperando:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "salir"
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return "menu"
                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            return "menu"

        draw(window, background, bg_image, player, objects, bullets, enemies, offset_x, puntuacion, combo)

        # Scroll de cámara
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
    
    return "menu"


if __name__ == "__main__":
    main(window)