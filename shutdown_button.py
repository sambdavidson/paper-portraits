# Handles the shutdown button
from gpiozero import Button
from threading import Timer

GPIO_PIN = 5
REQUIRED_CLICKS = 5
TIMEOUT = 5

active_clicks = 0
timeout_timer = None
# Function to run before shutdown. Called if defined by user.
pre_shutdown_function = None


def click_with_timeout():
    global active_clicks, timeout_timer
    if timeout_timer is not None:
        timeout_timer.cancel()
    timeout_timer = Timer(TIMEOUT, reset)
    active_clicks += 1
    if active_clicks >= REQUIRED_CLICKS:
        shutdown()


def reset():
    global active_clicks, timeout_timer
    active_clicks = 0
    timeout_timer = None


def shutdown():
    """Shuts down the Pi, called once enough clicks happened."""
    global pre_shutdown_function
    if pre_shutdown_function is not None:
        if callable(pre_shutdown_function):
            pre_shutdown_function()
        else:
            print("WARNING: pre-shutdown function not callable")

    print("SHUTTING DOWN")


button = Button(GPIO_PIN)
button.when_pressed = click_with_timeout
