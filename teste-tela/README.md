# teste-tela

Teste básico da tela: mostra a versão por 2 s e depois alterna entre branco máximo e preto absoluto a cada 3 s. Serve para conferir se o driver e a fiação estão funcionando.

```
mpremote cp lib/gc9d01.py :gc9d01.py
mpremote run teste-tela/teste-tela.py
```

## Histórico de versões

- **v1.0.0** - círculo, retângulo e textos de teste
- **v1.1.0** - alterna branco/preto a cada 3 s
- **v1.2.0** - mostra a versão ao iniciar
- **v1.3.0** - usa o driver com init completo, SPI a 27 MHz (testado na placa)
