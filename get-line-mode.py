#!/usr/bin/env python
import os
import mmap
import struct

# Constants
GPIO_BASE = 0xFE200000  # Use 0x7E200000 on older models
GPFSEL_OFFSET = 0x00    # GPFSEL0 starts at offset 0x00
GPFSEL_SIZE = 6        # Number of GPFSEL registers (for GPIO 0-53)

def get_gpio_function(gpio):
    """ Reads the GPIO function mode from /dev/mem """
    if gpio < 0 or gpio > 53:
        raise ValueError("GPIO pin must be between 0 and 53")

    # Open /dev/mem
    with open("/dev/mem", "rb") as f:
        # Map memory
        mem = mmap.mmap(f.fileno(), length=4096, offset=GPIO_BASE, access=mmap.ACCESS_READ)
        
        # Determine which GPFSEL register and bit position
        reg_index = gpio // 10
        bit_offset = (gpio % 10) * 3

        # Read the GPFSEL register
        mem.seek(GPFSEL_OFFSET + (reg_index * 4))
        reg_value = struct.unpack("<I", mem.read(4))[0]

        # Extract the 3-bit function value
        function = (reg_value >> bit_offset) & 0b111

        # Close memory map
        mem.close()

        return function

def decode_gpio_function(func):
    """ Decodes function select value to human-readable mode """
    modes = {
        0: "Input",
        1: "Output",
        2: "Alt5",
        3: "Alt4",
        4: "Alt0",
        5: "Alt1",
        6: "Alt2",
        7: "Alt3",
    }
    return modes.get(func, "Unknown")

# Example Usage
for gpio_pin in range(0, 53):  # range(start, stop) where stop is exclusive
    func_val = get_gpio_function(gpio_pin)
    print(f"GPIO %02d Mode: %s"%(gpio_pin,decode_gpio_function(func_val)))

