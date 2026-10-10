# tela-sem-fio

Substitui os antigos `mensagem-wifi` e `imagem-bluetooth`, juntando os dois em um programa só: a placa abre a rede Wi-Fi e o Bluetooth ao mesmo tempo, e tanto a mensagem do letreiro quanto a imagem podem chegar por qualquer um dos dois.

- `tela-sem-fio.py` roda na **placa**: cria a rede Wi-Fi, serve a página, anuncia o Bluetooth e mostra o que chegar.
- `pagina.html` é a **mesma página** para os dois caminhos. Fica gravada na placa (para o Wi-Fi) e também pode ser aberta do computador ou de um site https (para o Bluetooth).

## Como usar

```
mpremote cp lib/gc9d01.py :gc9d01.py
mpremote cp tela-sem-fio/pagina.html :pagina.html
mpremote run tela-sem-fio/tela-sem-fio.py
```

A tela mostra o nome (**ESP32-Tela-** mais um código de 5 dígitos, o mesmo no Wi-Fi e no Bluetooth), a senha do Wi-Fi e o endereço.

- **Por Wi-Fi:** conecte na rede da placa (senha `12345678`) e abra **http://192.168.4.1**. Se o celular avisar que a rede não tem internet, escolha continuar conectado.
- **Por Bluetooth:** dentro da pasta `tela-sem-fio`, rode `python -m http.server` e abra `http://localhost:8000/pagina.html` no Chrome ou no Edge; no Android, hospede o `pagina.html` em https (o GitHub Pages serve). Toque em **Conectar por Bluetooth** e escolha a placa pelo código.

A página escolhe o caminho sozinha: aberta pelo endereço da placa usa o Wi-Fi; aberta de https ou localhost usa o Bluetooth.

Para iniciar sozinho ao ligar, copie como `main.py`: `mpremote cp tela-sem-fio/tela-sem-fio.py :main.py`

## Pacote

O mesmo pacote vale nos dois caminhos; só muda como ele viaja.

| Parte | Tamanho | Conteúdo |
|---|---|---|
| Tipo | 1 byte | `1` = texto, `2` = imagem |
| Tamanho | 4 bytes | Tamanho do corpo, little-endian |
| Corpo | variável | Depende do tipo |

- **Corpo do texto:** cor da mensagem, do fundo e da borda (3 bytes RGB cada), velocidade (1 byte, 1 a 10), tamanho da letra (1 byte, 4 a 16) e a mensagem em UTF-8 (até 126 letras). Com a mensagem vazia, só as cores e os ajustes mudam.
- **Corpo da imagem:** 51.200 bytes, 160x160 pixels RGB565 com o byte alto primeiro.

Como viaja:

- **Wi-Fi:** o pacote inteiro é o corpo de um `POST /pacote`. `GET /info` devolve o código e a versão da placa.
- **Bluetooth:** a página faz o handshake, escreve `1` na característica de controle, depois o cabeçalho de 5 bytes e o corpo em pedaços de 240 bytes na característica de dados, cada escrita confirmada pela placa.

## Detalhes

- O Wi-Fi leva cerca de um segundo para uma imagem; o Bluetooth, de alguns segundos a uns 20 s.
- Enquanto uma imagem chega, o letreiro fica parado. Se o envio for interrompido, o letreiro volta; se não havia letreiro, volta a tela inicial.
- A imagem e a mensagem ficam só na memória; ao desligar a placa elas somem.
- A fonte não tem acentos: `ç`, `ã`, `é` etc. viram `c`, `a`, `e`; emojis e outros símbolos viram `?`.
- As cores do letreiro vão com os bytes invertidos, como o painel lê.
- Wi-Fi, Bluetooth e um buffer de tela inteiro (51 KB) não cabem juntos na memória. Por isso este programa usa o `gc9d01.Painel`, sem buffer: tudo é desenhado em faixas de 8 linhas (2,5 KB), enviadas ao painel uma por vez, e a imagem segue pelo mesmo caminho conforme chega. Precisa do `gc9d01.py` v1.3.0 ou mais novo na placa.
- A imagem aparece na tela de cima para baixo durante o envio.
- As faixas são criadas antes de os rádios ligarem, e o serial mostra a memória a cada etapa. Se a memória livre do sistema ficar abaixo de uns 20 KB com tudo ligado, as conexões começam a cair.
- Se o Bluetooth não conseguir ligar, o programa avisa no serial, a tela mostra `So Wi-Fi` e tudo continua funcionando pelo Wi-Fi.
- `USAR_WIFI` e `USAR_BLUETOOTH`, no topo do script, ligam ou desligam cada rádio. Os dois dividem a mesma antena; desligar um serve para testar o outro sozinho.
- Qualquer pessoa na rede ou por perto pode mudar a tela; o Bluetooth não tem senha nem pareamento.

## Histórico de versões

- **v1.0.0** - texto e imagem na mesma placa, por Wi-Fi e por Bluetooth, com o mesmo pacote; substitui o `mensagem-wifi` e o `imagem-bluetooth` (ainda não testado na placa)
- **v1.0.1** - liga os rádios antes de tudo (Bluetooth primeiro); sem Bluetooth, segue só com Wi-Fi
- **v1.1.0** - sem o buffer de 51 KB: desenho em 4 cores e imagem enviada em faixas direto ao painel
- **v1.2.0** - desenha direto em faixas de 8 linhas, criadas antes dos rádios, para sobrar memória para as conexões
- **v1.2.1** - opção de ligar só um dos rádios, para testes; avisa quando a conexão Bluetooth não completa
- **v1.2.2** - imagem por Wi-Fi não é mais desfeita depois de 3 s (o fim do pacote se perdia)
