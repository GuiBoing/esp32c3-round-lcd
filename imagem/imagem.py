from machine import Pin, SPI
import gc9d01

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - mostra imagem.raw (160x160 RGB565) na tela
VERSAO = "v1.0.0"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

print("imagem", VERSAO)

# Lê o arquivo cru direto no buffer do display
with open("imagem.raw", "rb") as f:
    f.readinto(display.buffer)
display.show()
