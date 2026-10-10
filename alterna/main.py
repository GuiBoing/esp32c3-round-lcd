import gc
import os
import sys
import time

import machine
from machine import Pin

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - alterna entre imagem.py e mensagem-wifi.py pelo botão BOOT
# v1.1.0 - mensagens de depuração no serial a cada passo da troca
VERSAO = "v1.1.0"

# Mostra no serial cada passo da troca (False para desligar)
DEBUG = True

# Programas que o botão percorre, nesta ordem (precisam estar na placa)
PROGRAMAS = ("imagem.py", "mensagem-wifi.py","imagem-bluetooth.py")

# Guarda qual programa está em uso, para voltar nele ao religar
ARQUIVO = "programa.txt"

# Botão BOOT: GPIO9, vai a 0 quando apertado
botao = Pin(9, Pin.IN, Pin.PULL_UP)

try:
    with open(ARQUIVO) as f:
        indice = int(f.read()) % len(PROGRAMAS)
except (OSError, ValueError):
    indice = 0

def debug(*partes):
    if DEBUG:
        print("[alterna %d ms]" % time.ticks_ms(), *partes)

def troca(pino):
    pino.irq(handler=None)
    proximo = (indice + 1) % len(PROGRAMAS)
    debug("1/4 botao apertado, proximo:", PROGRAMAS[proximo])
    with open(ARQUIVO, "w") as f:
        f.write(str(proximo))
    debug("2/4 gravou", ARQUIVO)
    # Só reinicia depois de soltar, para o GPIO9 não estar apertado no boot
    while pino.value() == 0:
        time.sleep_ms(10)
    debug("3/4 botao solto")
    time.sleep_ms(50)
    debug("4/4 reiniciando")
    machine.reset()

botao.irq(troca, Pin.IRQ_FALLING)

print("alterna", VERSAO, "->", PROGRAMAS[indice])
debug("motivo do ultimo reinicio:", machine.reset_cause())
debug("memoria livre:", gc.mem_free(), "botao:", botao.value())
for nome in PROGRAMAS + ("gc9d01.py", "imagem.raw"):
    if nome not in os.listdir():
        debug("FALTA NA PLACA:", nome)

# Os programas são laços sem fim, então a troca é feita reiniciando a placa
try:
    exec(open(PROGRAMAS[indice]).read(), {})
    debug("programa terminou sozinho:", PROGRAMAS[indice])
except Exception as erro:
    debug("programa falhou:", PROGRAMAS[indice])
    sys.print_exception(erro)

# O programa terminou ou falhou: fica aqui para o botão continuar valendo
while True:
    time.sleep_ms(100)

