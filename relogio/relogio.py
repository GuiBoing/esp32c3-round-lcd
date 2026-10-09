import math
import time
from machine import Pin, SPI
import gc9d01

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - relógio analógico com ponteiros + hora digital
VERSAO = "v1.0.0"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

# Cores RGB565 com os bytes invertidos (framebuf é little-endian)
PRETO = 0x0000
BRANCO = 0xFFFF
VERMELHO = 0x00F8
CINZA = 0x1084
CIANO = 0xFF07

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

def desenha(hora, minuto, segundo):
    display.fill(PRETO)

    # Mostrador: borda e 12 marcações (maiores em 12, 3, 6 e 9)
    display.ellipse(CX, CY, 78, 78, CINZA)
    for i in range(12):
        x1, y1 = ponto(i * 30, 64 if i % 3 == 0 else 70)
        x2, y2 = ponto(i * 30, 76)
        display.line(x1, y1, x2, y2, BRANCO)

    # Hora digital embaixo do centro
    display.text("{:02d}:{:02d}".format(hora, minuto), 60, 112, CIANO)

    # Ponteiros
    ponteiro((hora % 12) * 30 + minuto / 2, 38, BRANCO, True)
    ponteiro(minuto * 6 + segundo / 10, 58, BRANCO, True)
    ponteiro(segundo * 6, 66, VERMELHO)
    display.ellipse(CX, CY, 3, 3, VERMELHO, True)

    display.show()

# Mostra a versão no serial e na tela
print("relogio", VERSAO)
display.fill(PRETO)
display.text("relogio", 52, 68, BRANCO)
display.text(VERSAO, 80 - len(VERSAO) * 4, 84, BRANCO)
display.show()
time.sleep(2)

ultimo = -1
while True:
    t = time.localtime()
    if t[5] != ultimo:
        ultimo = t[5]
        desenha(t[3], t[4], t[5])
    time.sleep_ms(50)
