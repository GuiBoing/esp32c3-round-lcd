import time

import framebuf
from machine import Pin, SPI
import gc9d01

# Porte do exemplo Waveshare 01_Text_and_Number_Display
# Histórico de versões (atualize a cada mudança)
# v1.0.0 - troca de cores, texto e contador 00-99 em números grandes
VERSAO = "v1.0.0"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

# Cores RGB565 com os bytes invertidos (framebuf é little-endian)
BRANCO = 0xFFFF
AZUL = 0x1F00
VERMELHO = 0x00F8
VERDE = 0xE007
FUNDO = 0xFF04 # 0x04FF do exemplo original

def texto_grande(texto, x, y, escala, cor, fundo):
    # A fonte do framebuf é fixa em 8x8; amplia desenhando um quadrado por pixel
    largura = len(texto) * 8
    fb = framebuf.FrameBuffer(bytearray(largura), largura, 8, framebuf.MONO_HLSB)
    fb.text(texto, 0, 0, 1)
    display.fill_rect(x, y, largura * escala, 8 * escala, fundo)
    for py in range(8):
        for px in range(largura):
            if fb.pixel(px, py):
                display.fill_rect(x + px * escala, y + py * escala, escala, escala, cor)

print("01_texto_numero", VERSAO)

# Transição de cores
for cor in (AZUL, VERMELHO, VERDE):
    display.fill(cor)
    display.show()
    time.sleep(1)

display.fill(FUNDO)
display.text("Hello, Waveshare!", 12, 40, BRANCO)

numero = 0
while True:
    # Contador de dois dígitos, de 00 a 99
    texto_grande("{:02d}".format(numero), 32, 62, 6, BRANCO, FUNDO)
    display.show()
    numero = (numero + 1) % 100
    time.sleep(1)
