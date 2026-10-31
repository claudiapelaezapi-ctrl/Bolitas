import pygame
import sys
import random
import math
import pyttsx3
import threading

# Inicializar pygame y el mezclador de sonido
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

# --- CONFIGURACIÓN DE VOLUMEN INDEPENDIENTE ---
VOLUMEN_MUSICA = 0.05  # <--- Modifica este valor (entre 0.0 y 1.0) para subir o bajar solo la música

# Inicializar motor de voz forzando la voz en español (ID 1: Helena)
def hablar(texto):
    def _proceso_voz():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 135)  # Velocidad más lenta y clara
            
            voices = engine.getProperty('voices')
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)  # Forzar ID 1 (Español)
                    
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            pass
    threading.Thread(target=_proceso_voz, daemon=True).start()

# --- GENERADOR DE MELODÍA DE FONDO (SINTETIZADOR) ---
def generar_melodia_fondo():
    sample_rate = 22050
    notas = [220, 261.63, 329.63, 392.00, 440, 523.25, 392.00, 329.63]
    duracion_nota = 0.18
    n_samples = int(sample_rate * duracion_nota)
    
    buf = bytearray()
    for nota in notas:
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = int(50 * math.sin(2 * math.pi * nota * t) + 25 * math.sin(2 * math.pi * (nota * 1.5) * t))
            buf.append(val & 0xFF)
            buf.append(val & 0xFF)
            
    return pygame.mixer.Sound(buffer=bytes(buf))

try:
    musica_fondo = generar_melodia_fondo()
    musica_fondo.set_volume(VOLUMEN_MUSICA)
    musica_fondo.play(loops=-1)
except Exception:
    pass

# Configuración de la pantalla
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Cyber Tic-Tac-Toe - Con Melodía y Voz en Español")

# Colores Neón / Futuristas
NEGRO = (10, 5, 20)
AZUL_NEON = (0, 255, 255)
ROJO_NEON = (255, 0, 100)
VERDE_NEON = (0, 255, 128)
AMARILLO_NEON = (255, 255, 0)
BLANCO = (255, 255, 255)
GRIS_BOTON = (50, 40, 80)

# Fuentes
fuente = pygame.font.SysFont("Courier New", 18, bold=True)
fuente_titulo = pygame.font.SysFont("Courier New", 30, bold=True)

# Variables del juego
estado_juego = "MENU" 
modo_seleccionado = None 
dificultad = "IMPOSIBLE" 
nombre_opcion2_actual = "Usuario 1"

tablero = [["" for _ in range(3)] for _ in range(3)]
turno = "X" 
mensaje_ganador = ""
linea_ganadora_info = None

victorias_x = 0
victorias_o = 0
empates = 0
tiempo_espera_pc = 0

offset_grid = 0
estrellas = [[random.randint(0, ANCHO), random.randint(0, ALTO), random.choice([1, 2])] for _ in range(60)]

def generar_tono(frecuencia, duracion_ms, tipo="sine"):
    sample_rate = 22050
    n_samples = int(sample_rate * (duracion_ms / 1000.0))
    buf = bytearray()
    for i in range(n_samples):
        t = float(i) / sample_rate
        if tipo == "sine":
            val = int(100 * math.sin(2 * math.pi * frecuencia * t))
        elif tipo == "square":
            val = 100 if math.sin(2 * math.pi * frecuencia * t) > 0 else -100
        buf.append(val & 0xFF)
        buf.append(val & 0xFF)
    return pygame.mixer.Sound(buffer=bytes(buf))

snd_clic = generar_tono(440, 50, "sine")
snd_pc = generar_tono(880, 70, "sine")
snd_victoria = generar_tono(587, 250, "square")

