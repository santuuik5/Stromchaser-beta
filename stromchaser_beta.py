#!/usr/bin/env python3
"""
Stromchaser Beta - Un juego 2D de cazar tornados
Controles:
- Flechas o WASD: Mover el vehículo
- ESPACIO: Activar turbo
- ESC: Salir del juego
"""

import pygame
import random
import math

# Inicializar Pygame
pygame.init()

# Constantes del juego
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60

# Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL_CIELO = (135, 206, 235)
VERDE_CESPED = (34, 139, 34)
GRIS_OSCURO = (64, 64, 64)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)
NARANJA = (255, 165, 0)
GRIS_TORNADO = (128, 128, 128)
AZUL_VEHICULO = (70, 130, 180)

# Categorías de tornados (Escala Fujita Mejorada)
CATEGORIAS_TORNADO = {
    'EF0': {'velocidad_min': 105, 'velocidad_max': 137, 'radio_min': 30, 'radio_max': 50, 
            'color': (200, 200, 200), 'fuerza_ascenso': 3, 'daño': 1, 'nombre': 'Débil'},
    'EF1': {'velocidad_min': 138, 'velocidad_max': 177, 'radio_min': 40, 'radio_max': 60, 
            'color': (180, 180, 255), 'fuerza_ascenso': 5, 'daño': 1, 'nombre': 'Moderado'},
    'EF2': {'velocidad_min': 178, 'velocidad_max': 217, 'radio_min': 50, 'radio_max': 70, 
            'color': (100, 100, 255), 'fuerza_ascenso': 7, 'daño': 2, 'nombre': 'Significativo'},
    'EF3': {'velocidad_min': 218, 'velocidad_max': 266, 'radio_min': 60, 'radio_max': 80, 
            'color': (150, 50, 150), 'fuerza_ascenso': 9, 'daño': 2, 'nombre': 'Severo'},
    'EF4': {'velocidad_min': 267, 'velocidad_max': 322, 'radio_min': 70, 'radio_max': 90, 
            'color': (100, 0, 100), 'fuerza_ascenso': 11, 'daño': 3, 'nombre': 'Devastador'},
    'EF5': {'velocidad_min': 323, 'velocidad_max': 500, 'radio_min': 80, 'radio_max': 100, 
            'color': (50, 0, 50), 'fuerza_ascenso': 13, 'daño': 3, 'nombre': 'Increíble'}
}

class Vehiculo(pygame.sprite.Sprite):
    """Clase para el vehículo del jugador"""
    
    def __init__(self):
        super().__init__()
        # Crear superficie del vehículo
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        # Dibujar un vehículo simple
        pygame.draw.rect(self.image, AZUL_VEHICULO, (0, 10, 40, 20))
        pygame.draw.rect(self.image, GRIS_OSCURO, (5, 0, 30, 10))
        pygame.draw.circle(self.image, NEGRO, (10, 30), 5)
        pygame.draw.circle(self.image, NEGRO, (30, 30), 5)
        
        self.rect = self.image.get_rect()
        self.rect.center = (ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2)
        
        # Velocidad y movimiento
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.velocidad_max = 5
        self.turbo = False
        self.turbo_duracion = 0
        
        # Física de ascenso por tornados
        self.en_ascenso = False
        self.fuerza_ascenso = 0
        self.altura_ascenso = 0
        self.categoria_actual = None
        
    def aplicar_ascenso(self, fuerza, categoria):
        """Aplica fuerza de ascenso cuando el vehículo es atrapado por un tornado"""
        self.en_ascenso = True
        self.fuerza_ascenso = fuerza
        self.categoria_actual = categoria
        self.altura_ascenso = 0
        
    def update(self):
        # Si está en ascenso, aplicar física especial
        if self.en_ascenso:
            self.altura_ascenso += self.fuerza_ascenso
            self.rect.y -= self.fuerza_ascenso * 0.5  # Mover hacia arriba
            
            # Efecto de oscilación
            self.rect.x += math.sin(self.altura_ascenso * 0.1) * 2
            
            # Si alcanza cierta altura, liberar
            if self.altura_ascenso > 300:
                self.en_ascenso = False
                self.fuerza_ascenso = 0
                self.categoria_actual = None
                self.altura_ascenso = 0
            return
            
        # Movimiento con teclas (solo si no está en ascenso)
        teclas = pygame.key.get_pressed()
        
        self.velocidad_x = 0
        self.velocidad_y = 0
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.velocidad_x = -self.velocidad_max
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.velocidad_x = self.velocidad_max
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.velocidad_y = -self.velocidad_max
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.velocidad_y = self.velocidad_max
            
        # Turbo
        if teclas[pygame.K_SPACE] and self.turbo_duracion > 0:
            self.velocidad_x *= 1.5
            self.velocidad_y *= 1.5
            self.turbo_duracion -= 1
        elif not teclas[pygame.K_SPACE]:
            self.turbo_duracion = 60  # Recargar turbo
            
        # Actualizar posición
        self.rect.x += self.velocidad_x
        self.rect.y += self.velocidad_y
        
        # Mantener dentro de la pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > ANCHO_PANTALLA:
            self.rect.right = ANCHO_PANTALLA
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > ALTO_PANTALLA:
            self.rect.bottom = ALTO_PANTALLA


