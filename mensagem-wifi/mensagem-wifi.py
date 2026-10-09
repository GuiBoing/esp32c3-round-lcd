import socket
import time

import framebuf
import network
from machine import Pin, SPI
import gc9d01

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - rede Wi-Fi própria + página com caixa de mensagem que aparece na tela
# v1.1.0 - mensagem em letras gigantes (2 por vez) deslizando na tela
VERSAO = "v1.1.0"

# Rede criada pela placa (a senha precisa ter no mínimo 8 caracteres)
REDE = "ESP32-Tela"
SENHA = "12345678"

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)

PRETO = 0x0000
BRANCO = 0xFFFF

# Área útil do texto pequeno (tela de início) na tela redonda (fonte 8x8)
COLUNAS = 14
LINHAS = 9

# Letreiro: cada pixel da fonte 8x8 vira um quadrado de ESCALA pixels,
# então com 10 cabem 2 letras por vez na tela de 160
ESCALA = 10
TOPO = 80 - 4 * ESCALA
PASSO = 8 # Pixels andados por quadro (velocidade)

# A fonte do framebuf não tem acentos
COM_ACENTO = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"
SEM_ACENTO = "aaaaeeiooouucAAAAEEIOOOUUC"

PAGINA = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tela ESP32</title>
<style>
body{font-family:sans-serif;max-width:420px;margin:24px auto;padding:0 16px}
textarea{width:100%%;height:110px;font-size:18px;box-sizing:border-box}
button{width:100%%;padding:14px;font-size:18px;margin-top:8px}
</style></head><body>
<h2>Mensagem na tela</h2>
<form action="/" method="get">
<textarea name="m" maxlength="126" autofocus></textarea>
<button type="submit">Enviar</button>
</form>
<p>Na tela agora: <b>%s</b></p>
</body></html>"""

def tira_acentos(texto):
    saida = ""
    for c in texto:
        i = COM_ACENTO.find(c)
        if i >= 0:
            saida += SEM_ACENTO[i]
        elif ord(c) < 128:
            saida += c
        else:
            saida += "?"
    return saida

def decodifica(valor):
    # Desfaz a codificação de URL (+ vira espaço, %XX vira byte)
    partes = valor.replace("+", " ").split("%")
    dados = bytearray(partes[0].encode())
    for parte in partes[1:]:
        try:
            dados.append(int(parte[:2], 16))
            dados.extend(parte[2:].encode())
        except ValueError:
            dados.extend(b"%" + parte.encode())
    try:
        return bytes(dados).decode()
    except UnicodeError:
        return ""

def quebra(texto):
    # Quebra em linhas de até COLUNAS letras, sem cortar palavras quando possível
    linhas = []
    atual = ""
    for palavra in texto.split():
        while len(palavra) > COLUNAS:
            if atual:
                linhas.append(atual)
                atual = ""
            linhas.append(palavra[:COLUNAS])
            palavra = palavra[COLUNAS:]
        if not atual:
            atual = palavra
        elif len(atual) + 1 + len(palavra) <= COLUNAS:
            atual += " " + palavra
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas[:LINHAS]

def mostra(texto):
    linhas = quebra(texto)
    display.fill(PRETO)
    y = 80 - len(linhas) * 5 + 1
    for linha in linhas:
        display.text(linha, 80 - len(linha) * 4, y, BRANCO)
        y += 10
    display.show()

def prepara(texto):
    # Desenha o texto inteiro em um buffer de 1 bit, na fonte 8x8 original
    largura = len(texto) * 8
    fb = framebuf.FrameBuffer(bytearray(largura), largura, 8, framebuf.MONO_HLSB)
    fb.text(texto, 0, 0, 1)
    return fb, largura

def quadro(letras, largura, desl):
    # Amplia só as colunas da fonte que estão visíveis neste quadro
    display.fill(PRETO)
    primeira = max(0, desl // ESCALA)
    ultima = min(largura, (desl + 160) // ESCALA + 1)
    for coluna in range(primeira, ultima):
        x = coluna * ESCALA - desl
        for linha in range(8):
            if letras.pixel(coluna, linha):
                display.fill_rect(x, TOPO + linha * ESCALA, ESCALA, ESCALA, BRANCO)
    display.show()

def le_mensagem(requisicao):
    # Primeira linha: "GET /?m=texto HTTP/1.1"
    try:
        caminho = requisicao.split(b"\r\n")[0].split(b" ")[1].decode()
    except (IndexError, UnicodeError):
        return None
    if "?" not in caminho:
        return None
    for par in caminho.split("?", 1)[1].split("&"):
        if par.startswith("m="):
            return tira_acentos(decodifica(par[2:])).strip()
    return None

print("mensagem-wifi", VERSAO)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=REDE, password=SENHA, authmode=network.AUTH_WPA2_PSK)
ip = ap.ifconfig()[0]
print("Rede:", REDE, "Senha:", SENHA, "Endereco: http://" + ip)

atual = "Wi-Fi: " + REDE + " Senha: " + SENHA + " " + ip
mostra(atual)

servidor = socket.socket()
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind(("0.0.0.0", 80))
servidor.listen(2)
servidor.settimeout(0) # Não bloqueia, para o letreiro continuar andando

letras = None
largura = 0
desl = 0

while True:
    try:
        conexao, endereco = servidor.accept()
    except OSError:
        conexao = None

    if conexao:
        try:
            conexao.settimeout(3)
            mensagem = le_mensagem(conexao.recv(1024))
            if mensagem:
                atual = mensagem
                print("Mensagem:", atual)
                letras, largura = prepara(atual)
                desl = -160 # Começa entrando pela direita
            seguro = atual.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            conexao.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n")
            conexao.sendall((PAGINA % seguro).encode())
        except OSError:
            pass
        finally:
            conexao.close()

    if letras:
        quadro(letras, largura, desl)
        desl += PASSO
        if desl >= largura * ESCALA:
            desl = -160
    else:
        time.sleep_ms(50)
