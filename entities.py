"""
Clases de entidades del juego: enemigos, balas, etc.
"""
import pygame
from config import *


class Bullet(pygame.sprite.Sprite):
    """Proyectil disparado por el jugador"""
    
    def __init__(self, x, y, direccion):
        super().__init__()
        self.image = pygame.Surface((20, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, COLOR_AMARILLO_COLOMBIA, (0, 0, 20, 8))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = BULLET_VELOCIDAD * direccion
        self.mask = pygame.mask.from_surface(self.image)
        self.dano = BULLET_DANO
    
    def update(self):
        """Actualiza la posición de la bala"""
        self.rect.x += self.velocidad
    
    def draw(self, win, offset_x):
        """Dibuja la bala en pantalla"""
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Enemy(pygame.sprite.Sprite):
    """Enemigo base - Maletines y contratos corruptos"""
    
    ANIMATION_DELAY = 5
    
    def __init__(self, x, y, width, height, tipo="maletin"):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.tipo = tipo
        self.vida = ENEMY_VIDA
        self.vida_maxima = ENEMY_VIDA
        self.velocidad = ENEMY_VELOCIDAD
        self.direccion = -1
        self.animation_count = 0
        
        # Crear sprite según el tipo
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self._crear_sprite(width, height, tipo)
        
        self.mask = pygame.mask.from_surface(self.image)
        self.dano_al_jugador = ENEMY_DANO
    
    def _crear_sprite(self, width, height, tipo):
        """Crea el sprite visual del enemigo (placeholder)"""
        if tipo == "maletin":
            # Maletín café con detalles
            pygame.draw.rect(self.image, (101, 67, 33), (0, 10, width, height-20))
            pygame.draw.rect(self.image, (139, 90, 43), (5, 15, width-10, height-30))
            # "Piernas"
            pygame.draw.rect(self.image, (50, 50, 50), (10, height-12, 8, 12))
            pygame.draw.rect(self.image, (50, 50, 50), (width-18, height-12, 8, 12))
        elif tipo == "contrato":
            # Papel volador
            pygame.draw.rect(self.image, COLOR_BLANCO, (5, 0, width-10, height))
            pygame.draw.line(self.image, COLOR_NEGRO, (10, 15), (width-10, 15), 2)
            pygame.draw.line(self.image, COLOR_NEGRO, (10, 25), (width-10, 25), 2)
        
    def update(self, plataformas):
        """Actualiza el movimiento y comportamiento del enemigo"""
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
            check_x = self.rect.centerx + (self.direccion * self.rect.width // 2 + self.direccion * 5)
            check_y = self.rect.bottom + 10
            hay_suelo_adelante = False
            
            for plataforma in plataformas:
                if plataforma.rect.collidepoint(check_x, check_y):
                    hay_suelo_adelante = True
                    break
            
            if not hay_suelo_adelante:
                self.direccion *= -1
        
        # Cambiar dirección en bordes del mundo
        if self.rect.left < 0 or self.rect.right > WIDTH * 4:
            self.direccion *= -1
            
        self.animation_count += 1
        
    def recibir_dano(self, cantidad):
        """
        Reduce la vida del enemigo
        
        Returns:
            bool: True si murió, False si sigue vivo
        """
        self.vida -= cantidad
        return self.vida <= 0
    
    def draw(self, win, offset_x):
        """Dibuja al enemigo y su barra de vida"""
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        
        # Barra de vida
        if self.vida < self.vida_maxima:
            barra_ancho = self.rect.width
            barra_alto = 5
            barra_x = self.rect.x - offset_x
            barra_y = self.rect.y - 10
            # Fondo rojo
            pygame.draw.rect(win, COLOR_ROJO, (barra_x, barra_y, barra_ancho, barra_alto))
            # Vida verde
            vida_ancho = (self.vida / self.vida_maxima) * barra_ancho
            pygame.draw.rect(win, COLOR_VERDE, (barra_x, barra_y, vida_ancho, barra_alto))