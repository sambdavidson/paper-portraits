from PIL import Image
from gpiozero import Button
import sys
import os
import time
import datetime
import epd7in5
import leds
import face_framer
import image_saver
import shutdown_button
import debug_print
from function_timer import default as dft

WELCOME_IMAGE_LOCATION = os.path.join(os.path.dirname(__file__), 'welcome_screen.png')
ERROR_WARN_LIMIT = 3
ERROR_IMAGE_LOCATION = os.path.join(os.path.dirname(__file__), 'error_screen.png')
ERROR_LOG_LOCATION = os.path.join(os.path.dirname(__file__), 'errors.log')
SHUTDOWN_IMAGE_LOCATION = os.path.join(os.path.dirname(__file__), 'shutdown_screen.png')
REQUIRE_NEW_FACE_GPIO_PIN = 26

welcome_image = Image.open(WELCOME_IMAGE_LOCATION)
consecutive_error_count = 0
face_framer = face_framer.FaceFramer(epd7in5)
error_image = Image.open(ERROR_IMAGE_LOCATION)
shutdown_image = Image.open(SHUTDOWN_IMAGE_LOCATION)

require_new_face_button = Button(REQUIRE_NEW_FACE_GPIO_PIN)
require_new_face_button.when_pressed = face_framer.change_require_new_face


def end_setup():
    shutdown_button.pre_shutdown_function = pre_shutdown
    dft.start_function('display_image_to_epd')
    face_framer.display_image_to_epd(welcome_image)
    dft.function_return()


def loop():
    """Main loop that runs FaceFramer work. Captures errors."""
    try:
        dft.start_function('find_face')
        face = face_framer.find_face()
        dft.function_return()
        # TODO: clean these up
        if face is None:
            return
        # TODO: Draw debug info based on buttons pressed.
        dft.start_function('display_image_to_epd')
        face_framer.display_image_to_epd(face)
        dft.function_return()
        dft.start_function('save_image')
        image_saver.save_image(face.rotate(90, expand=True))
        dft.function_return()
        reset_consecutive_error_count()
    except Exception as e:
        error(e)


def reset_consecutive_error_count():
    global consecutive_error_count
    consecutive_error_count = 0


def error(e):
    global consecutive_error_count, error_image
    append_to_log(e)
    debug_print.error(e)
    consecutive_error_count += 1
    if consecutive_error_count >= ERROR_WARN_LIMIT:
        face_framer.display_image_to_epd(error_image)


def append_to_log(text):
    with open(ERROR_LOG_LOCATION, 'a+') as logfile:
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        error_metadata = 'Type: {}\tFile: {}\tLine: {}\tTime: {}'.format(exc_type, file, exc_tb.tb_lineno, timestamp)
        logfile.write('\n{}\n{}\n'.format(error_metadata, text))


def pre_shutdown():
    leds.turn_on_red()
    leds.turn_on_red()
    time.sleep(3)
    # face_framer.display_image_to_epd(shutdown_image)  # This image is fun but since it takes forever to push a frame


dft.time_action('global vars')
dft.start_function('end_setup')
end_setup()
dft.function_return()
debug_print.info('Startup Timings:\n' + dft.timings_string())

print('Running loop...')
while True:
    dft.reset('loop')
    loop()
    debug_print.info('TIMINGS:\n'+dft.timings_string())
