# 07_relogio

Porte do `07_Clock`. Usa o mostrador do demo (12, 3, 6, 9 e marcações brancas) como fundo e desenha os ponteiros por cima: hora em branco, minuto em verde, segundo em vermelho.

- `mostrador.raw`: fundo 160x160 RGB565 (50 KB), convertido do `AC.png` do demo. É relido do arquivo a cada segundo para apagar os ponteiros antigos.

```
mpremote cp exemplos-waveshare/07_relogio/mostrador.raw :mostrador.raw
mpremote rtc --set run exemplos-waveshare/07_relogio/07_relogio.py
```

O `rtc --set` acerta a hora da placa pela hora do Raspberry. No original os ponteiros são imagens PNG giradas pelo LVGL; aqui são linhas.

## Histórico de versões

- **v1.0.0** - mostrador do demo como fundo + ponteiros desenhados por cima (ainda não testado na placa)
