"""
Clase del jugador con todas sus mecánicas
"""
import pygame
from config import *
from utils import load_sprite_sheets


class Player(pygame.sprite.Sprite):
    """Jugador principal - Político corrupto huyendo"""
    
    COLOR = (255, 0, 0)
    ANIMATION_DELAY = 3
    SPRITES = None  # Se cargará en __init__

    def __init__(self, x, y, width, height):
        super().__init__()
        
        # Cargar sprites si no se han cargado aún
        if Player.SPRITES is None:
            Player.SPRITES = load_sprite_sheets(PATH_MAIN_CHARACTERS, "MaskDude", 32, 32, True)
        
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
        # Speed boost properties (coffee power-up)
        self.speed_multiplier = 1.0
        self.speed_boost_end_time = 0  # pygame ticks when boost expires
        
        # Propiedades de combate
        self.vida = PLAYER_VIDA_INICIAL
        self.vida_maxima = PLAYER_VIDA_INICIAL
        self.municion = PLAYER_MUNICION_INICIAL
        self.municion_maxima = PLAYER_MUNICION_INICIAL
        self.puede_disparar = True
        self.tiempo_ultimo_disparo = 0
        self.cooldown_disparo = COOLDOWN_DISPARO
        
        # Inicializar sprite
        self.sprite = self.SPRITES["idle_left"][0]
        self.update()

    def jump(self):
        """Hace que el jugador salte"""
        self.y_vel = -PLAYER_GRAVITY * PLAYER_JUMP_FORCE
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        """Mueve al jugador por diferencial"""
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self, cantidad=10):
        """Marca al jugador como golpeado y aplica daño.

        cantidad: cantidad de daño a aplicar (por defecto 10, usado por las llamas).
        """
        self.hit = True
        self.recibir_dano(cantidad)

    def recibir_dano(self, cantidad):
        """Reduce la vida del jugador"""
        self.vida -= cantidad
        if self.vida < 0:
            self.vida = 0
    
    def disparar(self, tiempo_actual):
        """
        Intenta disparar un proyectil
        
        Returns:
            Bullet o None si no puede disparar
        """
        from entities import Bullet  # Import aquí para evitar circular
        
        if self.municion > 0 and self.puede_disparar:
            self.municion -= 1
            self.puede_disparar = False
            self.tiempo_ultimo_disparo = tiempo_actual
            
            direccion = 1 if self.direction == "right" else -1
            offset_x = 30 if self.direction == "right" else -30
            return Bullet(self.rect.centerx + offset_x, self.rect.centery, direccion)
        return None
    
    def actualizar_cooldown(self, tiempo_actual):
        """Actualiza el cooldown de disparo"""
        if not self.puede_disparar:
            if tiempo_actual - self.tiempo_ultimo_disparo > self.cooldown_disparo:
                self.puede_disparar = True

    def apply_speed_boost(self, duration_ms: int = 10000, multiplier: float = 1.5, tiempo_actual: int | None = None):
        """Apply a temporary speed boost to the player.

        duration_ms: duration in milliseconds
        multiplier: factor to multiply PLAYER_VEL
        tiempo_actual: optional current time (pygame ticks). If None use pygame.time.get_ticks().
        """
        if tiempo_actual is None:
            tiempo_actual = pygame.time.get_ticks()
        self.speed_multiplier = multiplier
        self.speed_boost_end_time = tiempo_actual + duration_ms

    def update_speed_boost(self, tiempo_actual: int):
        """Expire speed boost when the time is reached."""
        if self.speed_multiplier != 1.0 and tiempo_actual >= self.speed_boost_end_time:
            self.speed_multiplier = 1.0
            self.speed_boost_end_time = 0

    def get_speed(self) -> int:
        """Get the current horizontal speed the player should use (int)."""
        return int(PLAYER_VEL * self.speed_multiplier)

    def move_left(self, vel):
        """Mueve al jugador a la izquierda"""
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        """Mueve al jugador a la derecha"""
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        """Loop principal de actualización del jugador"""
        self.y_vel += min(1, (self.fall_count / fps) * PLAYER_GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        """Marca que el jugador ha aterrizado"""
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        """Marca que el jugador golpeó algo con la cabeza"""
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        """Actualiza el sprite según el estado actual"""
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > PLAYER_GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        """Actualiza el rectángulo y la máscara de colisión"""
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        """Dibuja al jugador en pantalla"""
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))