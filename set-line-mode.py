#!/usr/bin/env python
import mmap
import os
import struct

# import  iomem=relaxed!
#  vi /etc/default/grub
#  Add iomem=relaxed to GRUB_CMDLINE_LINUX
#  grub2-mkconfig -o /boot/grub2/grub.cfg
#  reboot

GPIO_BASE = 0xFE200000  # Raspberry Pi 4 GPIO base address
GPFSEL_OFFSET = 0x00    # Offset for function select registers
BLOCK_SIZE = 4096
GPIO_PIN = 9

def set_gpio_alt(pin, alt):
    with open("/dev/mem", "r+b") as f:
        mm = mmap.mmap(f.fileno(), BLOCK_SIZE, offset=GPIO_BASE)

        reg_index = (pin // 10) * 4
        bit_pos = (pin % 10) * 3

        mm.seek(reg_index)
        reg_val = struct.unpack("<I", mm.read(4))[0]
        reg_val &= ~(7 << bit_pos)
        reg_val |= (alt << bit_pos)

        mm.seek(reg_index)
        mm.write(struct.pack("<I", reg_val))
        mm.close()


for GPIO_PIN in range(9, 12):
    set_gpio_alt(GPIO_PIN, 4)  # ALT0 = PWM0
    set_gpio_alt(GPIO_PIN, 4)  # ALT0 = PWM0
    set_gpio_alt(GPIO_PIN, 4)  # ALT0 = PWM0
    print(f"GPIO {GPIO_PIN:02d} set to ALT0 (PWM0)")

