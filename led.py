"""A script that accepts RGB values to define a color
and then displays the color on the LEDs for a specified amount of time.

Parameters:
    red (int): A number in the range 0-255 specifying how much
        red should be in the RGB color display.
    green (int): A number in the range 0-255 specifying how much
        green should be in the RGB color display.
    blue (int): A number in the range 0-255 specifying how much
        blue should be in the RGB color display.
    time (int): The number of seconds that LEDs should display the color
        before returning to an "off" state.
Based on an example script written by Tony DiCola (tony@tonydicola.com),
found at https://tutorials-raspberrypi.com/connect-control-raspberry-pi-ws2812-rgb-led-strips/
"""
import time
import sys
from neopixel import *
import argparse
# LED strip configuration:
LED_COUNT = 16      # Number of LED pixels.
LED_PIN = 18      # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


def set_color_for_time(strip, color, time):
    """This method displays the specified color for the specified amount of time.

    Parameters:
        color (Color): Determines the color displayed on the LED strip.
        time (int): The amount of time in seconds that the LEDs will be illuminated.

    """
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    time.sleep(time)
    strip.clear()


if __name__ == '__main__':
    red = int(sys.argv[1])
    green = int(sys.argv[2])
    blue = int(sys.argv[3])
    color_to_display = Color(red, green, blue)
    time_in_seconds = int(sys.argv[4])
    strip = Adafruit_NeoPixel(
        LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    set_green(strip, color_to_display, time_in_seconds)
