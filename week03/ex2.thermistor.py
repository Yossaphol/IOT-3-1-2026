import spidev
import math
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

R_FIXED = 10000
R0 = 10000
B = 4050
T0 = 25 + 273.15

def read_adc(channel):

    command = [0x06 | (channel >> 2),
               (channel & 0x03) << 6,
               0]

    adc = spi.xfer2(command)

    value = ((adc[1] & 0x0F) << 8) | adc[2]
    return value

try:

    while True:

        adc = read_adc(0)

        voltage = adc * 3.3 / 4095

        resistance = (voltage * R_FIXED) / (3.3 - voltage)

        temperatureK = 1 / ((1/T0) + (1/B) * math.log(resistance/R0))
        temperatureC = temperatureK - 273.15
        temperatureF = (temperatureC * 9/5) + 32
        temperatureR = temperatureK * 9/5

        print("----------------------------")
        print(f"ADC         : {adc}")
        print(f"Voltage     : {voltage:.3f} V")
        print(f"Resistance  : {resistance:.0f} Ω")
        print(f"Celsius     : {temperatureC:.2f} °C")
        print(f"Kelvin      : {temperatureK:.2f} K")
        print(f"Fahrenheit  : {temperatureF:.2f} °F")
        print(f"Rankine     : {temperatureR:.2f} °R")
        time.sleep(1)

except KeyboardInterrupt:
    spi.close()