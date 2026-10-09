# Roda no Raspberry (Python normal, não MicroPython). Precisa do Pillow.
# Uso: python3 converte.py foto.jpg imagem.raw
import sys
from PIL import Image, ImageOps

# Corta no centro e redimensiona para 160x160
img = ImageOps.fit(Image.open(sys.argv[1]).convert("RGB"), (160, 160))

dados = bytearray()
for r, g, b in img.getdata():
    cor = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    dados += cor.to_bytes(2, "big") # O painel lê o byte alto primeiro

with open(sys.argv[2], "wb") as f:
    f.write(dados)
