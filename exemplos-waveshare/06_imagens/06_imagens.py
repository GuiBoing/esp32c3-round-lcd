import time
from machine import Pin, SPI
import gc9d01

# Porte do exemplo Waveshare 06_Image_Display
# Precisa dos arquivos A1.raw a A4.raw na placa (160x160 RGB565)
# Histórico de versões (atualize a cada mudança)
# v1.0.0 - mostra as 4 imagens do demo, 3 s cada (o original mostra só a A3)
VERSAO = "v1.0.0"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

IMAGENS = ("A1.raw", "A2.raw", "A3.raw", "A4.raw")

print("06_imagens", VERSAO)

while True:
    for nome in IMAGENS:
        # Lê o arquivo cru direto no buffer do display
        with open(nome, "rb") as f:
            f.readinto(display.buffer)
        display.show()
        time.sleep(3)
