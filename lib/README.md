# lib

`gc9d01.py`: driver da tela redonda (chip GC9D01, 160x160). É um `framebuf.FrameBuffer` RGB565, então aceita `fill`, `text`, `line`, `rect`, `ellipse`, `poly` etc.; `show()` envia o buffer para o painel.

Precisa estar na placa antes de qualquer programa:

```
mpremote cp lib/gc9d01.py :gc9d01.py
```

Uso:

```python
display = gc9d01.GC9D01(spi, dc=dc, cs=cs, rst=rst)
display.fill(0xFFFF)
display.show()
```

Para programas com pouca memória sobrando, `gc9d01.Painel(spi, dc=dc, cs=cs, rst=rst)` liga a tela sem criar o buffer de 51 KB; `envia(y, dados)` manda linhas inteiras já prontas em RGB565, a partir da linha `y`. O `tela-sem-fio` usa assim.

Cores vão em RGB565 com os bytes invertidos (vermelho `0x00F8`, verde `0xE007`, azul `0x1F00`).

## Histórico de versões

- **v1.0.0** - init reduzido, sem Sleep Out (tela não ligava direito)
- **v1.1.0** - adiciona Sleep Out (`0x11`); tela liga, mas branco sai cinza claro
- **v1.2.0** - init completo do demo oficial Waveshare; branco e preto corretos (testado na placa)
- **v1.3.0** - classe `Painel`, sem buffer de tela, que recebe as linhas prontas (ainda não testado na placa)