class Boton:
    def __init__(self, x, y, w, h, texto, color_base, color_hover):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = color_hover

    def dibujar(self, superficie):
        mouse_pos = pygame.mouse.get_pos()
        color_actual = self.color_hover if self.rect.collidepoint(mouse_pos) else self.color_base
        pygame.draw.rect(superficie, color_actual, self.rect, border_radius=8)
        pygame.draw.rect(superficie, BLANCO, self.rect, 2, border_radius=8)
        txt_surface = fuente.render(self.texto, True, BLANCO)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        superficie.blit(txt_surface, txt_rect)

    def clic(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                snd_clic.play()
                return True
        return False

btn_modo1 = Boton(200, 160, 400, 45, "1. PC contra Usuario", GRIS_BOTON, AZUL_NEON)
btn_modo2 = Boton(200, 220, 400, 45, "2. PC vs Usuario 1 o 2 (Azar)", GRIS_BOTON, ROJO_NEON)
btn_modo3 = Boton(200, 280, 400, 45, "3. Usuario 1 con Usuario 2", GRIS_BOTON, VERDE_NEON)
btn_dificultad = Boton(200, 350, 400, 45, f"Dificultad IA: {dificultad}", (40, 40, 100), AMARILLO_NEON)
btn_salir_menu = Boton(200, 420, 400, 45, "Salir", (80, 20, 20), (200, 50, 50))

btn_reinicio = Boton(50, 520, 180, 45, "Reiniciar", (20, 60, 60), AZUL_NEON)
btn_salir_juego = Boton(570, 520, 180, 45, "Menú / Salir", (80, 20, 20), (200, 50, 50))

def reiniciar_tablero():
    global tablero, turno, mensaje_ganador, linea_ganadora_info, nombre_opcion2_actual
    tablero = [["" for _ in range(3)] for _ in range(3)]
    mensaje_ganador = ""
    linea_ganadora_info = None
    turno = "X"
    if modo_seleccionado == 2:
        nombre_opcion2_actual = random.choice(["Usuario 1", "Usuario 2"])
    hablar("Nueva partida iniciada")

def obtener_nombre_jugador(simbolo):
    if modo_seleccionado == 1:
        return f"Usuario ({simbolo})" if simbolo == "X" else f"PC ({simbolo})"
    elif modo_seleccionado == 2:
        return f"{nombre_opcion2_actual} ({simbolo})" if simbolo == "X" else f"PC ({simbolo})"
    else: 
        return f"Usuario 1 ({simbolo})" if simbolo == "X" else f"Usuario 2 ({simbolo})"

def verificar_ganador_detalle(b):
    global linea_ganadora_info
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] and b[i][0] != "":
            linea_ganadora_info = ("fila", i)
            return b[i][0]
    for i in range(3):
        if b[0][i] == b[1][i] == b[2][i] and b[0][i] != "":
            linea_ganadora_info = ("columna", i)
            return b[0][i]
    if b[0][0] == b[1][1] == b[2][2] and b[0][0] != "":
        linea_ganadora_info = ("diagonal_principal", 0)
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] and b[0][2] != "":
        linea_ganadora_info = ("diagonal_secundaria", 0)
        return b[0][2]
    if all(b[r][c] != "" for r in range(3) for c in range(3)):
        return "EMPATE"
    return None

def verificar_ganador_simulacion(b):
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] and b[i][0] != "": return b[i][0]
        if b[0][i] == b[1][i] == b[2][i] and b[0][i] != "": return b[0][i]
    if b[0][0] == b[1][1] == b[2][2] and b[0][0] != "": return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] and b[0][2] != "": return b[0][2]
    if all(b[r][c] != "" for r in range(3) for c in range(3)): return "EMPATE"
    return None

def minimax(b, profundidad, es_maximizando):
    res = verificar_ganador_simulacion(b)
    if res == "O": return 10
    if res == "X": return -10
    if res == "EMPATE": return 0

    if es_maximizando:
        mejor = -float('inf')
        for r in range(3):
            for c in range(3):
                if b[r][c] == "":
                    b[r][c] = "O"
                    puntaje = minimax(b, profundidad + 1, False)
                    b[r][c] = ""
                    mejor = max(puntaje, mejor)
        return mejor
    else:
        mejor = float('inf')
        for r in range(3):
            for c in range(3):
                if b[r][c] == "":
                    b[r][c] = "X"
                    puntaje = minimax(b, profundidad + 1, True)
                    b[r][c] = ""
                    mejor = min(puntaje, mejor)
        return mejor

