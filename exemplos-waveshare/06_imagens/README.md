# 06_imagens

Porte do `06_Image_Display`. Passa as 4 imagens do demo em loop, 3 s cada (o original mostra só a A3 parada).

- `A1.raw` a `A4.raw`: imagens 160x160 RGB565 (50 KB cada), convertidas dos JPG do demo.

```
mpremote cp exemplos-waveshare/06_imagens/A1.raw exemplos-waveshare/06_imagens/A2.raw exemplos-waveshare/06_imagens/A3.raw exemplos-waveshare/06_imagens/A4.raw :
mpremote run exemplos-waveshare/06_imagens/06_imagens.py
```

Para usar imagens próprias, converta com `imagem/converte.py` e ajuste a lista `IMAGENS` no script.

## Histórico de versões

- **v1.0.0** - mostra as 4 imagens do demo, 3 s cada (ainda não testado na placa)
