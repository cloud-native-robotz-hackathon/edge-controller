# Hacking with Fedora

## GPIO Setup

https://github.com/DexterInd/GoPiGo3/blob/master/Software/Python/gopigo3.py#L231-L235
```
        # Make sure the SPI lines are configured for mode ALT0 so that the hardware SPI controller can use them
        # subprocess.call('gpio mode 12 ALT0', shell=True)
        # subprocess.call('gpio mode 13 ALT0', shell=True)
        # subprocess.call('gpio mode 14 ALT0', shell=True)
        import pigpio
        pi_gpio = pigpio.pi()
        pi_gpio.set_mode(9, pigpio.ALT0)
        pi_gpio.set_mode(10, pigpio.ALT0)
        pi_gpio.set_mode(11, pigpio.ALT0)
        pi_gpio.stop()
```

```
root@robocop:~# gpioinfo
gpiochip0 - 58 lines:
        line   0:       "ID_SDA"                input
        line   1:       "ID_SCL"                input
        line   2:       "SDA1"                  input
        line   3:       "SCL1"                  input
        line   4:       "GPIO_GCLK"             input
        line   5:       "GPIO5"                 input
        line   6:       "GPIO6"                 input
        line   7:       "SPI_CE1_N"             input
        line   8:       "SPI_CE0_N"             input
        line   9:       "SPI_MISO"              input
        line  10:       "SPI_MOSI"              input
        line  11:       "SPI_SCLK"              input
        line  12:       "GPIO12"                input
        line  13:       "GPIO13"                input
        line  14:       "TXD1"                  input
        line  15:       "RXD1"                  input
        line  16:       "GPIO16"                input
        line  17:       "GPIO17"                input
        line  18:       "GPIO18"                input
        line  19:       "GPIO19"                input
        line  20:       "GPIO20"                input
        line  21:       "GPIO21"                input
        line  22:       "GPIO22"                input
        line  23:       "GPIO23"                input
        line  24:       "GPIO24"                input
        line  25:       "GPIO25"                input
        line  26:       "GPIO26"                input
        line  27:       "GPIO27"                input
        line  28:       "RGMII_MDIO"            input
        line  29:       "RGMIO_MDC"             input
        line  30:       "CTS0"                  input
        line  31:       "RTS0"                  input
        line  32:       "TXD0"                  input
        line  33:       "RXD0"                  input
        line  34:       "SD1_CLK"               input
        line  35:       "SD1_CMD"               input
        line  36:       "SD1_DATA0"             input
        line  37:       "SD1_DATA1"             input
        line  38:       "SD1_DATA2"             input
        line  39:       "SD1_DATA3"             input
        line  40:       "PWM0_MISO"             input
        line  41:       "PWM1_MOSI"             input
        line  42:       "STATUS_LED_G_CLK"      output consumer="ACT"
        line  43:       "SPIFLASH_CE_N"         input
        line  44:       "SDA0"                  input
        line  45:       "SCL0"                  input
        line  46:       "RGMII_RXCLK"           input
        line  47:       "RGMII_RXCTL"           input
        line  48:       "RGMII_RXD0"            input
        line  49:       "RGMII_RXD1"            input
        line  50:       "RGMII_RXD2"            input
        line  51:       "RGMII_RXD3"            input
        line  52:       "RGMII_TXCLK"           input
        line  53:       "RGMII_TXCTL"           input
        line  54:       "RGMII_TXD0"            input
        line  55:       "RGMII_TXD1"            input
        line  56:       "RGMII_TXD2"            input
        line  57:       "RGMII_TXD3"            input
gpiochip1 - 8 lines:
        line   0:       "BT_ON"                 output consumer="shutdown"
        line   1:       "WL_ON"                 output active-low consumer="reset"
        line   2:       "PWR_LED_OFF"           output active-low consumer="PWR"
        line   3:       "GLOBAL_RESET"          output
        line   4:       "VDD_SD_IO_SEL"         output consumer="vdd-sd-io"
        line   5:       "CAM_GPIO"              output consumer="regulator-cam1"
        line   6:       "SD_PWR_ON"             output consumer="regulator-sd-vcc"
        line   7:       unnamed                 input
```


https://github.com/DexterInd/GoPiGo3/blob/master/Hardware/GoPiGo3%20v3.2.0.pdf


