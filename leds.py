# Controls the LEDs
from threading import Timer
from gpiozero import LED

RED_GPIO_PIN = 19
GREEN_GPIO_PIN = 13

BLINK_LENGTH = 0.5

red_led = LED(RED_GPIO_PIN)
green_led = LED(GREEN_GPIO_PIN)


def turn_on_red():
    red_led.on()


def turn_on_green():
    green_led.on()


def blink_red_led():
    red_led.on()
    blink_timer = Timer(BLINK_LENGTH, turn_off_red)
    blink_timer.start()


def blink_green_led():
    green_led.on()
    blink_timer = Timer(BLINK_LENGTH, turn_off_green)
    blink_timer.start()


def turn_off_red():
    red_led.off()


def turn_off_green():
    green_led.off()