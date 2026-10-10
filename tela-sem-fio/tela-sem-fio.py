import gc
import socket
import time

import bluetooth
import esp32
import framebuf
import machine
import network
from machine import Pin, SPI
import gc9d01

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - texto e imagem na mesma placa, por Wi-Fi e por Bluetooth, com o mesmo pacote
# v1.0.1 - liga os rádios antes de tudo (Bluetooth primeiro); sem Bluetooth, segue só com Wi-Fi
# v1.1.0 - sem o buffer de 51 KB: desenho em 4 cores e imagem enviada em faixas direto ao painel
# v1.2.0 - desenha direto em faixas de 8 linhas, criadas antes dos rádios, para sobrar memória para as conexões
# v1.2.1 - opção de ligar só um dos rádios, para testes; avisa quando a conexão Bluetooth não completa
# v1.2.2 - imagem por Wi-Fi não é mais desfeita depois de 3 s (o fim do pacote se perdia)
VERSAO = "v1.2.2"

# Rádios ligados. Com os dois, eles dividem a mesma antena;
# desligue um deles para testar o outro sozinho
USAR_WIFI = True
USAR_BLUETOOTH = True

# Código de 5 dígitos tirado do número de série do chip: é sempre o mesmo em cada placa
CODIGO = "%05d" % (int.from_bytes(machine.unique_id()[-3:], "big") % 100000)

# Nome da rede Wi-Fi e do Bluetooth (a senha do Wi-Fi precisa ter no mínimo 8 caracteres)
PREFIXO = "ESP32-Tela"
NOME = PREFIXO + "-" + CODIGO
SENHA = "12345678"

# Os mesmos três códigos precisam estar no pagina.html
SERVICO = bluetooth.UUID("7b1e0001-5c3a-4e2b-9f6d-2a8c4d10e571")
CONTROLE = bluetooth.UUID("7b1e0002-5c3a-4e2b-9f6d-2a8c4d10e571")
DADOS = bluetooth.UUID("7b1e0003-5c3a-4e2b-9f6d-2a8c4d10e571")

def memoria(etapa):
    # Memória do MicroPython (em uso e livre) e a livre do sistema, onde ficam o Wi-Fi e o Bluetooth
    sistema = sum(regiao[1] for regiao in esp32.idf_heap_info(esp32.HEAP_DATA))
    print("Memoria", etapa, "- MicroPython:", gc.mem_alloc(), "em uso,", gc.mem_free(), "livre; sistema:", sistema)

print("tela-sem-fio", VERSAO, NOME)
gc.collect()
memoria("no inicio")

# Wi-Fi, Bluetooth e um buffer de tela inteiro (51 KB) não cabem juntos na memória.
# Então tudo é desenhado em faixas de 8 linhas, enviadas ao painel uma por vez.
# As faixas são criadas antes de tudo: se o MicroPython precisar pedir mais memória
# depois que os rádios ligarem, ele pega quase toda a que sobrou para eles.
LINHAS_FAIXA = 8
TAMANHO_FAIXA = 160 * LINHAS_FAIXA * 2

faixa_dados = bytearray(TAMANHO_FAIXA)
faixa = framebuf.FrameBuffer(faixa_dados, 160, LINHAS_FAIXA, framebuf.RGB565)

# A imagem que chega usa uma faixa só dela, para não misturar com o letreiro
faixa_imagem = bytearray(TAMANHO_FAIXA)

bloco = bytearray(512)
bloco_mv = memoryview(bloco)

# Recolhe o lixo com frequência, para a memória do MicroPython não precisar crescer
gc.threshold(8192)

# Os rádios ligam em seguida, enquanto a memória do sistema ainda está inteira.
# O Bluetooth vai primeiro; se o boot.py já ligou o Wi-Fi, ele sai e volta depois.
ap = network.WLAN(network.AP_IF)
ap.active(False)

tem_bluetooth = False
if USAR_BLUETOOTH:
    ble = bluetooth.BLE()
    try:
        ble.active(True)
        tem_bluetooth = True
    except OSError as erro:
        print("Bluetooth nao iniciou:", erro)
    memoria("com Bluetooth")

if USAR_WIFI:
    ap.active(True)
    ap.config(essid=NOME, password=SENHA, authmode=network.AUTH_WPA2_PSK)
    ip = ap.ifconfig()[0]
    memoria("com Wi-Fi")

# MOSI=GPIO7, SCLK=GPIO6, DC=GPIO4, CS=GPIO5, RESET=GPIO8
spi = SPI(1, baudrate=27000000, sck=Pin(6), mosi=Pin(7))
dc = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(8, Pin.OUT)

painel = gc9d01.Painel(spi, dc=dc, cs=cs, rst=rst)

