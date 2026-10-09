import time
from machine import Pin, SPI
import gc9d01

# Porte dos exemplos Waveshare 04_Animated_Eye2 e 05_Animated_Eye12 (Demo_2)
# Precisa do arquivo olho.raw na placa (12 quadros de 160x160 RGB565)
# Histórico de versões (atualize a cada mudança)
# v1.0.0 - animação de 12 quadros em loop, com medição de FPS no serial
VERSAO = "v1.0.0"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

QUADROS = 12
ATRASO_MS = 70 # frameTime do exemplo original

print("04_olho_animado", VERSAO)

with open("olho.raw", "rb") as f:
    while True:
        inicio = time.ticks_ms()
        f.seek(0)
        for _ in range(QUADROS):
            # Cada quadro é lido direto no buffer do display
            f.readinto(display.buffer)
            display.show()
            time.sleep_ms(ATRASO_MS)
        tempo = time.ticks_diff(time.ticks_ms(), inicio)
        print("FPS: {:.1f}".format(QUADROS * 1000 / tempo))
