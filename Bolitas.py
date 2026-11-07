import pygame
import sys
import random
import math
import pyttsx3
import threading

# Inicializar pygame y el mezclador de sonido
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)

# --- CONFIGURACIÓN DE VOLUMEN INDEPENDIENTE PARA LA MÚSICA ---
VOLUMEN_MUSICA = 0.15  # Cambia este valor entre 0.0 y 1.0 para ajustar solo la música

# Motor de voz en español (Fuerza ID 1: Helena)
def hablar(texto):
    def _proceso_voz():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 135)
            voices = engine.getProperty('voices')
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            engine.say(texto)
            engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=_proceso_voz, daemon=True).start()

# --- GENERADOR DE MELODÍA DE FONDO (SINTETIZADOR) ---
def generar_melodia_fondo():
    sample_rate = 22050
    notas = [196.00, 246.94, 293.66, 349.23, 392.00, 440.00, 349.23, 293.66]
    duracion_nota = 0.2
    n_samples = int(sample_rate * duracion_nota)
    
    buf = bytearray()
    for nota in notas:
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = int(45 * math.sin(2 * math.pi * nota * t) + 20 * math.sin(2 * math.pi * (nota * 0.5) * t))
            buf.append(val & 0xFF)
            buf.append(val & 0xFF)
    return pygame.mixer.Sound(buffer=bytes(buf))

try:
    musica_fondo = generar_melodia_fondo()
    musica_fondo.set_volume(VOLUMEN_MUSICA)
    musica_fondo.play(loops=-1)
except Exception:
    pass

# Configuración de pantalla
ANCHO = 800
ALTO = 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Cyber Conecta 4 - Fondo Amarillo Neón")

# Colores con Fondo Amarillo
AMARILLO_FONDO = (255, 235, 59)      # Fondo amarillo vibrante
LINEAS_GRID = (220, 190, 20)        # Líneas de fondo sutiles
AZUL_OSCURO = (15, 25, 60)          # Texto y acentos de alta visibilidad
ROJO_NEON = (220, 20, 80)           # Ficha X
VERDE_NEON = (0, 160, 90)           # Ficha O (ajustado para contraste en amarillo)
AZUL_NEON = (0, 120, 220)           # Acentos
AMARILLO_ALERTA = (200, 150, 0)     # Textos destacados
BLANCO = (255, 255, 255)
GRIS_BOTON = (40, 40, 60)           # Botones oscuros para que resalte el texto blanco
AZUL_TABLERO = (20, 35, 90)

# Fuentes
fuente = pygame.font.SysFont("Courier New", 18, bold=True)
fuente_titulo = pygame.font.SysFont("Courier New", 28, bold=True)

# Variables del juego
estado_juego = "MENU"
modo_seleccionado = None
dificultad = "IMPOSIBLE"
nombre_opcion2_actual = "Usuario 1"

# Tablero de Conecta 4: 6 filas x 7 columnas
FILAS = 6
COLS = 7
tablero = [["" for _ in range(COLS)] for _ in range(FILAS)]
turno = "X"
mensaje_ganador = ""
linea_ganadora_info = None

victorias_x = 0
victorias_o = 0
empates = 0
tiempo_espera_pc = 0

offset_grid = 0
estrellas = [[random.randint(0, ANCHO), random.randint(0, ALTO), random.choice([1, 2])] for _ in range(70)]