# Pacote, igual no Wi-Fi e no Bluetooth:
#   1 byte de tipo + 4 bytes de tamanho do corpo (little-endian) + corpo
# Corpo do TEXTO: cor da mensagem, do fundo e da borda (3 bytes RGB cada),
#   velocidade (1 byte), tamanho da letra (1 byte) e a mensagem em UTF-8
# Corpo da IMAGEM: 160x160 pixels RGB565, byte alto primeiro
TEXTO = 1
IMAGEM = 2
ABORTO = 0 # Só interno: uma imagem parou no meio

TAMANHO_IMAGEM = 160 * 160 * 2
MAX_LETRAS = 126
MAX_TEXTO = 11 + MAX_LETRAS * 4

_CONECTOU = 1
_DESCONECTOU = 2
_ESCREVEU = 3
_ESCRITA = 0x0004 | 0x0008 # Escrita sem e com confirmação
_NOTIFICA = 0x0010

# Primeiro byte do que chega na característica de controle do Bluetooth
_INICIO = 1 # Vai começar um pacote novo
_HANDSHAKE = 2 # Seguido de 4 bytes sorteados pela página

# A fonte do framebuf não tem acentos
COM_ACENTO = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"
SEM_ACENTO = "aaaaeeiooouucAAAAEEIOOOUUC"

# As cores vão com os bytes invertidos, como o painel lê
PRETO = 0x0000
BRANCO = 0xFFFF
COR_MENSAGEM = BRANCO
COR_FUNDO = PRETO
COR_BORDA = 0xFF07 # Ciano
VELOCIDADE = 8
ESCALA = 10

modo = "info" # "info", "texto" ou "imagem"
recebendo = False # Tem imagem chegando: o letreiro não pode desenhar por cima
redesenha = True # O próximo quadro do letreiro precisa cobrir a tela inteira
pendentes = [] # Pacotes completos, esperando o laço principal aplicar
aceito = False # Vira True quando o handshake do Bluetooth termina
conectado = False

letras = None
largura = 0
desl = 0

