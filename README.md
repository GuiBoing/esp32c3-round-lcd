# esp32c3-round-lcd

Projetos em MicroPython para a placa **Waveshare ESP32-C3-LCD-0.71** (tela redonda IPS 160x160, chip GC9D01), enviados a partir de um Raspberry Pi via SSH.

## Estrutura

| Pasta | O que faz | Roda onde |
|---|---|---|
| `lib/gc9d01.py` | Driver da tela (framebuf RGB565 + init completo do GC9D01) | Placa |
| `teste-tela/teste-tela.py` | Alterna branco máximo / preto absoluto a cada 3 s | Placa |
| `relogio/relogio.py` | Relógio analógico com ponteiros + hora digital | Placa |
| `imagem/imagem.py` | Mostra o arquivo `imagem.raw` na tela | Placa |
| `imagem/converte.py` | Converte JPG/PNG para `imagem.raw` (160x160 RGB565) | Raspberry |
| `mensagem-wifi/mensagem-wifi.py` | Cria rede Wi-Fi e página com caixa de mensagem que aparece na tela | Placa |
| `wifi-boot/boot.py` | Cria a rede Wi-Fi da placa e liga o WebREPL (enviar código sem cabo) | Placa |

Todos os programas mostram a versão no serial ao iniciar; `teste-tela` e `relogio` também mostram na tela por 2 s.

## Hardware

| Sinal | GPIO |
|---|---|
| MOSI | 7 |
| SCLK | 6 |
| CS | 5 |
| DC | 4 |
| RST | 8 |

SPI a 27 MHz (valor do demo oficial). O backlight não tem pino de controle no demo.

## Como usar (no Raspberry)

O driver precisa estar na placa antes de qualquer programa:

```
mpremote cp lib/gc9d01.py :gc9d01.py
```

Teste da tela:

```
mpremote run teste-tela/teste-tela.py
```

Relógio (o `rtc --set` acerta a hora da placa pela hora do Raspberry):

```
mpremote rtc --set run relogio/relogio.py
```

Imagem (Pillow: `sudo apt install python3-pil`):

```
python3 imagem/converte.py foto.jpg imagem.raw
mpremote cp imagem.raw :imagem.raw
mpremote run imagem/imagem.py
```

Para um programa iniciar sozinho ao ligar a placa, copie como `main.py`:

```
mpremote cp relogio/relogio.py :main.py
```

## Exemplos da Waveshare (`exemplos-waveshare/`)

Portes para MicroPython dos exemplos Arduino do [demo oficial](https://files.waveshare.com/wiki/ESP32-C3-LCD-0.71/ESP32-C3-LCD-0.71-Demo.zip). Os `.raw` já estão convertidos (160x160 RGB565).

| Pasta | Exemplo original | O que faz | Arquivos de dados |
|---|---|---|---|
| `01_texto_numero` | 01_Text_and_Number_Display | Troca de cores, texto e contador 00-99 | - |
| `02_formas` | 02_Shapes_on_Circular_Display | Quadrado, triângulo e círculo com cores aleatórias | - |
| `04_olho_animado` | 04_Animated_Eye2 e 05_Animated_Eye12 | Animação de 12 quadros (olho), mostra FPS no serial | `olho.raw` (600 KB) |
| `06_imagens` | 06_Image_Display | Passa as 4 imagens do demo, 3 s cada | `A1.raw` a `A4.raw` (50 KB cada) |
| `07_relogio` | 07_Clock | Mostrador do demo + ponteiros | `mostrador.raw` (50 KB) |

Não portados: `03_Animated_Eye1` e o `Demo_1` do `05` (olho procedural "Uncanny Eyes"). Ele calcula pixel a pixel sobre ~150 KB de tabelas, o que não cabe na RAM nem roda em velocidade útil em MicroPython puro.

Diferenças em relação ao original: a fonte é a 8x8 do `framebuf` (ampliada no contador); os exemplos 04, 06 e 07 usavam LVGL e aqui desenham direto no buffer; no 07 os ponteiros são linhas, não as imagens PNG.

Como rodar (depois de copiar o driver):

```
mpremote run exemplos-waveshare/01_texto_numero/01_texto_numero.py
mpremote run exemplos-waveshare/02_formas/02_formas.py

mpremote cp exemplos-waveshare/04_olho_animado/olho.raw :olho.raw
mpremote run exemplos-waveshare/04_olho_animado/04_olho_animado.py

mpremote cp exemplos-waveshare/06_imagens/A1.raw exemplos-waveshare/06_imagens/A2.raw exemplos-waveshare/06_imagens/A3.raw exemplos-waveshare/06_imagens/A4.raw :
mpremote run exemplos-waveshare/06_imagens/06_imagens.py

mpremote cp exemplos-waveshare/07_relogio/mostrador.raw :mostrador.raw
mpremote rtc --set run exemplos-waveshare/07_relogio/07_relogio.py
```

Todos os `.raw` juntos somam ~870 KB; se faltar espaço na placa, apague os que não estiver usando (`mpremote rm :olho.raw`).

## Lembretes

- **Cores:** o `framebuf` grava RGB565 em little-endian e o painel lê big-endian, então as constantes de cor vão com os bytes invertidos (vermelho `0x00F8`, azul `0x1F00`, verde `0xE007`). Branco e preto não mudam.
- **Hora:** a placa perde a hora sem energia. Sem `mpremote rtc --set` o relógio começa em 00:00 de 2000. Longe do Raspberry, precisaria de Wi-Fi + NTP (não implementado).
- **Imagem:** os cantos somem na tela redonda; deixe o assunto no centro. Se vermelho e azul saírem trocados, inverta `r` e `b` no `converte.py`.
- **Init do driver:** veio do `GC9D01_Init.h` (TFT_eSPI) do [demo oficial](https://files.waveshare.com/wiki/ESP32-C3-LCD-0.71/ESP32-C3-LCD-0.71-Demo.zip). Wiki: https://www.waveshare.com/wiki/ESP32-C3-LCD-0.71

## Histórico de versões

### lib/gc9d01.py

- **v1.0.0** - init reduzido, sem Sleep Out (tela não ligava direito)
- **v1.1.0** - adiciona Sleep Out (`0x11`); tela liga, mas branco sai cinza claro
- **v1.2.0** - init completo do demo oficial Waveshare; branco e preto corretos (testado na placa)

### teste-tela

- **v1.0.0** - círculo, retângulo e textos de teste
- **v1.1.0** - alterna branco/preto a cada 3 s
- **v1.2.0** - mostra a versão ao iniciar
- **v1.3.0** - usa o driver com init completo, SPI a 27 MHz (testado na placa)

### relogio

- **v1.0.0** - relógio analógico com ponteiros + hora digital (ainda não testado na placa)

### imagem

- **v1.0.0** - conversor + exibição de `imagem.raw` (ainda não testado na placa)

### mensagem-wifi

- **v1.0.0** - rede Wi-Fi própria + página com caixa de mensagem que aparece na tela
- **v1.1.0** - mensagem em letras gigantes (2 por vez) deslizando na tela (ainda não testado na placa)

### wifi-boot

- **v1.0.0** - conecta no Wi-Fi de casa e inicia o WebREPL
- **v2.0.0** - passa a criar a própria rede Wi-Fi em vez de usar a de casa (ainda não testado na placa)

### exemplos-waveshare

- **v1.0.0** - portes dos exemplos 01, 02, 04/05, 06 e 07 (ainda não testados na placa)
