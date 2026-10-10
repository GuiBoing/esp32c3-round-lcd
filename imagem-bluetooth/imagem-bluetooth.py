import time

import bluetooth
import machine
from machine import Pin, SPI
import gc9d01

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - recebe imagem 160x160 RGB565 por Bluetooth LE e mostra na tela
# v1.0.1 - página tenta conectar 3 vezes; conexão e desconexão aparecem no serial
# v1.1.0 - código de 5 dígitos próprio de cada placa, no nome do Bluetooth e na tela
# v1.2.0 - handshake: a placa só aceita imagem depois de responder ao aperto de mão da página
VERSAO = "v1.2.0"

# Código de 5 dígitos tirado do número de série do chip: é sempre o mesmo em cada placa
CODIGO = "%05d" % (int.from_bytes(machine.unique_id()[-3:], "big") % 100000)

# Nome que aparece na busca do Bluetooth
PREFIXO = "ESP32-Tela"
NOME = PREFIXO + "-" + CODIGO

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
_NOTIFICA = 0x0010

# Primeiro byte do que chega na característica de controle
_INICIO = 1 # Começa uma imagem nova
_HANDSHAKE = 2 # Seguido de 4 bytes sorteados pela página

tela = memoryview(display.buffer)
recebidos = 0
pronta = False
aceito = False # Vira True quando o handshake termina
tem_imagem = False
aviso = None # Linhas de texto para o laço principal desenhar

def campo(tipo, valor):
    return bytes((len(valor) + 1, tipo)) + valor

# O anúncio só comporta 31 bytes, então o nome vai na resposta da busca
ANUNCIO = campo(0x01, b"\x06") + campo(0x07, bytes(SERVICO))
RESPOSTA = campo(0x09, NOME.encode())

def anuncia():
    ble.gap_advertise(100000, adv_data=ANUNCIO, resp_data=RESPOSTA)

def evento(codigo, dados):
    global recebidos, pronta, aceito, aviso
    if codigo == _CONECTOU:
        recebidos = 0
        aceito = False
        print("Conectou, aguardando handshake")
    elif codigo == _DESCONECTOU:
        recebidos = 0
        aceito = False
        aviso = TELA_INICIAL
        print("Desconectou")
        anuncia() # Volta a aparecer na busca
    elif codigo == _ESCREVEU:
        if dados[1] == h_controle:
            comando = ble.gatts_read(h_controle)
            if comando[:1] == bytes((_HANDSHAKE,)):
                # Devolve os bytes sorteados, mais o código e a versão da placa
                aceito = True
                ble.gatts_notify(dados[0], h_controle, comando[:5] + (CODIGO + " " + VERSAO).encode())
                aviso = ["Conectado", CODIGO]
                print("Handshake ok")
            elif comando[:1] == bytes((_INICIO,)) and aceito:
                recebidos = 0
                aviso = None # Nada de texto por cima da imagem que vai chegar
        elif dados[1] == h_dados and aceito:
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

print("imagem-bluetooth", VERSAO, NOME)

ble = bluetooth.BLE()
ble.active(True)
ble.irq(evento)
ble.config(gap_name=NOME, mtu=256)
((h_controle, h_dados),) = ble.gatts_register_services(
    ((SERVICO, ((CONTROLE, _ESCRITA | _NOTIFICA), (DADOS, _ESCRITA))),)
)
ble.gatts_set_buffer(h_dados, 512) # O padrão é 20 bytes por escrita
anuncia()

TELA_INICIAL = ["Bluetooth:", PREFIXO, CODIGO, VERSAO]
mostra(TELA_INICIAL)

while True:
    if pronta:
        pronta = False
        tem_imagem = True
        display.show()
        print("Imagem recebida")
    if aviso:
        # Depois da primeira imagem, os avisos só saem no serial
        if not tem_imagem:
            mostra(aviso)
        aviso = None
    time.sleep_ms(20)