def movimiento_pc_decision():
    vacias = [(r, c) for r in range(3) for c in range(3) if tablero[r][c] == ""]
    if not vacias: return None

    if dificultad == "FACIL":
        return random.choice(vacias)
    else: 
        mejor_puntaje = -float('inf')
        mejor_movimiento = None
        for r, c in vacias:
            tablero[r][c] = "O"
            puntaje = minimax(tablero, 0, False)
            tablero[r][c] = ""
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_movimiento = (r, c)
        return mejor_movimiento

reloj = pygame.time.Clock()

while True:
    reloj.tick(60)
    offset_grid = (offset_grid + 1) % 40

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if estado_juego == "MENU":
            if btn_modo1.clic(evento):
                modo_seleccionado = 1
                victorias_x, victorias_o, empates = 0, 0, 0
                reiniciar_tablero()
                estado_juego = "JUGANDO"
            elif btn_modo2.clic(evento):
                modo_seleccionado = 2
                victorias_x, victorias_o, empates = 0, 0, 0
                reiniciar_tablero()
                estado_juego = "JUGANDO"
            elif btn_modo3.clic(evento):
                modo_seleccionado = 3
                victorias_x, victorias_o, empates = 0, 0, 0
                reiniciar_tablero()
                estado_juego = "JUGANDO"
            elif btn_dificultad.clic(evento):
                dificultad = "FACIL" if dificultad == "IMPOSIBLE" else "IMPOSIBLE"
                btn_dificultad.texto = f"Dificultad IA: {dificultad}"
            elif btn_salir_menu.clic(evento):
                pygame.quit()
                sys.exit()

        elif estado_juego == "JUGANDO":
            if btn_reinicio.clic(evento):
                reiniciar_tablero()
            elif btn_salir_juego.clic(evento):
                estado_juego = "MENU"

            es_turno_pc = (modo_seleccionado in [1, 2]) and turno == "O"
            
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not mensaje_ganador and not es_turno_pc:
                mouse_x, mouse_y = evento.pos
                if 250 <= mouse_x <= 550 and 150 <= mouse_y <= 450:
                    col = (mouse_x - 250) // 100
                    fila = (mouse_y - 150) // 100
                    if 0 <= fila < 3 and 0 <= col < 3 and tablero[fila][col] == "":
                        tablero[fila][col] = turno
                        snd_clic.play()
                        res = verificar_ganador_detalle(tablero)
                        if res:
                            snd_victoria.play()
                            if res == "EMPATE":
                                mensaje_ganador = "¡Empate!"
                                hablar("Empate")
                                empates += 1
                            else:
                                gan = obtener_nombre_jugador(res)
                                mensaje_ganador = f"¡Ganador: {gan}!"
                                hablar(f"Ganador {gan}")
                                if res == "X": victorias_x += 1
                                else: victorias_o += 1
                        else:
                            turno = "O" if turno == "X" else "X"
                            tiempo_espera_pc = pygame.time.get_ticks()

    es_turno_pc = (modo_seleccionado in [1, 2]) and turno == "O"
    if estado_juego == "JUGANDO" and not mensaje_ganador and es_turno_pc:
        if pygame.time.get_ticks() - tiempo_espera_pc > 1000:
            mov = movimiento_pc_decision()
            if mov:
                tablero[mov[0]][mov[1]] = "O"
                snd_pc.play()
                res = verificar_ganador_detalle(tablero)
                if res:
                    snd_victoria.play()
                    if res == "EMPATE":
                        mensaje_ganador = "¡Empate!"
                        hablar("Empate")
                        empates += 1
                    else:
                        gan = obtener_nombre_jugador(res)
                        mensaje_ganador = f"¡Ganador: {gan}!"
                        hablar(f"Ganador {gan}")
                        if res == "X": victorias_x += 1
                        else: victorias_o += 1
                else:
                    turno = "X"

    pantalla.fill(NEGRO)

    for estrella in estrellas:
        estrella[1] += estrella[2]
        if estrella[1] > ALTO:
            estrella[1] = 0
            estrella[0] = random.randint(0, ANCHO)
        pygame.draw.circle(pantalla, AZUL_NEON, (estrella[0], estrella[1]), estrella[2])

    for x in range(0, ANCHO, 40):
        x_pos = (x + offset_grid) % ANCHO
        pygame.draw.line(pantalla, (20, 10, 40), (x_pos, 0), (x_pos, ALTO), 1)
    for y in range(0, ALTO, 40):
        y_pos = (y + offset_grid) % ALTO
        pygame.draw.line(pantalla, (20, 10, 40), (0, y_pos), (ANCHO, y_pos), 1)

    if estado_juego == "MENU":
        titulo = fuente_titulo.render("CYBER ARCADE: TRES EN RAYA", True, AZUL_NEON)
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 80)))
        btn_modo1.dibujar(pantalla)
        btn_modo2.dibujar(pantalla)
        btn_modo3.dibujar(pantalla)
        btn_dificultad.dibujar(pantalla)
        btn_salir_menu.dibujar(pantalla)

    elif estado_juego == "JUGANDO":
        nombres_modos = {
            1: f"PC vs Usuario ({dificultad})",
            2: f"PC vs {nombre_opcion2_actual} ({dificultad})",
            3: "Usuario 1 vs Usuario 2"
        }
        txt_modo = fuente.render(f"Modo: {nombres_modos[modo_seleccionado]}", True, AMARILLO_NEON)
        pantalla.blit(txt_modo, txt_modo.get_rect(center=(ANCHO // 2, 25)))

        if modo_seleccionado == 1:
            nombre_x = "Usuario (X)"
            nombre_o = "PC (O)"
        elif modo_seleccionado == 2:
            nombre_x = f"{nombre_opcion2_actual} (X)"
            nombre_o = "PC (O)"
        else:
            nombre_x = "Usuario 1 (X)"
            nombre_o = "Usuario 2 (O)"

        txt_marcador = fuente.render(f"{nombre_x}: {victorias_x}  |  Empates: {empates}  |  {nombre_o}: {victorias_o}", True, BLANCO)
        pantalla.blit(txt_marcador, txt_marcador.get_rect(center=(ANCHO // 2, 60)))

        if mensaje_ganador:
            txt_turno = fuente_titulo.render(mensaje_ganador, True, ROJO_NEON)
        else:
            nombre_turno_actual = obtener_nombre_jugador(turno)
            txt_turno = fuente.render(f"Turno de: {nombre_turno_actual}", True, VERDE_NEON if turno == "O" else AZUL_NEON)
        pantalla.blit(txt_turno, txt_turno.get_rect(center=(ANCHO // 2, 105)))

        for i in range(1, 3):
            pygame.draw.line(pantalla, AZUL_NEON, (250 + i * 100, 150), (250 + i * 100, 450), 4)
            pygame.draw.line(pantalla, AZUL_NEON, (250, 150 + i * 100), (550, 150 + i * 100), 4)

        for fila in range(3):
            for col in range(3):
                val = tablero[fila][col]
                centro_x = 250 + col * 100 + 50
                centro_y = 150 + fila * 100 + 50
                if val == "X":
                    pygame.draw.line(pantalla, ROJO_NEON, (centro_x - 30, centro_y - 30), (centro_x + 30, centro_y + 30), 6)
                    pygame.draw.line(pantalla, ROJO_NEON, (centro_x - 30, centro_y + 30), (centro_x + 30, centro_y - 30), 6)
                elif val == "O":
                    pygame.draw.circle(pantalla, VERDE_NEON, (centro_x, centro_y), 32, 6)

        if linea_ganadora_info:
            tipo, idx = linea_ganadora_info
            if tipo == "fila":
                y_linea = 150 + idx * 100 + 50
                pygame.draw.line(pantalla, AMARILLO_NEON, (260, y_linea), (540, y_linea), 8)
            elif tipo == "columna":
                x_linea = 250 + idx * 100 + 50
                pygame.draw.line(pantalla, AMARILLO_NEON, (x_linea, 160), (x_linea, 440), 8)
            elif tipo == "diagonal_principal":
                pygame.draw.line(pantalla, AMARILLO_NEON, (260, 160), (540, 440), 8)
            elif tipo == "diagonal_secundaria":
                pygame.draw.line(pantalla, AMARILLO_NEON, (540, 160), (260, 440), 8)

        btn_reinicio.dibujar(pantalla)
        btn_salir_juego.dibujar(pantalla)

    pygame.display.flip()