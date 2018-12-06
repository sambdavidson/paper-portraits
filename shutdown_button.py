# Handles the shutdown button
from gpiozero import Button
from threading import Timer
from subprocess import call

GPIO_PIN = 5
REQUIRED_CLICKS = 5
TIMEOUT = 5

active_clicks = 0
timeout_timer = None
# Function to run before shutdown. Called if defined by user.
pre_shutdown_function = None

# Tracks if we are shutting down. Don't want to call shutdown callbacks a bunch
__shutting_down = False


def click_with_timeout():
    global active_clicks, timeout_timer, __shutting_down

    if __shutting_down:
        return

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
    global pre_shutdown_function, __shutting_down
    __shutting_down = True

    if pre_shutdown_function is not None:
        if callable(pre_shutdown_function):
            pre_shutdown_function()
        else:
            print("WARNING: pre-shutdown function not callable")

    # call("sudo shutdown -h now", shell=True) # UNCOMMENT WHEN ACTUALLY IN PHOTO FRAME
    quit() # Used instead of shutdown for testing.


button = Button(GPIO_PIN)
button.when_pressed = click_with_timeout
