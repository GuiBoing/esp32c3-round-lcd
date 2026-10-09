import math
import time
from machine import Pin, SPI
import gc9d01

# Porte do exemplo Waveshare 07_Clock
# Precisa do arquivo mostrador.raw na placa (160x160 RGB565)
# Histórico de versões (atualize a cada mudança)
# v1.0.0 - mostrador do demo como fundo + ponteiros desenhados por cima
VERSAO = "v1.0.0"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

# Cores RGB565 com os bytes invertidos (framebuf é little-endian)
BRANCO = 0xFFFF
VERMELHO = 0x00F8
VERDE = 0xE007

CX = 80
CY = 80

def ponto(angulo, raio):
    # Ângulo em graus, 0 = 12 horas, sentido horário
    rad = math.radians(angulo)
    return CX + round(raio * math.sin(rad)), CY - round(raio * math.cos(rad))

def ponteiro(angulo, comprimento, cor, grosso=False):
    x, y = ponto(angulo, comprimento)
    display.line(CX, CY, x, y, cor)
    if grosso:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            display.line(CX + dx, CY + dy, x + dx, y + dy, cor)

print("07_relogio", VERSAO)

fundo = open("mostrador.raw", "rb")

ultimo = -1
while True:
    t = time.localtime()
    if t[5] != ultimo:
        ultimo = t[5]
        hora, minuto, segundo = t[3], t[4], t[5]

        # Recarrega o mostrador do arquivo para apagar os ponteiros antigos
        fundo.seek(0)
        fundo.readinto(display.buffer)

        ponteiro((hora % 12) * 30 + minuto / 2, 32, BRANCO, True)
        ponteiro(minuto * 6 + segundo / 10, 48, VERDE, True)
        ponteiro(segundo * 6, 54, VERMELHO)
        display.ellipse(CX, CY, 3, 3, VERMELHO, True)

        display.show()
    time.sleep_ms(50)
