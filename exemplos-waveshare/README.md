# exemplos-waveshare

Portes para MicroPython dos exemplos Arduino do [demo oficial](https://files.waveshare.com/wiki/ESP32-C3-LCD-0.71/ESP32-C3-LCD-0.71-Demo.zip) da Waveshare. Cada pasta tem seu próprio README.

| Pasta | Exemplo original | O que faz |
|---|---|---|
| `01_texto_numero` | 01_Text_and_Number_Display | Troca de cores, texto e contador 00-99 |
| `02_formas` | 02_Shapes_on_Circular_Display | Quadrado, triângulo e círculo com cores aleatórias |
| `04_olho_animado` | 04_Animated_Eye2 e 05_Animated_Eye12 | Animação de 12 quadros (olho), mostra FPS no serial |
| `06_imagens` | 06_Image_Display | Passa as 4 imagens do demo, 3 s cada |
| `07_relogio` | 07_Clock | Mostrador do demo + ponteiros |

Todos precisam do driver na placa: `mpremote cp lib/gc9d01.py :gc9d01.py`

## Não portados

`03_Animated_Eye1` e o `Demo_1` do `05` (olho procedural "Uncanny Eyes"). Ele calcula pixel a pixel sobre ~150 KB de tabelas, o que não cabe na RAM nem roda em velocidade útil em MicroPython puro.

## Diferenças em relação ao original

- A fonte é a 8x8 do `framebuf` (ampliada no contador do 01).
- Os exemplos 04, 06 e 07 usavam LVGL; aqui desenham direto no buffer.
- No 07 os ponteiros são linhas, não as imagens PNG do demo.

## Espaço na placa

Todos os `.raw` juntos somam ~870 KB. Se faltar espaço, apague os que não estiver usando (`mpremote rm :olho.raw`).

## Histórico de versões

- **v1.0.0** - portes dos exemplos 01, 02, 04/05, 06 e 07 (ainda não testados na placa)
