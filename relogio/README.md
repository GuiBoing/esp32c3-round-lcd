# relogio

Relógio analógico desenhado por código: borda, 12 marcações, ponteiros de hora e minuto (brancos), segundos (vermelho) e hora digital embaixo do centro. Mostra a versão por 2 s ao iniciar.

```
mpremote cp lib/gc9d01.py :gc9d01.py
mpremote rtc --set run relogio/relogio.py
```

O `rtc --set` acerta a hora da placa pela hora do Raspberry. Sem ele o relógio começa em 00:00 de 2000, porque a placa perde a hora sem energia.

Para iniciar sozinho ao ligar: `mpremote cp relogio/relogio.py :main.py` (a hora continua dependendo do `rtc --set`).

## Histórico de versões

- **v1.0.0** - relógio analógico com ponteiros + hora digital (ainda não testado na placa)
