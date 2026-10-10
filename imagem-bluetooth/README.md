# imagem-bluetooth

Envia uma imagem do celular ou do computador para a tela por Bluetooth LE, sem cabo e sem Wi-Fi.

- `imagem-bluetooth.py` roda na **placa**: anuncia o nome **ESP32-Tela**, recebe a imagem em pedaços direto no buffer do display e mostra quando chega o último.
- `enviar.html` roda no **navegador**: corta a imagem no centro, redimensiona para 160x160, converte para RGB565 e envia por Web Bluetooth.

## Como usar

1. Suba o `gc9d01.py` para a placa (se ainda não estiver lá) e rode o `imagem-bluetooth.py`:

```
mpremote cp lib/gc9d01.py :gc9d01.py
mpremote run imagem-bluetooth/imagem-bluetooth.py
```

2. Abra o `enviar.html` no Chrome ou no Edge (veja abaixo como), escolha a imagem e toque em **Enviar para a tela**.
3. Na primeira vez o navegador abre a lista de dispositivos; escolha **ESP32-Tela**. Depois disso dá para enviar outras imagens sem escolher de novo.

Para iniciar sozinho ao ligar, copie como `main.py`: `mpremote cp imagem-bluetooth/imagem-bluetooth.py :main.py`

## Abrindo a página

O Web Bluetooth só funciona em página **https** ou em **localhost**, então a placa não consegue servir essa página ela mesma.

- **No computador:** dentro da pasta `imagem-bluetooth`, rode `python -m http.server` e abra `http://localhost:8000/enviar.html`.
- **No celular (Android):** hospede o `enviar.html` em https (o GitHub Pages serve) e abra pelo Chrome.
- **iPhone e Firefox** não têm Web Bluetooth.

## Detalhes

- O ESP32-C3 só tem Bluetooth LE, então o "enviar arquivo por Bluetooth" do celular não funciona; precisa ser pela página.
- A imagem tem 51.200 bytes e vai em pedaços de 240 bytes, cada um confirmado pela placa. Leva de alguns segundos a uns 20 s, conforme o aparelho.
- A característica de controle zera a contagem: toda imagem começa com uma escrita nela, então um envio interrompido não desalinha o próximo.
- A imagem fica só na memória; ao desligar a placa ela some.
- Os cantos somem na tela redonda (a prévia da página já aparece redonda).
- Qualquer pessoa por perto pode conectar e mandar uma imagem; não tem senha nem pareamento.

## Histórico de versões

- **v1.0.0** - recebe imagem 160x160 RGB565 por Bluetooth LE e mostra na tela (ainda não testado na placa)
