# mensagem-wifi

A placa cria a própria rede Wi-Fi e serve uma página com uma caixa de texto; o que for enviado aparece na tela, centralizado e quebrado em linhas.

## Como usar

1. Suba o `gc9d01.py` para a placa (se ainda não estiver lá) e rode o `mensagem-wifi.py` pelo Thonny.
2. A tela mostra o nome da rede, a senha e o endereço.
3. No celular, conecte no Wi-Fi **ESP32-Tela** (senha `12345678`). Se o celular avisar que a rede não tem internet, escolha continuar conectado.
4. Abra **http://192.168.4.1** no navegador, escreva e toque em Enviar.

Para iniciar sozinho ao ligar, use no `main.py`: `exec(open("mensagem-wifi.py").read())`

## Detalhes

- Nome e senha da rede ficam em `REDE` e `SENHA` no topo do script (senha com no mínimo 8 caracteres).
- A mensagem aparece em letras gigantes (2 por vez) deslizando da direita para a esquerda, em loop. Até 126 letras.
- `ESCALA` é o tamanho da letra (10 = 2 letras por tela, 5 = 4 letras) e `PASSO` é a velocidade (pixels por quadro).
- A tela de início (rede, senha e endereço) continua em texto pequeno, até chegar a primeira mensagem.
- A fonte não tem acentos: `ç`, `ã`, `é` etc. viram `c`, `a`, `e`; emojis e outros símbolos viram `?`.
- Qualquer pessoa conectada na rede pode mudar a mensagem.

## Histórico de versões

- **v1.0.0** - rede Wi-Fi própria + página com caixa de mensagem que aparece na tela
- **v1.1.0** - mensagem em letras gigantes (2 por vez) deslizando na tela (ainda não testado na placa)
