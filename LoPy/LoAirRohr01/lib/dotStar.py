# -*- coding: utf-8 -*-
# Based on https://github.com/JanBednarik/micropython-ws2812
# Adapted for LoPy by @aureleq

import gc
from machine import SPI
from machine import Pin
from machine import disable_irq
from machine import enable_irq
from uos import uname

class dotStar:

    def __init__(self, ledNumber=1, clockPin='P10', dataPin='P11'):
        """
        Params:
        * ledNumber = count of LEDs
        * clockPin = pin to connect clock channel
        * dataPin = pin to connect data channel
        """
        self.ledNumber  = ledNumber
        self.clockPin   = clockPin
        self.dataPin    = dataPin

        # Prepare SPI data buffer (4 bytes for each led, additional init and stop sequence)
        self.buf_length = self.ledNumber * 4 + 8
        self.buf = bytearray(self.buf_length)

        # SPI 0 init
        #self.spi = SPI(0, SPI.MASTER, baudrate=8000000, polarity=0, phase=1, pins=(clockPin, dataPin, None))
        self.spi = SPI(0, SPI.MASTER, pins=(clockPin, dataPin, None))

        # Turn LEDs off
        self.show([])

    def show(self, data):
        """
        Show LRGB data on LEDs. Expected data = [(L, R, G, B), ...] where L, R, G and B
        are intensities of colors in range from 0 to 255. One RGB tuple for each
        LED. Count of tuples may be less than count of connected LEDs.
        """
        self.fill_buf(data)
        self.send_buf()

    def send_buf(self):
        """
        Send buffer over SPI.
        """
        #disable_irq()
        self.spi.write(self.buf)
        #enable_irq()
        gc.collect()

    def update_buf(self, data, start=0):
        """
        Fill a part of the buffer with LRGB data.
        Returns the index of the first unfilled LED
        """

        buf = self.buf

        index = 4 + start * 4
        for lum, red, green, blue in data:
            buf[index]   = lum
            buf[index+1] = red
            buf[index+2] = green
            buf[index+3] = blue

            index += 4

            if index+4 > len(buf):
                break

        return int(index / 4 - 1)

    def fill_buf(self, data):
        """
        Fill buffer with RGB data.
        All LEDs after the data are turned off.
        """
        end = self.update_buf(data) + 1

        # Turn off the rest of the LEDs
        buf = self.buf
        for i in range(end, self.ledNumber+1):
            buf[4*i]   = 0xff
            buf[4*i+1] = 0x00
            buf[4*i+2] = 0x00
            buf[4*i+3] = 0x00

    def repeat(self, lum, red, green, blue):

        buf = self.buf

        print(self.ledNumber)

        for i in range(1, self.ledNumber+1):
            buf[4*i]   = lum
            buf[4*i+1] = red
            buf[4*i+2] = green
            buf[4*i+3] = blue
        self.send_buf()

        #endIndex = 4 + self.ledNumber * 4

        #self.buf[endIndex]   = 0xff
        #self.buf[endIndex+1] = 0xff
        #self.buf[endIndex+2] = 0xff
        #self.buf[endIndex+3] = 0xff
