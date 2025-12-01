"""
Clases de entidades del juego: enemigos, balas, power-ups, boss
"""
import pygame
import random
import math
from config import *
from os.path import join


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


class BossBullet(pygame.sprite.Sprite):
    """Proyectil disparado por el boss"""
    
    def __init__(self, x, y, direccion):
        super().__init__()
        self.image = pygame.Surface((30, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, COLOR_ROJO, (0, 0, 30, 12))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 8 * direccion
        self.mask = pygame.mask.from_surface(self.image)
        self.dano = BOSS_DANO
    
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
        # Death animation state
        self.dying = False
        self.death_counter = 0
        self.death_duration = 18  # frames for death animation
        
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
        elif tipo == "mermelada":
            # Enemigo volador - frasco de mermelada con "alas" (placeholder)
            # Cuerpo redondo morado
            pygame.draw.ellipse(self.image, (160, 32, 240), (0, 0, width, height))
            # Tapa
            pygame.draw.rect(self.image, (200, 200, 200), (0, 0, width, height//4))
            # Ojos
            pygame.draw.circle(self.image, COLOR_BLANCO, (width//3, height//3), 5)
            pygame.draw.circle(self.image, COLOR_BLANCO, (2*width//3, height//3), 5)
            # Detalle 'mermelada' salpicada
            pygame.draw.circle(self.image, (255, 120, 120), (width//2, height//2 + 4), width//6)

            # Establecer características de vuelo (parámetros por defecto)
            self.velocidad = 1.5
            self.dano_al_jugador = 8
            self.fly_amplitude = 30
            self.fly_speed = 0.04 + random.random() * 0.03
            self.base_y = self.rect.y
            self.fly_phase = random.random() * 6.28
        
    def update(self, plataformas):
        """Actualiza el movimiento y comportamiento del enemigo"""
        # If enemy is dying we animate the death and then self.kill()
        if self.dying:
            self.death_counter += 1
            if self.death_counter >= self.death_duration:
                # Finaliza y quita el sprite
                self.kill()
            return
        # Movimiento horizontal básico
        # Si es tipo mermelada (volador) usamos un patrón de vuelo oscilatorio
        if self.tipo == "mermelada":
            # mover horizontalmente
            self.rect.x += int(self.velocidad * self.direccion)
            # movimiento vertical oscilante (seno) para volar
            self.fly_phase += self.fly_speed
            self.rect.y = int(self.base_y + self.fly_amplitude * math.sin(self.fly_phase))
            # cambiar dirección cuando se aleje de rango horizontal fijo
            if self.rect.left < 0 or self.rect.right > WIDTH * 4:
                self.direccion *= -1
            self.animation_count += 1
            return

        # Movimiento horizontal para enemigos tipo suelo
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
        """Dibuja al enemigo y su barra de vida. Si está en muerte, animamos un 'shrink'"""
        if self.dying:
            # scaling down over death_duration
            factor = max(0.01, 1.0 - (self.death_counter / self.death_duration))
            new_w = max(1, int(self.rect.width * factor))
            new_h = max(1, int(self.rect.height * factor))
            scaled = pygame.transform.scale(self.image, (new_w, new_h))
            # center scaled image inside original rect
            draw_x = self.rect.x - offset_x + (self.rect.width - new_w) // 2
            draw_y = self.rect.y + (self.rect.height - new_h) // 2
            win.blit(scaled, (draw_x, draw_y))
            return

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

    def start_death(self):
        """Iniciar animación de muerte (no borra inmediatamente; espera muerte animada)."""
        if not self.dying:
            self.dying = True
            self.death_counter = 0
            # bloquear colisiones mientras muere
            self.mask = None


class Boss(pygame.sprite.Sprite):
    """Boss final - Político corrupto gigante"""
    
    def __init__(self, x, y):
        super().__init__()
        # Aumentar tamaño del boss para que sea más imponente
        self.width = 240
        self.height = 300
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vida = BOSS_VIDA
        self.vida_maxima = BOSS_VIDA
        self.velocidad = BOSS_VELOCIDAD
        self.direccion = -1
        self.dano_al_jugador = BOSS_DANO
        
        # Estados de ataque
        self.puede_disparar = True
        self.tiempo_ultimo_disparo = 0
        self.cooldown_disparo = BOSS_COOLDOWN_DISPARO
        self.fase = 1  # Fase del boss (aumenta cuando pierde vida)
        
        # Crear sprite
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._crear_sprite()
        self.mask = pygame.mask.from_surface(self.image)
        
    def _crear_sprite(self):
        """Crea el sprite del boss: intenta cargar `assets/MainCharacters/Boss/boss.png`.
        Si no se encuentra, cae en el placeholder dibujado programáticamente.
        """
        try:
            path = join(PATH_ASSETS, PATH_MAIN_CHARACTERS, "Boss", "boss.png")
            img = pygame.image.load(path).convert_alpha()
            # escalar a las dimensiones del boss
            self.image = pygame.transform.scale(img, (self.width, self.height))
        except Exception:
            # Fallback: dibujar placeholder
            pygame.draw.rect(self.image, (40, 40, 40), (10, 30, 100, 120))
            pygame.draw.ellipse(self.image, (255, 200, 150), (30, 0, 60, 50))
            pygame.draw.polygon(self.image, COLOR_ROJO_COLOMBIA, [
                (60, 50), (50, 70), (70, 70)
            ])
            pygame.draw.circle(self.image, COLOR_ROJO, (45, 20), 8)
            pygame.draw.circle(self.image, COLOR_ROJO, (75, 20), 8)
            fuente = pygame.font.Font(None, 40)
            texto = fuente.render("$", True, COLOR_AMARILLO_COLOMBIA)
            self.image.blit(texto, (45, 80))
        
    def update(self, plataformas, player_pos):
        """Actualiza el comportamiento del boss"""
        # Determinar fase según vida
        if self.vida < self.vida_maxima * 0.3:
            self.fase = 3
            self.cooldown_disparo = 800  # Dispara más rápido
        elif self.vida < self.vida_maxima * 0.6:
            self.fase = 2
            self.cooldown_disparo = 1200
        
        # Movimiento básico
        nueva_x = self.rect.x + (self.velocidad * self.direccion)
        self.rect.x = nueva_x
        
        # Cambiar dirección en bordes
        if self.rect.left < WIDTH * 4 - 500 or self.rect.right > WIDTH * 4 + 500:
            self.direccion *= -1
        
        # Mirar hacia el jugador
        if player_pos < self.rect.centerx:
            self.direccion = -1
        else:
            self.direccion = 1
    
    def disparar(self, tiempo_actual):
        """
        Intenta disparar proyectiles
        
        Returns:
            list: Lista de balas creadas
        """
        if self.puede_disparar:
            self.puede_disparar = False
            self.tiempo_ultimo_disparo = tiempo_actual
            
            balas = []
            offset_y_positions = [self.rect.centery - 20, self.rect.centery, self.rect.centery + 20]
            
            # En fase 3, dispara 3 proyectiles
            if self.fase == 3:
                for offset_y in offset_y_positions:
                    balas.append(BossBullet(self.rect.centerx, offset_y, self.direccion))
            # En fase 2, dispara 2 proyectiles
            elif self.fase == 2:
                balas.append(BossBullet(self.rect.centerx, self.rect.centery - 15, self.direccion))
                balas.append(BossBullet(self.rect.centerx, self.rect.centery + 15, self.direccion))
            # En fase 1, dispara 1 proyectil
            else:
                balas.append(BossBullet(self.rect.centerx, self.rect.centery, self.direccion))
            
            return balas
        return []
    
    def actualizar_cooldown(self, tiempo_actual):
        """Actualiza el cooldown de disparo"""
        if not self.puede_disparar:
            if tiempo_actual - self.tiempo_ultimo_disparo > self.cooldown_disparo:
                self.puede_disparar = True
    
    def recibir_dano(self, cantidad):
        """
        Reduce la vida del boss
        
        Returns:
            bool: True si murió, False si sigue vivo
        """
        self.vida -= cantidad
        return self.vida <= 0
    
    def draw(self, win, offset_x):
        """Dibuja al boss y su barra de vida"""
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        
        # Barra de vida grande
        barra_ancho = 300
        barra_alto = 20
        barra_x = WIDTH // 2 - barra_ancho // 2
        barra_y = 20
        
        # Fondo
        pygame.draw.rect(win, (100, 0, 0), (barra_x, barra_y, barra_ancho, barra_alto))
        # Vida actual
        vida_ancho = (self.vida / self.vida_maxima) * barra_ancho
        pygame.draw.rect(win, COLOR_ROJO, (barra_x, barra_y, vida_ancho, barra_alto))
        # Borde
        pygame.draw.rect(win, COLOR_BLANCO, (barra_x, barra_y, barra_ancho, barra_alto), 3)
        
        # Texto de vida del boss
        fuente = pygame.font.Font(None, 24)
        texto = fuente.render(f"BOSS: {int(self.vida)}/{self.vida_maxima}", True, COLOR_BLANCO)
        win.blit(texto, (barra_x + barra_ancho // 2 - texto.get_width() // 2, barra_y - 25))


class PowerUp(pygame.sprite.Sprite):
    """Power-ups recolectables"""
    
    def __init__(self, x, y, tipo="municion"):
        super().__init__()
        self.tipo = tipo
        self.width = 40
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Crear sprite según tipo
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._crear_sprite()
        self.mask = pygame.mask.from_surface(self.image)
        
        # Efectos
        self.animation_count = 0
        
    def _crear_sprite(self):
        """Crea el sprite del power-up"""
        if self.tipo == "municion":
            # Caja de balas (amarillo)
            pygame.draw.rect(self.image, COLOR_AMARILLO_COLOMBIA, (5, 5, 30, 30))
            pygame.draw.rect(self.image, COLOR_NEGRO, (5, 5, 30, 30), 2)
        elif self.tipo == "vida":
            # Corazón (rojo)
            pygame.draw.polygon(self.image, COLOR_ROJO, [
                (20, 10), (10, 5), (5, 10), (5, 20), (20, 35),
                (35, 20), (35, 10), (30, 5), (20, 10)
            ])
        elif self.tipo == "cafe":
            # Taza de café (velocidad)
            pygame.draw.rect(self.image, (101, 67, 33), (10, 15, 20, 20))
            pygame.draw.arc(self.image, (101, 67, 33), (25, 20, 10, 10), 0, 3.14, 2)
    
    def loop(self):
        """Animación de flotación"""
        self.animation_count += 1
        offset = int(3 * pygame.math.Vector2(0, 1).rotate(self.animation_count * 2).y)
        self.rect.y += offset * 0.1
        
    def draw(self, win, offset_x):
        """Dibuja el power-up"""
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))