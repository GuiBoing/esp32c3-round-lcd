# boot.py: roda antes do main.py toda vez que a placa liga.
# Cria a rede Wi-Fi da placa e liga o WebREPL para enviar código sem cabo.
import network

# Histórico de versões (atualize a cada mudança)
# v1.0.0 - conecta no Wi-Fi de casa e inicia o WebREPL
# v2.0.0 - passa a criar a própria rede Wi-Fi em vez de usar a de casa
VERSAO = "v2.0.0"

# Rede criada pela placa (a senha precisa ter no mínimo 8 caracteres).
# Use os mesmos valores do mensagem-wifi.py
REDE = "ESP32-Tela"
SENHA = "12345678"

print("boot", VERSAO)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=REDE, password=SENHA, authmode=network.AUTH_WPA2_PSK)
print("Rede:", REDE, "IP:", ap.ifconfig()[0])

import webrepl
webrepl.start()
