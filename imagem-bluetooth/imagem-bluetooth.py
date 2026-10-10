import time

import bluetooth
from machine import Pin, SPI
import gc9d01

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - recebe imagem 160x160 RGB565 por Bluetooth LE e mostra na tela
VERSAO = "v1.0.0"

# Nome que aparece na busca do Bluetooth
NOME = "ESP32-Tela"

# Os mesmos três códigos precisam estar no enviar.html
SERVICO = bluetooth.UUID("7b1e0001-5c3a-4e2b-9f6d-2a8c4d10e571")
CONTROLE = bluetooth.UUID("7b1e0002-5c3a-4e2b-9f6d-2a8c4d10e571")
DADOS = bluetooth.UUID("7b1e0003-5c3a-4e2b-9f6d-2a8c4d10e571")

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

PRETO = 0x0000
BRANCO = 0xFFFF

# Uma imagem inteira: 160x160 pixels, 2 bytes cada
TAMANHO = 160 * 160 * 2

_CONECTOU = 1
_DESCONECTOU = 2
_ESCREVEU = 3
_ESCRITA = 0x0004 | 0x0008 # Escrita sem e com confirmação

tela = memoryview(display.buffer)
recebidos = 0
pronta = False

def campo(tipo, valor):
    return bytes((len(valor) + 1, tipo)) + valor

# O anúncio só comporta 31 bytes, então o nome vai na resposta da busca
ANUNCIO = campo(0x01, b"\x06") + campo(0x07, bytes(SERVICO))
RESPOSTA = campo(0x09, NOME.encode())

def anuncia():
    ble.gap_advertise(100000, adv_data=ANUNCIO, resp_data=RESPOSTA)

def evento(codigo, dados):
    global recebidos, pronta
    if codigo == _CONECTOU:
        recebidos = 0
    elif codigo == _DESCONECTOU:
        recebidos = 0
        anuncia() # Volta a aparecer na busca
    elif codigo == _ESCREVEU:
        if dados[1] == h_controle:
            recebidos = 0 # Qualquer escrita aqui começa uma imagem nova
        elif dados[1] == h_dados:
            # Copia o pedaço direto no buffer do display, na sequência
            pedaco = ble.gatts_read(h_dados)
            n = min(len(pedaco), TAMANHO - recebidos)
            tela[recebidos:recebidos + n] = pedaco[:n]
            recebidos += n
            if recebidos == TAMANHO:
                recebidos = 0
                pronta = True

def mostra(linhas):
    display.fill(PRETO)
    y = 80 - len(linhas) * 5 + 1
    for linha in linhas:
        display.text(linha, 80 - len(linha) * 4, y, BRANCO)
        y += 10
    display.show()

print("imagem-bluetooth", VERSAO)

ble = bluetooth.BLE()
ble.active(True)
ble.irq(evento)
ble.config(gap_name=NOME, mtu=256)
((h_controle, h_dados),) = ble.gatts_register_services(
    ((SERVICO, ((CONTROLE, _ESCRITA), (DADOS, _ESCRITA))),)
)
ble.gatts_set_buffer(h_dados, 512) # O padrão é 20 bytes por escrita
anuncia()

mostra(["Bluetooth:", NOME, VERSAO])

while True:
    if pronta:
        pronta = False
        display.show()
        print("Imagem recebida")
    time.sleep_ms(20)
