# imagem

Mostra uma imagem qualquer na tela.

- `converte.py` roda no **Raspberry**: corta no centro, redimensiona para 160x160 e grava em RGB565 cru (51.200 bytes). Precisa do Pillow (`sudo apt install python3-pil`).
- `imagem.py` roda na **placa**: lê `imagem.raw` direto no buffer do display.

```
python3 imagem/converte.py foto.jpg imagem.raw
mpremote cp lib/gc9d01.py :gc9d01.py
mpremote cp imagem.raw :imagem.raw
mpremote run imagem/imagem.py
```

Os cantos somem na tela redonda; deixe o assunto no centro. Se vermelho e azul saírem trocados, inverta `r` e `b` na linha do `cor =` do `converte.py`.

## Histórico de versões

- **v1.0.0** - conversor + exibição de `imagem.raw` (ainda não testado na placa)