# Efectos de sonido sintéticos
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
snd_ficha = generar_tono(660, 80, "sine")
snd_pc = generar_tono(880, 70, "sine")
snd_victoria = generar_tono(587, 300, "square")

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
        pygame.draw.rect(superficie, AZUL_OSCURO, self.rect, 2, border_radius=8)
        txt_surface = fuente.render(self.texto, True, BLANCO)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        superficie.blit(txt_surface, txt_rect)

    def clic(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                snd_clic.play()
                return True
        return False

# Botones del Menú Principal
btn_modo1 = Boton(200, 180, 400, 45, "1. PC contra Usuario", GRIS_BOTON, AZUL_NEON)
btn_modo2 = Boton(200, 245, 400, 45, "2. PC vs Usuario 1 o 2 (Azar)", GRIS_BOTON, ROJO_NEON)
btn_modo3 = Boton(200, 310, 400, 45, "3. Usuario 1 con Usuario 2", GRIS_BOTON, VERDE_NEON)
btn_dificultad = Boton(200, 375, 400, 45, f"Dificultad IA: {dificultad}", (40, 40, 100), AMARILLO_ALERTA)
btn_salir_menu = Boton(200, 440, 400, 45, "Salir", (80, 20, 20), (200, 50, 50))

btn_reinicio = Boton(50, 630, 180, 45, "Reiniciar", GRIS_BOTON, AZUL_NEON)
btn_salir_juego = Boton(570, 630, 180, 45, "Menú / Salir", (80, 20, 20), (200, 50, 50))

def reiniciar_tablero():
    global tablero, turno, mensaje_ganador, linea_ganadora_info, nombre_opcion2_actual
    tablero = [["" for _ in range(COLS)] for _ in range(FILAS)]
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
    # Horizontal
    for r in range(FILAS):
        for c in range(COLS - 3):
            if b[r][c] == b[r][c+1] == b[r][c+2] == b[r][c+3] and b[r][c] != "":
                linea_ganadora_info = ("H", r, c)
                return b[r][c]
    # Vertical
    for r in range(FILAS - 3):
        for c in range(COLS):
            if b[r][c] == b[r+1][c] == b[r+2][c] == b[r+3][c] and b[r][c] != "":
                linea_ganadora_info = ("V", r, c)
                return b[r][c]
    # Diagonal positiva
    for r in range(3, FILAS):
        for c in range(COLS - 3):
            if b[r][c] == b[r-1][c+1] == b[r-2][c+2] == b[r-3][c+3] and b[r][c] != "":
                linea_ganadora_info = ("DP", r, c)
                return b[r][c]
    # Diagonal negativa
    for r in range(FILAS - 3):
        for c in range(COLS - 3):
            if b[r][c] == b[r+1][c+1] == b[r+2][c+2] == b[r+3][c+3] and b[r][c] != "":
                linea_ganadora_info = ("DN", r, c)
                return b[r][c]
                
    if all(b[0][c] != "" for c in range(COLS)):
        return "EMPATE"
    return None

def soltar_ficha(b, col, simbolo):
    for r in range(FILAS - 1, -1, -1):
        if b[r][col] == "":
            b[r][col] = simbolo
            return r
    return None

def evaluar_ventana(ventana, pieza):
    puntaje = 0
    pieza_op = "X" if pieza == "O" else "O"
    if ventana.count(pieza) == 4:
        puntaje += 100
    elif ventana.count(pieza) == 3 and ventana.count("") == 1:
        puntaje += 5
    elif ventana.count(pieza) == 2 and ventana.count("") == 2:
        puntaje += 2
    if ventana.count(pieza_op) == 3 and ventana.count("") == 1:
        puntaje -= 4
    return puntaje

def puntuar_tablero(b, pieza):
    puntaje = 0
    centro_col = [b[r][COLS//2] for r in range(FILAS)]
    puntaje += centro_col.count(pieza) * 3

    for r in range(FILAS):
        fila_arr = b[r]
        for c in range(COLS - 3):
            ventana = fila_arr[c:c+4]
            puntaje += evaluar_ventana(ventana, pieza)
    for c in range(COLS):
        col_arr = [b[r][c] for r in range(FILAS)]
        for r in range(FILAS - 3):
            ventana = col_arr[r:r+4]
            puntaje += evaluar_ventana(ventana, pieza)
    return puntaje

def minimax(b, profundidad, alfa, beta, es_maximizando):
    val_terminal = verificar_ganador_detalle(b)
    if val_terminal == "O": return (None, 100000)
    if val_terminal == "X": return (None, -100000)
    if val_terminal == "EMPATE" or profundidad == 0: return (None, puntuar_tablero(b, "O"))

    columnas_validas = [c for c in range(COLS) if b[0][c] == ""]
    if es_maximizando:
        mejor_puntaje = -float('inf')
        mejor_col = random.choice(columnas_validas)
        for c in columnas_validas:
            b_copia = [fila[:] for fila in b]
            soltar_ficha(b_copia, c, "O")
            _, puntaje = minimax(b_copia, profundidad - 1, alfa, beta, False)
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_col = c
            alfa = max(alfa, mejor_puntaje)
            if beta <= alfa: break
        return mejor_col, mejor_puntaje
    else:
        mejor_puntaje = float('inf')
        mejor_col = random.choice(columnas_validas)
        for c in columnas_validas:
            b_copia = [fila[:] for fila in b]
            soltar_ficha(b_copia, c, "X")
            _, puntaje = minimax(b_copia, profundidad - 1, alfa, beta, True)
            if puntaje < mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_col = c
            beta = min(beta, mejor_puntaje)
            if beta <= alfa: break
        return mejor_col, mejor_puntaje

def movimiento_pc_decision():
    columnas_validas = [c for c in range(COLS) if tablero[0][c] == ""]
    if not columnas_validas: return None
    if dificultad == "FACIL":
        return random.choice(columnas_validas)
    else:
        col, _ = minimax(tablero, 3, -float('inf'), float('inf'), True)
        return col if col is not None else random.choice(columnas_validas)

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
                if 125 <= mouse_x <= 675 and 150 <= mouse_y <= 600:
                    col = (mouse_x - 125) // 80
                    if 0 <= col < COLS:
                        fila_puesta = soltar_ficha(tablero, col, turno)
                        if fila_puesta is not None:
                            snd_ficha.play()
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

    # Turno automatizado de la PC
    es_turno_pc = (modo_seleccionado in [1, 2]) and turno == "O"
    if estado_juego == "JUGANDO" and not mensaje_ganador and es_turno_pc:
        if pygame.time.get_ticks() - tiempo_espera_pc > 500:
            col_pc = movimiento_pc_decision()
            if col_pc is not None:
                soltar_ficha(tablero, col_pc, "O")
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

    # Dibujar fondo amarillo neón
    pantalla.fill(AMARILLO_FONDO)
    for estrella in estrellas:
        estrella[1] += estrella[2]
        if estrella[1] > ALTO:
            estrella[1] = 0
            estrella[0] = random.randint(0, ANCHO)
        pygame.draw.circle(pantalla, LINEAS_GRID, (estrella[0], estrella[1]), estrella[2])

    for x in range(0, ANCHO, 40):
        x_pos = (x + offset_grid) % ANCHO
        pygame.draw.line(pantalla, LINEAS_GRID, (x_pos, 0), (x_pos, ALTO), 1)
    for y in range(0, ALTO, 40):
        y_pos = (y + offset_grid) % ALTO
        pygame.draw.line(pantalla, LINEAS_GRID, (0, y_pos), (ANCHO, y_pos), 1)

    if estado_juego == "MENU":
        titulo = fuente_titulo.render("CYBER ARCADE: CONECTA 4", True, AZUL_OSCURO)
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
        txt_modo = fuente.render(f"Modo: {nombres_modos[modo_seleccionado]}", True, AZUL_OSCURO)
        pantalla.blit(txt_modo, txt_modo.get_rect(center=(ANCHO // 2, 20)))

        if modo_seleccionado == 1:
            nombre_x = "Usuario (X)"
            nombre_o = "PC (O)"
        elif modo_seleccionado == 2:
            nombre_x = f"{nombre_opcion2_actual} (X)"
            nombre_o = "PC (O)"
        else:
            nombre_x = "Usuario 1 (X)"
            nombre_o = "Usuario 2 (O)"

        txt_marcador = fuente.render(f"{nombre_x}: {victorias_x}  |  Empates: {empates}  |  {nombre_o}: {victorias_o}", True, AZUL_OSCURO)
        pantalla.blit(txt_marcador, txt_marcador.get_rect(center=(ANCHO // 2, 50)))

        if mensaje_ganador:
            txt_turno = fuente_titulo.render(mensaje_ganador, True, ROJO_NEON)
        else:
            nombre_turno_actual = obtener_nombre_jugador(turno)
            txt_turno = fuente.render(f"Turno de: {nombre_turno_actual}", True, AZUL_OSCURO)
        pantalla.blit(txt_turno, txt_turno.get_rect(center=(ANCHO // 2, 85)))

        # Dibujar tablero de Conecta 4
        ancho_tablero = COLS * 80
        alto_tablero = FILAS * 80
        inicio_x = (ANCHO - ancho_tablero) // 2
        inicio_y = 150

        pygame.draw.rect(pantalla, AZUL_TABLERO, (inicio_x, inicio_y, ancho_tablero, alto_tablero), border_radius=12)
        pygame.draw.rect(pantalla, AZUL_OSCURO, (inicio_x, inicio_y, ancho_tablero, alto_tablero), 3, border_radius=12)

        # Dibujar agujeros y fichas
        for r in range(FILAS):
            for c in range(COLS):
                centro_x = inicio_x + c * 80 + 40
                centro_y = inicio_y + r * 80 + 40
                val = tablero[r][c]
                
                if val == "X":
                    color_ficha = ROJO_NEON
                elif val == "O":
                    color_ficha = VERDE_NEON
                else:
                    color_ficha = (235, 220, 40) # Hueco oscuro sobre fondo amarillo

                pygame.draw.circle(pantalla, color_ficha, (centro_x, centro_y), 30)
                pygame.draw.circle(pantalla, AZUL_OSCURO, (centro_x, centro_y), 30, 2)

        # Línea láser de victoria
        if linea_ganadora_info:
            tipo, r_ini, c_ini = linea_ganadora_info
            if tipo == "H":
                x1 = inicio_x + c_ini * 80 + 40
                y1 = inicio_y + r_ini * 80 + 40
                x2 = inicio_x + (c_ini + 3) * 80 + 40
                y2 = y1
                pygame.draw.line(pantalla, ROJO_NEON, (x1, y1), (x2, y2), 8)
            elif tipo == "V":
                x1 = inicio_x + c_ini * 80 + 40
                y1 = inicio_y + r_ini * 80 + 40
                x2 = x1
                y2 = inicio_y + (r_ini + 3) * 80 + 40
                pygame.draw.line(pantalla, ROJO_NEON, (x1, y1), (x2, y2), 8)
            elif tipo == "DP":
                x1 = inicio_x + c_ini * 80 + 40
                y1 = inicio_y + r_ini * 80 + 40
                x2 = inicio_x + (c_ini + 3) * 80 + 40
                y2 = inicio_y + (r_ini - 3) * 80 + 40
                pygame.draw.line(pantalla, ROJO_NEON, (x1, y1), (x2, y2), 8)
            elif tipo == "DN":
                x1 = inicio_x + c_ini * 80 + 40
                y1 = inicio_y + r_ini * 80 + 40
                x2 = inicio_x + (c_ini + 3) * 80 + 40
                y2 = inicio_y + (r_ini + 3) * 80 + 40
                pygame.draw.line(pantalla, ROJO_NEON, (x1, y1), (x2, y2), 8)

        btn_reinicio.dibujar(pantalla)
        btn_salir_juego.dibujar(pantalla)

    pygame.display.flip()