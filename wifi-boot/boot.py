# boot.py: roda antes do main.py toda vez que a placa liga.
# Cria a rede Wi-Fi da placa e liga o WebREPL para enviar código sem cabo.
import network

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - conecta no Wi-Fi de casa e inicia o WebREPL
# v2.0.0 - passa a criar a própria rede Wi-Fi em vez de usar a de casa
# v2.0.1 - erro no WebREPL não derruba mais o boot (o main.py deixava de rodar)
VERSAO = "v2.0.1"

# Rede criada pela placa (a senha precisa ter no mínimo 8 caracteres).
# Use a mesma senha do tela-sem-fio.py (lá o nome ganha o código da placa)
REDE = "ESP32-Tela"
SENHA = "12345678"

print("boot", VERSAO)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=REDE, password=SENHA, authmode=network.AUTH_WPA2_PSK)
print("Rede:", REDE, "IP:", ap.ifconfig()[0])

# Se o boot.py terminar com erro, a placa não roda o main.py
try:
    import webrepl
    webrepl.start()
except Exception as erro:
    print("WebREPL nao iniciou:", erro)