class Tornado(pygame.sprite.Sprite):
    """Clase para los tornados con categorías y física realista"""
    
    def __init__(self, nivel_juego=1):
        super().__init__()
        
        # Seleccionar categoría basada en el nivel del juego y probabilidad
        self.seleccionar_categoria(nivel_juego)
        
        # Crear superficie del tornado
        self.radio = random.randint(
            self.categoria['radio_min'], 
            self.categoria['radio_max']
        )
        self.image = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
        
        # Dibujar tornado (cono espiral) con color de categoría
        centro = self.radio
        for i in range(self.radio):
            angulo = i * 0.5 + self.radio * 0.1  # Rotación inicial
            x = centro + math.cos(angulo) * i
            y = centro + math.sin(angulo) * i * 0.5
            tamano = max(1, self.radio - i)
            # Usar color de la categoría con variación
            color_base = self.categoria['color']
            color = (
                max(0, min(255, color_base[0] + i % 30)),
                max(0, min(255, color_base[1] + i % 30)),
                max(0, min(255, color_base[2] + i % 30))
            )
            pygame.draw.circle(self.image, color, (int(x), int(y)), tamano)
            
        self.rect = self.image.get_rect()
        # Posición aleatoria fuera de la pantalla
        lado = random.choice(['izquierda', 'derecha', 'arriba', 'abajo'])
        if lado == 'izquierda':
            self.rect.x = -self.radio * 2
            self.rect.y = random.randint(0, ALTO_PANTALLA)
        elif lado == 'derecha':
            self.rect.x = ANCHO_PANTALLA + self.radio
            self.rect.y = random.randint(0, ALTO_PANTALLA)
        elif lado == 'arriba':
            self.rect.x = random.randint(0, ANCHO_PANTALLA)
            self.rect.y = -self.radio * 2
        else:
            self.rect.x = random.randint(0, ANCHO_PANTALLA)
            self.rect.y = ALTO_PANTALLA + self.radio
            
        # Movimiento del tornado - más rápido según categoría
        self.velocidad_x = random.uniform(-2, 2) + (self.nivel_ef * 0.3)
        self.velocidad_y = random.uniform(-2, 2) + (self.nivel_ef * 0.3)
        self.direccion_cambio = 0
        self.rotacion = 0
        self.velocidad_rotacion = random.uniform(5, 15) + (self.nivel_ef * 2)
        
    def seleccionar_categoria(self, nivel_juego):
        """Selecciona la categoría del tornado basada en el nivel"""
        # Probabilidades basadas en el nivel
        categorias_posibles = list(CATEGORIAS_TORNADO.keys())
        
        # A mayor nivel, más probabilidad de tornados fuertes
        if nivel_juego == 1:
            pesos = [50, 30, 15, 5, 0, 0]  # Principalmente EF0-EF1
        elif nivel_juego == 2:
            pesos = [30, 35, 20, 10, 5, 0]  # EF0-EF2
        elif nivel_juego == 3:
            pesos = [20, 25, 25, 20, 8, 2]  # EF1-EF3
        elif nivel_juego >= 4:
            pesos = [10, 15, 20, 25, 20, 10]  # Todos posibles
        
        self.nombre_categoria = random.choices(categorias_posibles, weights=pesos)[0]
        self.categoria = CATEGORIAS_TORNADO[self.nombre_categoria]
        self.nivel_ef = int(self.nombre_categoria[1])  # Extraer número (0-5)
        
    def update(self):
        self.rect.x += self.velocidad_x
        self.rect.y += self.velocidad_y
        
        # Rotar visualmente el tornado
        self.rotacion += self.velocidad_rotacion
        if self.rotacion >= 360:
            self.rotacion = 0
        
        # Cambiar dirección ocasionalmente
        self.direccion_cambio += 1
        if self.direccion_cambio > max(60, 120 - self.nivel_ef * 10):
            self.velocidad_x = random.uniform(-3, 3) + (self.nivel_ef * 0.5)
            self.velocidad_y = random.uniform(-3, 3) + (self.nivel_ef * 0.5)
            self.direccion_cambio = 0
            
        # Eliminar si está muy lejos
        if (self.rect.x < -200 or self.rect.x > ANCHO_PANTALLA + 200 or
            self.rect.y < -200 or self.rect.y > ALTO_PANTALLA + 200):
            self.kill()
    
    def aplicar_fisica_al_vehiculo(self, vehiculo):
        """Aplica la física de ascenso al vehículo cuando es atrapado"""
        # Calcular distancia al centro del tornado
        centro_tornado = self.rect.center
        centro_vehiculo = vehiculo.rect.center
        
        distancia = math.sqrt(
            (centro_tornado[0] - centro_vehiculo[0])**2 + 
            (centro_tornado[1] - centro_vehiculo[1])**2
        )
        
        # Si el vehículo está cerca del centro, es atrapado
        if distancia < self.radio * 0.7:
            vehiculo.aplicar_ascenso(
                self.categoria['fuerza_ascenso'],
                self.nombre_categoria
            )
            return True
        return False


