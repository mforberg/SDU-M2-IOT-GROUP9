from machine import UART
import pycom
import machine
import os

uart = UART(0, baudrate=115200)
os.dupterm(uart)


machine.main('main.py')