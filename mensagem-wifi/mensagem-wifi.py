import socket
import time

import framebuf
import network
from machine import Pin, SPI
import gc9d01

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - rede Wi-Fi própria + página com caixa de mensagem que aparece na tela
# v1.1.0 - mensagem em letras gigantes (2 por vez) deslizando na tela
# v1.2.0 - página escura com controles aplicados e formulário persistente
VERSAO = "v1.2.0"

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

# A fonte do framebuf não tem acentos
COM_ACENTO = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"
SEM_ACENTO = "aaaaeeiooouucAAAAEEIOOOUUC"

PAGINA = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tela ESP32</title>
    <style>
        :root { color-scheme: dark; --page-text: __TC__; --panel: __BC__; --message: __MC__; --outline: __BT__; }
        * { box-sizing: border-box; }
        body {
            min-height: 100vh; margin: 0; padding: 32px 16px;
            font-family: system-ui, sans-serif; color: var(--page-text);
            background: radial-gradient(ellipse at 50% -15%, #19333b 0, #101719 45%, #090c0d 100%);
        }
        main { width: min(100%, 620px); margin: 0 auto; }
        header { margin: 0 0 24px; }
        .eyebrow { margin: 0 0 8px; color: #81c9bd; font-size: 12px; font-weight: 700; text-transform: uppercase; }
        h1 { margin: 0; color: #f1f6f4; font-size: 28px; line-height: 1.15; }
        .preview {
            min-height: 86px; display: grid; place-items: center; margin-bottom: 20px;
            padding: 18px; border: 1px solid var(--outline); border-radius: 8px;
            background: var(--panel); color: var(--message); overflow-wrap: anywhere;
            font-size: 20px; font-weight: 700; text-align: center;
        }
        form { display: grid; gap: 18px; }
        .field { display: grid; gap: 8px; }
        label, legend { color: #c7d2d0; font-size: 14px; font-weight: 600; }
        textarea {
            width: 100%; min-height: 112px; resize: vertical; padding: 13px 14px;
            border: 1px solid #384548; border-radius: 6px; background: #111719;
            color: #f1f6f4; font: inherit; font-size: 17px; line-height: 1.45;
        }
        textarea:focus, input:focus-visible, button:focus-visible { outline: 2px solid #71c8b7; outline-offset: 2px; }
        fieldset { min-width: 0; margin: 0; padding: 0; border: 0; }
        .colors { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
        .color-field { min-height: 56px; display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 9px 11px; border: 1px solid #303b3e; border-radius: 6px; background: #111719; }
        .color-field label { font-size: 13px; }
        input[type="color"] { width: 42px; height: 34px; padding: 2px; border: 1px solid #526064; border-radius: 4px; background: #111719; }
        input[type="range"] { width: 100%; accent-color: #71c8b7; }
        .range-heading { display: flex; justify-content: space-between; gap: 12px; }
        output { color: #81c9bd; font-size: 13px; font-variant-numeric: tabular-nums; }
        button { min-height: 48px; padding: 12px 16px; border: 0; border-radius: 6px; background: #8bd2c2; color: #09201e; font: inherit; font-weight: 750; cursor: pointer; }
        button:hover { background: #a5e4d6; }
        .current { margin: 18px 0 0; color: #98a8a6; font-size: 13px; }
        @media (max-width: 420px) {
            body { padding: 24px 14px; }
            .colors { grid-template-columns: 1fr; gap: 8px; }
        }
    </style>
</head>
<body>
    <main>
        <header><p class="eyebrow">ESP32 · letreiro</p><h1>Mensagem na tela</h1></header>
        <div class="preview" aria-label="Prévia da mensagem">__MESSAGE__</div>
        <form action="/" method="get">
            <div class="field"><label for="message">Mensagem</label><textarea id="message" name="m" maxlength="126" autofocus>__MESSAGE__</textarea></div>
            <fieldset><legend>Cores</legend><div class="colors">
                <div class="color-field"><label for="mc">Cor da mensagem</label><input type="color" name="mc" id="mc" value="__MC__"></div>
                <div class="color-field"><label for="bc">Cor do fundo</label><input type="color" name="bc" id="bc" value="__BC__"></div>
                <div class="color-field"><label for="tc">Cor do texto da página</label><input type="color" name="tc" id="tc" value="__TC__"></div>
                <div class="color-field"><label for="bt">Cor da borda</label><input type="color" name="bt" id="bt" value="__BT__"></div>
            </div></fieldset>
            <div class="field"><div class="range-heading"><label for="speed">Velocidade</label><output id="speed-value">__SPEED__ px/quadro</output></div><input type="range" name="speed" id="speed" min="1" max="10" value="__SPEED__" oninput="document.getElementById('speed-value').value=this.value+' px/quadro'"></div>
            <div class="field"><div class="range-heading"><label for="font">Tamanho do texto</label><output id="font-value">__FONT__ px</output></div><input type="range" name="font" id="font" min="4" max="16" value="__FONT__" oninput="document.getElementById('font-value').value=this.value+' px'"></div>
            <button type="submit">Aplicar na tela</button>
        </form>
        <p class="current">Exibindo agora: <strong>__MESSAGE__</strong></p>
    </main>
</body>
</html>"""

COR_MENSAGEM = 0xFFFF
COR_FUNDO = 0x0000
COR_BORDA = 0x07FF
COR_TEXTO_PAGINA = "#dce7e4"
HEX_MENSAGEM = "#ffffff"
HEX_FUNDO = "#000000"
HEX_BORDA = "#00ffff"
VELOCIDADE = 8
ESCALA_ATUAL = ESCALA

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
    display.fill(COR_FUNDO)
    y = 80 - len(linhas) * 5 + 1
    for linha in linhas:
        display.text(linha, 80 - len(linha) * 4, y, COR_MENSAGEM)
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
    display.fill(COR_FUNDO)
    primeira = max(0, desl // ESCALA_ATUAL)
    ultima = min(largura, (desl + 160) // ESCALA_ATUAL + 1)
    for coluna in range(primeira, ultima):
        x = coluna * ESCALA_ATUAL - desl
        for linha in range(8):
            if letras.pixel(coluna, linha):
                y = 80 - 4 * ESCALA_ATUAL + linha * ESCALA_ATUAL
                display.fill_rect(x - 1, y - 1, ESCALA_ATUAL + 2, ESCALA_ATUAL + 2, COR_BORDA)
                display.fill_rect(x, y, ESCALA_ATUAL, ESCALA_ATUAL, COR_MENSAGEM)
    display.show()

def parametros(requisicao):
    # Primeira linha: "GET /?m=texto&mc=%23ffffff HTTP/1.1"
    try:
        caminho = requisicao.split(b"\r\n")[0].split(b" ")[1].decode()
    except (IndexError, UnicodeError):
        return {}
    if "?" not in caminho:
        return {}
    resultado = {}
    for par in caminho.split("?", 1)[1].split("&"):
        if "=" in par:
            chave, valor = par.split("=", 1)
            resultado[chave] = decodifica(valor)
    return resultado

def cor_rgb565(valor, padrao):
    if len(valor) != 7 or valor[0] != "#":
        return padrao
    try:
        rgb = int(valor[1:], 16)
        return ((rgb >> 19) & 0x1f) << 11 | ((rgb >> 10) & 0x3f) << 5 | ((rgb >> 3) & 0x1f)
    except ValueError:
        return padrao

def cor_hex(valor, padrao):
    if len(valor) != 7 or valor[0] != "#":
        return padrao
    try:
        int(valor[1:], 16)
        return "#" + valor[1:].lower()
    except ValueError:
        return padrao

def html_seguro(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")

def pagina(atual):
    html = PAGINA.replace("__MC__", HEX_MENSAGEM).replace("__BC__", HEX_FUNDO)
    html = html.replace("__TC__", COR_TEXTO_PAGINA).replace("__BT__", HEX_BORDA)
    html = html.replace("__SPEED__", str(VELOCIDADE)).replace("__FONT__", str(ESCALA_ATUAL))
    html = html.replace("__MESSAGE__", html_seguro(atual))
    return html

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
            opcoes = parametros(conexao.recv(1024))
            mensagem = tira_acentos(opcoes.get("m", "")).strip()
            if mensagem:
                atual = mensagem
                print("Mensagem:", atual)
                letras, largura = prepara(atual)
                desl = -160 # Começa entrando pela direita
            if "mc" in opcoes:
                HEX_MENSAGEM = cor_hex(opcoes["mc"], HEX_MENSAGEM)
                COR_MENSAGEM = cor_rgb565(HEX_MENSAGEM, COR_MENSAGEM)
            if "bc" in opcoes:
                HEX_FUNDO = cor_hex(opcoes["bc"], HEX_FUNDO)
                COR_FUNDO = cor_rgb565(HEX_FUNDO, COR_FUNDO)
            if "bt" in opcoes:
                HEX_BORDA = cor_hex(opcoes["bt"], HEX_BORDA)
                COR_BORDA = cor_rgb565(HEX_BORDA, COR_BORDA)
            if "tc" in opcoes:
                COR_TEXTO_PAGINA = cor_hex(opcoes["tc"], COR_TEXTO_PAGINA)
            try:
                VELOCIDADE = max(1, min(10, int(opcoes.get("speed", VELOCIDADE))))
                ESCALA_ATUAL = max(4, min(16, int(opcoes.get("font", ESCALA_ATUAL))))
            except ValueError:
                pass
            conexao.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n")
            conexao.sendall(pagina(atual).encode())
        except OSError:
            pass
        finally:
            conexao.close()

    if letras:
        quadro(letras, largura, desl)
        desl += VELOCIDADE
        if desl >= largura * ESCALA_ATUAL:
            desl = -160
    else:
        time.sleep_ms(50)