class NubeLluvia(pygame.sprite.Sprite):
    """Nubes de lluvia para ambiente"""
    
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, GRIS_TORNADO, (0, 0, 60, 40))
        pygame.draw.ellipse(self.image, GRIS_TORNADO, (15, -10, 40, 40))
        pygame.draw.ellipse(self.image, GRIS_TORNADO, (30, 0, 50, 40))
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, ANCHO_PANTALLA)
        self.rect.y = random.randint(-100, 100)
        self.velocidad_y = random.uniform(0.5, 2)
        
    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.y > ALTO_PANTALLA:
            self.rect.y = -50
            self.rect.x = random.randint(0, ANCHO_PANTALLA)


class Juego:
    """Clase principal del juego"""
    
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Stromchaser Beta - Caza Tornados")
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.puntuacion = 0
        self.vidas = 3
        self.nivel = 1
        
        # Grupos de sprites
        self.todos_los_sprites = pygame.sprite.Group()
        self.tornados = pygame.sprite.Group()
        self.nubes = pygame.sprite.Group()
        
        # Jugador
        self.jugador = Vehiculo()
        self.todos_los_sprites.add(self.jugador)
        
        # Fuentes
        self.fuente = pygame.font.Font(None, 36)
        self.fuente_pequena = pygame.font.Font(None, 24)
        
        # Temporizadores
        self.spawn_tornado_timer = 0
        self.spawn_nube_timer = 0
        
    def spawn_tornado(self):
        tornado = Tornado(self.nivel)
        self.todos_los_sprites.add(tornado)
        self.tornados.add(tornado)
        
    def spawn_nubes(self):
        for _ in range(5):
            nube = NubeLluvia()
            self.todos_los_sprites.add(nube)
            self.nubes.add(nube)
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
                    
    def actualizar(self):
        # Spawn de tornados
        self.spawn_tornado_timer += 1
        if self.spawn_tornado_timer > max(60, 180 - self.nivel * 10):
            self.spawn_tornado()
            self.spawn_tornado_timer = 0
            
        # Spawn de nubes
        self.spawn_nube_timer += 1
        if self.spawn_nube_timer > 300:
            self.spawn_nubes()
            self.spawn_nube_timer = 0
            
        # Actualizar todos los sprites
        self.todos_los_sprites.update()
        
        # Verificar física de ascenso con cada tornado
        for tornado in self.tornados:
            if tornado.aplicar_fisica_al_vehiculo(self.jugador):
                # El vehículo está siendo levantado, sumar puntos por categoría
                categoria_info = CATEGORIAS_TORNADO[tornado.nombre_categoria]
                puntos_ascenso = (tornado.nivel_ef + 1) * 50
                self.puntuacion += puntos_ascenso
                # Eliminar tornado después de levantar el vehículo
                tornado.kill()
                break
        
        # Detectar colisiones laterales con tornados (daño)
        if not self.jugador.en_ascenso:
            colisiones = pygame.sprite.spritecollide(self.jugador, self.tornados, False)
            if colisiones:
                self.vidas -= 1
                # Eliminar tornado que golpeó
                for tornado in colisiones:
                    tornado.kill()
                    
                if self.vidas <= 0:
                    self.ejecutando = False
                    
        # Aumentar puntuación por sobrevivir
        self.puntuacion += 1
        if self.puntuacion % 500 == 0:
            self.nivel += 1
    
    def dibujar(self):
        # Fondo
        self.pantalla.fill(AZUL_CIELO)
        
        # Dibujar césped en la parte inferior
        pygame.draw.rect(self.pantalla, VERDE_CESPED, (0, ALTO_PANTALLA - 50, ANCHO_PANTALLA, 50))
        
        # Dibujar todos los sprites
        self.todos_los_sprites.draw(self.pantalla)
        
        # Dibujar interfaz de usuario
        texto_puntos = self.fuente.render(f"Puntos: {self.puntuacion}", True, NEGRO)
        texto_vidas = self.fuente.render(f"Vidas: {self.vidas}", True, ROJO)
        texto_nivel = self.fuente.render(f"Nivel: {self.nivel}", True, AMARILLO)
        
        self.pantalla.blit(texto_puntos, (10, 10))
        self.pantalla.blit(texto_vidas, (10, 50))
        self.pantalla.blit(texto_nivel, (ANCHO_PANTALLA - 150, 10))
        
        # Mostrar categoría del tornado si está en ascenso
        if self.jugador.en_ascenso and self.jugador.categoria_actual:
            categoria_nombre = CATEGORIAS_TORNADO[self.jugador.categoria_actual]['nombre']
            texto_ascenso = self.fuente.render(f"¡ASCENSO EF{self.jugador.categoria_actual[1]}! - {categoria_nombre}", True, NARANJA)
            self.pantalla.blit(texto_ascenso, (ANCHO_PANTALLA // 2 - 200, ALTO_PANTALLA // 2 - 100))
            
            # Barra de altura de ascenso
            altura_porcentaje = self.jugador.altura_ascenso / 300 * 100
            pygame.draw.rect(self.pantalla, GRIS_OSCURO, (ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA // 2 - 60, 200, 20))
            pygame.draw.rect(self.pantalla, AZUL_VEHICULO, (ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA // 2 - 60, int(200 * altura_porcentaje / 100), 20))
        
        # Instrucciones
        if self.puntuacion < 100:
            instrucciones = self.fuente_pequena.render("Usa WASD/Flechas para moverte - ESPACIO para turbo", True, NEGRO)
            self.pantalla.blit(instrucciones, (ANCHO_PANTALLA // 2 - 200, ALTO_PANTALLA - 40))
        
        pygame.display.flip()
    
    def ejecutar(self):
        while self.ejecutando:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)
        
        # Mostrar pantalla final
        self.mostrar_game_over()
        
    def mostrar_game_over(self):
        """Mostrar pantalla de game over"""
        self.pantalla.fill(NEGRO)
        texto_final = self.fuente.render("GAME OVER", True, ROJO)
        texto_puntos_final = self.fuente.render(f"Puntuación Final: {self.puntuacion}", True, BLANCO)
        texto_reiniciar = self.fuente_pequena.render("Presiona cualquier tecla para salir", True, BLANCO)
        
        self.pantalla.blit(texto_final, (ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA // 2 - 50))
        self.pantalla.blit(texto_puntos_final, (ANCHO_PANTALLA // 2 - 120, ALTO_PANTALLA // 2))
        self.pantalla.blit(texto_reiniciar, (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 + 50))
        
        pygame.display.flip()
        
        # Esperar antes de cerrar
        esperando = True
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT or evento.type == pygame.KEYDOWN:
                    esperando = False
        
        pygame.quit()


if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
