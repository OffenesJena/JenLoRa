from machine import I2C

#  ________
# | =    = |
# |   __   |
# |  /  \  |
# |  \__/  |
# |        |
# |_|_|_|_||
#   | | | |
#   | | | |
#   | | | |
#  SDA|VDD|
#     |   |
#    GND SCL

class HYT221:

    SCALE_MAX    = const(16384)
    TEMP_OFFSET  = const(40)
    TEMP_SCALE   = const(165)
    HUM_SCALE    = const(100)

    def __init__(self, i2c, address=0x28):
        self.i2c      = i2c
        self.address  = address

    def read(self):
        self.i2c.writeto(self.address, '')
        data          = self.i2c.readfrom(self.address, 4)
        humidity      =  (HUM_SCALE  * ((data[0] << 8 |  data[1]) & 0x3FFF))  / SCALE_MAX;
        # " >> 2" -> Mask away 2 least significant bits see HYT 221 doc
        temperature   = ((TEMP_SCALE *  (data[2] << 6 | (data[3] >>      2))) / SCALE_MAX) - TEMP_OFFSET;

        return humidity, temperature

    def readRAW(self):
        return self.i2c.readfrom(self.address, 4)
