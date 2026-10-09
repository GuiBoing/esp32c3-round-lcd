import time
from machine import Pin, SPI
import gc9d01

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - círculo, retângulo e textos de teste
# v1.1.0 - alterna branco/preto a cada 3 s + Sleep Out no driver
# v1.2.0 - mostra a versão ao iniciar
# v1.3.0 - init completo do GC9D01 (corrige branco acinzentado)
VERSAO = "v1.3.0"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

BRANCO = 0xFFFF
PRETO = 0x0000

# Mostra a versão no serial e na tela
print("teste-tela", VERSAO)
display.fill(PRETO)
display.text("teste-tela", 40, 68, BRANCO)
display.text(VERSAO, 80 - len(VERSAO) * 4, 84, BRANCO)
display.show()
time.sleep(2)

# Alterna entre branco máximo e preto absoluto a cada 3 segundos
while True:
    display.fill(BRANCO)
    display.show()
    time.sleep(3)
    display.fill(PRETO)
    display.show()
    time.sleep(3)
