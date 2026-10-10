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
| `imagem-bluetooth/imagem-bluetooth.py` | Recebe uma imagem por Bluetooth LE e mostra na tela | Placa |
| `imagem-bluetooth/enviar.html` | Página que converte e envia a imagem por Web Bluetooth | Navegador |
| `alterna/main.py` | Alterna entre `imagem.py` e `mensagem-wifi.py` a cada clique no botão BOOT | Placa |
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
- **v1.2.0** - página escura responsiva, formulário persistente e ajustes de apresentação aplicados ao letreiro
- **v1.2.1** - página com estilo cru: fundo azul escuro liso, sem efeitos

### imagem-bluetooth

- **v1.0.0** - recebe imagem 160x160 RGB565 por Bluetooth LE e mostra na tela (ainda não testado na placa)
- **v1.0.1** - página tenta conectar 3 vezes; conexão e desconexão aparecem no serial
- **v1.1.0** - código de 5 dígitos próprio de cada placa, no nome do Bluetooth e na tela
- **v1.2.0** - handshake: a placa só aceita imagem depois de responder ao aperto de mão da página

### wifi-boot

- **v1.0.0** - conecta no Wi-Fi de casa e inicia o WebREPL
- **v2.0.0** - passa a criar a própria rede Wi-Fi em vez de usar a de casa (ainda não testado na placa)

### alterna

- **v1.0.0** - alterna entre `imagem.py` e `mensagem-wifi.py` pelo botão BOOT (ainda não testado na placa)
- **v1.1.0** - mensagens de depuração no serial a cada passo da troca
