# 04_olho_animado

Porte do `04_Animated_Eye2` e do `Demo_2` do `05_Animated_Eye12` (os dois usam a mesma animação). Toca em loop os 12 quadros do olho vermelho girando e imprime o FPS no serial a cada volta.

É o melhor teste de velocidade da placa: cada quadro são 51.200 bytes lidos da flash e enviados por SPI.

- `olho.raw`: 12 quadros de 160x160 RGB565 (600 KB), extraídos do `EYEA.h` do demo.

```
mpremote cp exemplos-waveshare/04_olho_animado/olho.raw :olho.raw
mpremote run exemplos-waveshare/04_olho_animado/04_olho_animado.py
```

`ATRASO_MS` no script é a pausa entre quadros (70 ms no original); ponha 0 para ver o máximo que a placa aguenta.

## Histórico de versões

- **v1.0.0** - animação de 12 quadros em loop, com medição de FPS no serial (ainda não testado na placa)
