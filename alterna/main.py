import sys
import time

import machine
from machine import Pin

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - alterna entre imagem.py e mensagem-wifi.py pelo botão BOOT
VERSAO = "v1.0.0"

# Programas que o botão percorre, nesta ordem (precisam estar na placa)
PROGRAMAS = ("imagem.py", "mensagem-wifi.py")

# Guarda qual programa está em uso, para voltar nele ao religar
ARQUIVO = "programa.txt"

# Botão BOOT: GPIO9, vai a 0 quando apertado
botao = Pin(9, Pin.IN, Pin.PULL_UP)

try:
    with open(ARQUIVO) as f:
        indice = int(f.read()) % len(PROGRAMAS)
except (OSError, ValueError):
    indice = 0

def troca(pino):
    pino.irq(handler=None)
    with open(ARQUIVO, "w") as f:
        f.write(str((indice + 1) % len(PROGRAMAS)))
    # Só reinicia depois de soltar, para o GPIO9 não estar apertado no boot
    while pino.value() == 0:
        time.sleep_ms(10)
    time.sleep_ms(50)
    machine.reset()

botao.irq(troca, Pin.IRQ_FALLING)

print("alterna", VERSAO, "->", PROGRAMAS[indice])

# Os programas são laços sem fim, então a troca é feita reiniciando a placa
try:
    exec(open(PROGRAMAS[indice]).read(), {})
except Exception as erro:
    sys.print_exception(erro)

# O programa terminou ou falhou: fica aqui para o botão continuar valendo
while True:
    time.sleep_ms(100)
