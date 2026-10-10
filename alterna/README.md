# alterna

Um `main.py` que alterna entre o `imagem.py` e o `mensagem-wifi.py` a cada clique no botão **BOOT** da placa.

## Como usar

Copie o driver, os dois programas, a imagem e o `main.py` para a placa:

```
mpremote cp lib/gc9d01.py :gc9d01.py
mpremote cp imagem/imagem.py :imagem.py
mpremote cp imagem.raw :imagem.raw
mpremote cp mensagem-wifi/mensagem-wifi.py :mensagem-wifi.py
mpremote cp alterna/main.py :main.py
```

Ao ligar, a placa abre o último programa usado (na primeira vez, o `imagem.py`). Clique no BOOT e solte para passar para o próximo.

## Detalhes

- Os programas são laços sem fim, então a troca é feita reiniciando a placa: leva cerca de um segundo.
- O programa em uso fica gravado em `programa.txt`, na placa.
- A troca acontece ao **soltar** o botão. Não segure o BOOT ao ligar a placa ou apertar o RESET: isso entra no modo de gravação.
- A mensagem e as cores do `mensagem-wifi` se perdem a cada troca.
- Se um programa falhar (por exemplo, sem o `imagem.raw` na placa), o erro sai no serial e o botão continua funcionando.
- Para trocar ou acrescentar programas, edite `PROGRAMAS` no topo do `main.py`.
- Para usar um switch externo, solde em paralelo com o BOOT ou troque o `Pin(9, ...)` por outro GPIO livre, com o outro terminal no GND.

## Histórico de versões

- **v1.0.0** - alterna entre `imagem.py` e `mensagem-wifi.py` pelo botão BOOT (ainda não testado na placa)