class Receptor:
    # Monta um pacote a partir de pedaços de qualquer tamanho
    def __init__(self):
        self.feitos = 0
        self.zera()

    def zera(self):
        self.cabecalho = b""
        self.tipo = 0
        self.tamanho = 0
        self.pos = 0
        self.corpo = None
        self.invalido = False

    def cancela(self):
        if self.tipo == IMAGEM and not self.invalido:
            pendentes.append((ABORTO, None))
        self.zera()

    def recebe(self, pedaco):
        global recebendo
        if self.invalido:
            return
        pedaco = memoryview(pedaco)
        if len(self.cabecalho) < 5:
            n = 5 - len(self.cabecalho)
            self.cabecalho += bytes(pedaco[:n])
            pedaco = pedaco[n:]
            if len(self.cabecalho) < 5:
                return
            self.tipo = self.cabecalho[0]
            self.tamanho = int.from_bytes(self.cabecalho[1:], "little")
            if self.tipo == IMAGEM and self.tamanho == TAMANHO_IMAGEM:
                recebendo = True
            elif self.tipo == TEXTO and self.tamanho <= MAX_TEXTO:
                self.corpo = bytearray(self.tamanho)
            else:
                self.invalido = True
                return
        if self.tipo == IMAGEM:
            # A imagem não fica na memória: cada faixa completa vai direto para o painel
            while len(pedaco) and self.pos < self.tamanho:
                inicio = self.pos % TAMANHO_FAIXA
                n = min(len(pedaco), TAMANHO_FAIXA - inicio)
                faixa_imagem[inicio:inicio + n] = pedaco[:n]
                pedaco = pedaco[n:]
                self.pos += n
                if self.pos % TAMANHO_FAIXA == 0:
                    painel.envia((self.pos // TAMANHO_FAIXA - 1) * LINHAS_FAIXA, faixa_imagem)
        else:
            n = min(len(pedaco), self.tamanho - self.pos)
            self.corpo[self.pos:self.pos + n] = pedaco[:n]
            self.pos += n
        if self.pos == self.tamanho:
            pendentes.append((self.tipo, None if self.tipo == IMAGEM else bytes(self.corpo)))
            self.feitos += 1
            self.zera()

# Um receptor para cada caminho, para um não embaralhar o pacote do outro
do_wifi = Receptor()
do_bluetooth = Receptor()

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

def cor(rgb):
    c = (rgb[0] & 0xF8) << 8 | (rgb[1] & 0xFC) << 3 | rgb[2] >> 3
    return c >> 8 | (c & 0xFF) << 8

def tela_inicial():
    if USAR_WIFI:
        linhas = ["Wi-Fi/Bluetooth" if tem_bluetooth else "So Wi-Fi", PREFIXO, CODIGO, "Senha:" + SENHA, ip, VERSAO]
    else:
        linhas = ["So Bluetooth" if tem_bluetooth else "Sem radio", PREFIXO, CODIGO, VERSAO]
    topo = 80 - len(linhas) * 5 + 1
    for y0 in range(0, 160, LINHAS_FAIXA):
        faixa.fill(PRETO)
        y = topo - y0
        for linha in linhas:
            faixa.text(linha, 80 - len(linha) * 4, y, BRANCO)
            y += 10
        painel.envia(y0, faixa_dados)

def prepara(texto):
    # Desenha o texto inteiro em um buffer de 1 bit, na fonte 8x8 original
    largura = len(texto) * 8
    fb = framebuf.FrameBuffer(bytearray(largura), largura, 8, framebuf.MONO_HLSB)
    fb.text(texto, 0, 0, 1)
    return fb, largura

def quadro(letras, largura, desl, tudo):
    # Amplia só as colunas da fonte que estão visíveis neste quadro.
    # tudo: redesenha a tela inteira; senão, só as faixas por onde o letreiro passa
    topo = 80 - 4 * ESCALA
    primeira = max(0, desl // ESCALA)
    ultima = min(largura, (desl + 160) // ESCALA + 1)
    for y0 in range(0, 160, LINHAS_FAIXA):
        if recebendo:
            return # Começou a chegar imagem: o painel agora é dela
        dentro = y0 + LINHAS_FAIXA >= topo and y0 <= topo + 8 * ESCALA
        if not (tudo or dentro):
            continue
        faixa.fill(COR_FUNDO)
        if dentro:
            # Só as linhas da fonte que cruzam esta faixa (contando a borda)
            de = max(0, (y0 - 1 - topo) // ESCALA)
            ate = min(8, (y0 + LINHAS_FAIXA + 1 - topo) // ESCALA + 1)
            for coluna in range(primeira, ultima):
                x = coluna * ESCALA - desl
                for linha in range(de, ate):
                    if letras.pixel(coluna, linha):
                        y = topo + linha * ESCALA - y0
                        faixa.fill_rect(x - 1, y - 1, ESCALA + 2, ESCALA + 2, COR_BORDA)
                        faixa.fill_rect(x, y, ESCALA, ESCALA, COR_MENSAGEM)
        painel.envia(y0, faixa_dados)

def aplica(tipo, corpo):
    global modo, recebendo, redesenha, letras, largura, desl
    global COR_MENSAGEM, COR_FUNDO, COR_BORDA, VELOCIDADE, ESCALA
    if tipo == IMAGEM:
        recebendo = False
        modo = "imagem" # Já está na tela: foi desenhada enquanto chegava
        print("Imagem recebida")
    elif tipo == ABORTO:
        recebendo = False
        redesenha = True
        print("Imagem interrompida")
        if modo != "texto":
            # Ficou meia imagem no painel; o letreiro redesenha sozinho, o resto não
            modo = "info"
            tela_inicial()
    elif tipo == TEXTO and len(corpo) >= 11:
        COR_MENSAGEM = cor(corpo[0:3])
        COR_FUNDO = cor(corpo[3:6])
        COR_BORDA = cor(corpo[6:9])
        VELOCIDADE = max(1, min(10, corpo[9]))
        ESCALA = max(4, min(16, corpo[10]))
        redesenha = True
        try:
            mensagem = tira_acentos(corpo[11:].decode()).strip()[:MAX_LETRAS]
        except UnicodeError:
            mensagem = ""
        # Sem mensagem, só as cores e os ajustes mudam
        if mensagem:
            print("Mensagem:", mensagem)
            letras, largura = prepara(mensagem)
            desl = -160 # Começa entrando pela direita
            modo = "texto"

# ---------- Bluetooth ----------

def campo(tipo, valor):
    return bytes((len(valor) + 1, tipo)) + valor

# O anúncio só comporta 31 bytes, então o nome vai na resposta da busca
ANUNCIO = campo(0x01, b"\x06") + campo(0x07, bytes(SERVICO))
RESPOSTA = campo(0x09, NOME.encode())

def anuncia():
    ble.gap_advertise(100000, adv_data=ANUNCIO, resp_data=RESPOSTA)

def evento(codigo, dados):
    global aceito, conectado
    if codigo == _CONECTOU:
        aceito = False
        conectado = True
        print("Bluetooth conectou, aguardando handshake")
    elif codigo == _DESCONECTOU:
        # Este evento também vem quando alguém tenta conectar e a conexão não completa
        print("Bluetooth desconectou" if conectado else "Bluetooth: tentativa de conexao nao completou")
        aceito = False
        conectado = False
        do_bluetooth.cancela()
        anuncia() # Volta a aparecer na busca
    elif codigo == _ESCREVEU:
        if dados[1] == h_controle:
            comando = ble.gatts_read(h_controle)
            if comando[:1] == bytes((_HANDSHAKE,)):
                # Devolve os bytes sorteados, mais o código e a versão da placa
                aceito = True
                ble.gatts_notify(dados[0], h_controle, comando[:5] + (CODIGO + " " + VERSAO).encode())
                print("Handshake ok")
            elif comando[:1] == bytes((_INICIO,)) and aceito:
                do_bluetooth.cancela()
        elif dados[1] == h_dados and aceito:
            do_bluetooth.recebe(ble.gatts_read(h_dados))

# ---------- Wi-Fi ----------

def responde(conexao, estado, texto):
    conexao.sendall(b"HTTP/1.1 " + estado + b"\r\nContent-Type: text/plain; charset=utf-8\r\nConnection: close\r\n\r\n")
    conexao.sendall(texto.encode())

def envia_pagina(conexao):
    try:
        f = open("pagina.html", "rb")
    except OSError:
        responde(conexao, b"404 Not Found", "Falta o pagina.html na placa.")
        return
    conexao.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n")
    while True:
        n = f.readinto(bloco)
        if not n:
            break
        conexao.sendall(bloco_mv[:n])
    f.close()

def recebe_pacote(conexao, tamanho, inicio):
    # O corpo do POST é o pacote inteiro; o começo pode ter vindo junto com o cabeçalho
    do_wifi.cancela()
    feitos = do_wifi.feitos
    do_wifi.recebe(inicio)
    falta = tamanho - len(inicio)
    try:
        while falta > 0:
            # Pede só o que falta: o readinto espera encher o tamanho pedido
            n = conexao.readinto(bloco, min(falta, len(bloco)))
            if not n:
                break
            do_wifi.recebe(bloco_mv[:n])
            falta -= n
    except OSError:
        pass
    if do_wifi.feitos > feitos:
        responde(conexao, b"200 OK", "ok")
    else:
        do_wifi.cancela()
        responde(conexao, b"400 Bad Request", "Pacote incompleto ou invalido.")

def atende(conexao):
    conexao.settimeout(3)
    pedido = conexao.recv(1024)
    fim = pedido.find(b"\r\n\r\n")
    while fim < 0 and pedido and len(pedido) < 4096:
        mais = conexao.recv(1024)
        if not mais:
            break
        pedido += mais
        fim = pedido.find(b"\r\n\r\n")
    if fim < 0:
        return
    linhas = pedido[:fim].split(b"\r\n")
    partes = linhas[0].split(b" ")
    if len(partes) < 2:
        return
    metodo, caminho = partes[0], partes[1]
    if metodo == b"GET" and caminho == b"/":
        envia_pagina(conexao)
    elif metodo == b"GET" and caminho == b"/info":
        responde(conexao, b"200 OK", CODIGO + " " + VERSAO)
    elif metodo == b"POST" and caminho == b"/pacote":
        tamanho = 0
        for linha in linhas[1:]:
            if linha.lower().startswith(b"content-length:"):
                tamanho = int(linha.split(b":")[1])
        recebe_pacote(conexao, tamanho, pedido[fim + 4:])
    else:
        responde(conexao, b"404 Not Found", "Nao encontrado.")

# ---------- Início ----------

servidor = None
if USAR_WIFI:
    print("Wi-Fi:", NOME, "Senha:", SENHA, "Endereco: http://" + ip)
    servidor = socket.socket()
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", 80))
    servidor.listen(2)
    servidor.settimeout(0) # Não bloqueia, para o letreiro continuar andando

if tem_bluetooth:
    ble.irq(evento)
    ble.config(gap_name=NOME, mtu=256)
    ((h_controle, h_dados),) = ble.gatts_register_services(
        ((SERVICO, ((CONTROLE, _ESCRITA | _NOTIFICA), (DADOS, _ESCRITA))),)
    )
    ble.gatts_set_buffer(h_dados, 512) # O padrão é 20 bytes por escrita
    anuncia()
    print("Bluetooth:", NOME)

gc.collect()
memoria("com tudo ligado")
tela_inicial()

while True:
    conexao = None
    if servidor:
        try:
            conexao, endereco = servidor.accept()
        except OSError:
            pass

    if conexao:
        try:
            atende(conexao)
        except (OSError, ValueError):
            pass
        finally:
            conexao.close()

    while pendentes:
        aplica(*pendentes.pop(0))

    if modo == "texto" and not recebendo:
        quadro(letras, largura, desl, redesenha)
        redesenha = False
        desl += VELOCIDADE
        if desl >= largura * ESCALA:
            desl = -160
    else:
        time.sleep_ms(20)
