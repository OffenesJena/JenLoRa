import pycom
import machine
import math
import network
import os
import time
import utime
import socket
import binascii
import gc
from machine import RTC
from machine import SD
from machine import Timer
from network import LoRa
from machine import Pin
from machine import I2C
import bme280

print(os.uname())

# https://www.thethingsnetwork.org/wiki/LoRaWAN/Duty-Cycle
# https://docs.pycom.io/chapter/tutorials/lopy/lorawan-otaa.html
# https://github.com/ttn-be/ttnmapper

# Colors
off    = 0x000000
red    = 0xff0000
green  = 0x00ff00
blue   = 0x0000ff
orange = 0xffff00

# Turn off hearbeat LED
pycom.heartbeat(False)

# Use LEDs for indicating LoRa message sending...
useLED = True

# sds011
msg_start  = 170
msg_cmd    = 192
msg_end    = 171
sleep_time = 0.01
device     = None

def go_LoRa():

    # Initialize LoRa in LORAWAN mode.
    lora = LoRa(mode=LoRa.LORAWAN)

    # Device EUI: 70 B3 D5 49 95 7A 21 5F - LoAirRohr01
    print(binascii.hexlify(lora.mac()).upper().decode('utf-8'))

    # Join LoRa network and TTN app "environment"
    #   using "Over the Air Activation (OTAA)"
    app_eui = binascii.unhexlify('xx xx xx xx xx xx xx xx'.replace(' ',''))
    app_key = binascii.unhexlify('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

    # Wait until the module has joined the network
    pycom.rgbled(red)
    while not lora.has_joined():
        print('Could not join LoRa network...')
        pycom.rgbled(off)
        time.sleep(0.1)
        pycom.rgbled(red)
        time.sleep(2)

    print('Joined LoRa network...')
    if useLED:
        pycom.rgbled(orange)
    else:
        pycom.rgbled(off)


    # Create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    # Set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    #s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
    s.setblocking(True)

    while True:
        t, h, p    = readBME280()
        pm10, pm25 = readSDS011()
        bytesSent  = s.send(t + ";" + h + ";" + p + ";" + pm10 + ";" + pm25)
        print('Sent %s bytes' % bytesSent)
        #print(lora.stats()) # only for received packets!
        if useLED:
            pycom.rgbled(green)
            time.sleep(0.1)
            pycom.rgbled(blue)
            time.sleep(4.9)

def initBME280():
    i2c = I2C(0, I2C.MASTER, baudrate=100000, pins=("P9", "P10"))
    sensor = bme280.BME280(i2c=i2c)
    return sensor

def initSDS011():
    uart = UART(1, 9600)
    uart.init(9600, bits=8, parity=None, stop=1)
    return uart

def readBME280():
    hum   = bme280.humidity
    temp  = bme280.temperature
    press = bme280.pressure
    print(temp, hum, press)
    return temp, hum, press

def readSDS011():
    # Read in loop until message start: AAC0
    while True:
        s = sds011.read(1)
        if ord(s) == msg_start:
            s = sds011.read(1)
            if ord(s) == msg_cmd:
                break
        time.sleep(sleep_time)

    s = sds011.read(8)

    pm25hb = s[0]
    pm25lb = s[1]
    pm10hb = s[2]
    pm10lb = s[3]
    d5     = s[4]
    d6     = s[5]

    cs     = s[6]
    tail   = s[7]

    cs_expected = (pm25hb + pm25lb + pm10hb + pm10lb + d5 + d6) % 256

    if cs != cs_expected:
        print("SDS011 checksum test failed")
        return 0, 0

    if tail != msg_end:
        print("SDS011 message was not correctly terminated?")
        return (0, 0)

    pm10        = str(float(pm10hb + pm10lb*256)/10.0) + "pm10"
    pm25        = str(float(pm25hb + pm25lb*256)/10.0) + "pm25"
    print(pm10, pm25)
    return pm10, pm25


bme280 = initBME280()
sds011 = initSDS011()
go_LoRa()
