#!/usr/bin/env python

# https://github.com/raspberrypi/documentation/blob/develop/documentation/asciidoc/computers/raspberry-pi/spi-bus-on-raspberry-pi.adoc

import spidev

GPG_SPI = spidev.SpiDev()
GPG_SPI.open(0, 1)
GPG_SPI.max_speed_hz = 500000
GPG_SPI.mode = 0b00
GPG_SPI.bits_per_word = 8