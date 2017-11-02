## LoAirRohr

This scripts expects both a BME280 temperature, humidity and pressure sensor and a SDS011 particle sensor
connected to your pycom LoPy LoRa device.

The **BME280** is expected to be connected via I2C with clock SCL/SCK on *P9 (G16)* and data SDA/SDI on *P10 (G17)*
````
def initBME280():
    i2c = I2C(0, I2C.MASTER, baudrate=100000, pins=("P9", "P10"))
````

The **SDS011** is expected to be connected to UART1 with RX on *P3 (G11)* and TX on *P4 (G12)*
````
def initSDS011():
    uart = UART(1, 9600)
    uart.init(9600, bits=8, parity=None, stop=1)
````

Currently the LoPy will send a string containing all environmental data upstream
````
24.54C 54.76% 991.11nPha 5.7pm10 2.6pm25
````

At e.g. the The-Things-Network you can use the provided decoder script to decode this string into a javascript object 
