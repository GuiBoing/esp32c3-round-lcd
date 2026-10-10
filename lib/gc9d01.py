import time

import framebuf
from machine import Pin

# Comandos de Inicialização do Chip GC9D01
_SLPOUT  = b'\x11'
_DISPON  = b'\x29'
_CASET   = b'\x2a'
_RASET   = b'\x2b'
_RAMWR   = b'\x2c'

# Sequência completa do demo oficial Waveshare (TFT_eSPI GC9D01_Init.h)
_INIT = (
    (b'\xfe', None), # Inter_Register Enable
    (b'\xef', None),
    (b'\x80', b'\xff'), (b'\x81', b'\xff'), (b'\x82', b'\xff'), (b'\x83', b'\xff'),
    (b'\x84', b'\xff'), (b'\x85', b'\xff'), (b'\x86', b'\xff'), (b'\x87', b'\xff'),
    (b'\x88', b'\xff'), (b'\x89', b'\xff'), (b'\x8a', b'\xff'), (b'\x8b', b'\xff'),
    (b'\x8c', b'\xff'), (b'\x8d', b'\xff'), (b'\x8e', b'\xff'), (b'\x8f', b'\xff'),
    (b'\x3a', b'\x05'), # Modo de cor de 16-bits (RGB565)
    (b'\xec', b'\x01'),
    (b'\x74', b'\x02\x0e\x00\x00\x00\x00\x00'),
    (b'\x98', b'\x3e'),
    (b'\x99', b'\x3e'),
    (b'\xb5', b'\x0d\x0d'),
    (b'\x60', b'\x38\x0f\x79\x67'),
    (b'\x61', b'\x38\x11\x79\x67'),
    (b'\x64', b'\x38\x17\x71\x5f\x79\x67'),
    (b'\x65', b'\x38\x13\x71\x5b\x79\x67'),
    (b'\x6a', b'\x00\x00'),
    (b'\x6c', b'\x22\x02\x22\x02\x22\x22\x50'),
    (b'\x6e', b'\x03\x03\x01\x01\x00\x00\x0f\x0f\x0d\x0d\x0b\x0b\x09\x09\x00\x00'
              b'\x00\x00\x0a\x0a\x0c\x0c\x0e\x0e\x10\x10\x00\x00\x02\x02\x04\x04'),
    (b'\xbf', b'\x01'),
    (b'\xf9', b'\x40'),
    (b'\x9b', b'\x3b'),
    (b'\x93', b'\x33\x7f\x00'),
    (b'\x7e', b'\x30'),
    (b'\x70', b'\x0d\x02\x08\x0d\x02\x08'),
    (b'\x71', b'\x0d\x02\x08'),
    (b'\x91', b'\x0e\x09'),
    (b'\xc3', b'\x19'),
    (b'\xc4', b'\x19'),
    (b'\xc9', b'\x3c'),
    (b'\xf0', b'\x53\x15\x0a\x04\x00\x3e'), # Gamma
    (b'\xf2', b'\x53\x15\x0a\x04\x00\x3a'),
    (b'\xf1', b'\x56\xa8\x7f\x33\x34\x5f'),
    (b'\xf3', b'\x52\xa4\x7f\x33\x34\xdf'),
    (b'\x36', b'\x00'), # MADCTL: direção da varredura
)

class GC9D01(framebuf.FrameBuffer):
    def __init__(self, spi, dc, cs, rst, width=160, height=160):
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.width = width
        self.height = height

        # Buffer de memória em formato RGB565 (2 bytes por pixel)
        self.buffer = bytearray(self.width * self.height * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)

        self.init_display()

    def _write(self, command, data=None):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(command)
        self.cs.value(1)
        if data:
            self.dc.value(1)
            self.cs.value(0)
            self.spi.write(data)
            self.cs.value(1)

    def init_display(self):
        self.rst.value(1)
        time.sleep_ms(5)
        self.rst.value(0)
        time.sleep_ms(15)
        self.rst.value(1)
        time.sleep_ms(120)

        for command, data in _INIT:
            self._write(command, data)

        self._write(_SLPOUT) # Tira o painel do modo sleep
        time.sleep_ms(200)
        self._write(_DISPON)
        time.sleep_ms(50)

    def show(self):
        # Define a janela de pixels (0,0 até 159,159)
        self._write(_CASET, b'\x00\x00\x00\x9f')
        self._write(_RASET, b'\x00\x00\x00\x9f')
        self._write(_RAMWR, self.buffer)

class Painel:
    # Só o painel, sem buffer de tela: economiza os 51 KB do GC9D01.
    # Quem usa manda as linhas já prontas em RGB565, com envia().
    def __init__(self, spi, dc, cs, rst):
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.init_display()

    _write = GC9D01._write
    init_display = GC9D01.init_display

    def envia(self, y, dados):
        # dados: linhas inteiras de 160 pixels, a partir da linha y
        linhas = len(dados) // 320
        self._write(_CASET, b'\x00\x00\x00\x9f')
        self._write(_RASET, bytes((0, y, 0, y + linhas - 1)))
        self._write(_RAMWR, dados)
