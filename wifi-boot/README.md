# wifi-boot

`boot.py` que cria a rede Wi-Fi da própria placa ao ligar e inicia o WebREPL, para enviar e rodar código pelo Thonny sem cabo.

## Configurar (uma vez, pelo cabo)

1. No Shell do Thonny, rode `import webrepl_setup`, responda `E` para habilitar e defina uma senha. Ele pede para reiniciar; aceite.
2. Suba o `boot.py` para a raiz da placa (Upload to /) e reinicie.

## Usar sem cabo

1. Conecte o computador no Wi-Fi **ESP32-Tela** (senha `12345678`).
2. No Thonny: **Run > Configure interpreter**, em "Port or WebREPL" escolha **WebREPL**, e informe `ws://192.168.4.1:8266/` e a senha do WebREPL.

O endereço é sempre `192.168.4.1`.

## Detalhes

- Enquanto estiver no Wi-Fi da placa, o computador fica sem internet. Se o Raspberry usa Wi-Fi para o SSH, a conexão SSH cai ao trocar de rede; por cabo de rede ela continua.
- Mais lento que o USB; arquivos grandes é melhor mandar pelo cabo.
- `REDE` e `SENHA` ficam no topo do `boot.py`; mantenha a senha igual à do `tela-sem-fio.py`.
- Sem o `webrepl_setup` feito, o `boot.py` avisa no serial que o WebREPL não iniciou e segue; a rede Wi-Fi e o `main.py` funcionam do mesmo jeito.
- São duas senhas diferentes: a do Wi-Fi (`SENHA`) e a do WebREPL (definida no `webrepl_setup`).
- Funciona junto com o `tela-sem-fio`: a página fica em `http://192.168.4.1` e o WebREPL na porta 8266. Quando o `tela-sem-fio` inicia, o nome da rede passa a ser **ESP32-Tela-** mais o código da placa.

## Histórico de versões

- **v1.0.0** - conecta no Wi-Fi de casa e inicia o WebREPL
- **v2.0.0** - passa a criar a própria rede Wi-Fi em vez de usar a de casa (ainda não testado na placa)
- **v2.0.1** - erro no WebREPL não derruba mais o boot (o `main.py` deixava de rodar)
