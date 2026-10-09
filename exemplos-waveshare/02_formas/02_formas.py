import math
import random
import time
from array import array
from machine import Pin, SPI
import gc9d01

# Porte do exemplo Waveshare 02_Shapes_on_Circular_Display
# Histórico de versões (atualize a cada mudança)
# v1.0.0 - quadrado, triângulo e círculo com cores aleatórias a cada 3 s
VERSAO = "v1.0.0"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

BRANCO = 0xFFFF

CX = 80
CY = 80
RAIO = 80

def cor_aleatoria():
    r = random.getrandbits(8)
    g = random.getrandbits(8)
    b = random.getrandbits(8)
    cor = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    # Inverte os bytes (framebuf é little-endian)
    return ((cor & 0xFF) << 8) | (cor >> 8)

def quadrado():
    # A diagonal do quadrado é o diâmetro da tela
    lado = int(RAIO * math.sqrt(2))
    display.fill_rect(CX - lado // 2, CY - lado // 2, lado, lado, cor_aleatoria())

def triangulo():
    altura = int(RAIO * math.sqrt(3) / 2)
    lado = int(2 * RAIO * math.sin(math.pi / 3))
    pontos = array('h', [
        CX, CY - RAIO,
        CX - lado // 2, CY + altura // 2,
        CX + lado // 2, CY + altura // 2,
    ])
    display.poly(0, 0, pontos, cor_aleatoria(), True)

def circulo():
    display.ellipse(CX, CY, 30, 30, cor_aleatoria(), True)

print("02_formas", VERSAO)

display.fill(BRANCO)
display.show()

while True:
    for forma in (quadrado, triangulo, circulo):
        forma()
        display.show()
        time.sleep(3)
