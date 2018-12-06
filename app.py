from PIL import Image
from gpiozero import Button
import os
import time
import datetime
import epd7in5
import face_framer
import image_saver
import shutdown_button


ERROR_WARN_LIMIT = 3
ERROR_IMAGE_LOCATION = os.path.join(os.path.dirname(__file__), 'error_screen.png')
ERROR_LOG_LOCATION = os.path.join(os.path.dirname(__file__), 'errors.log')
SHUTDOWN_IMAGE_LOCATION = os.path.join(os.path.dirname(__file__), 'shutdown_screen.png')

consecutive_error_count = 0
face_framer = face_framer.FaceFramer(epd7in5)
error_image = Image.open(ERROR_IMAGE_LOCATION)
shutdown_image = Image.open(SHUTDOWN_IMAGE_LOCATION)

require_new_face_button = Button(26)
require_new_face_button.when_pressed = face_framer.change_require_new_face


def end_setup():
    shutdown_button.pre_shutdown_function = pre_shutdown


def loop():
    """Main loop that runs FaceFramer work. Captures errors."""
    try:
        face = face_framer.find_face()
        if face is None:
            return
        # TODO: Draw debug info based on buttons pressed.
        face_framer.display_image_to_epd(face)
        image_saver.save_image(face.rotate(90, expand=True))
        reset_consecutive_error_count()
    except Exception as e:
        error(e)


def reset_consecutive_error_count():
    global consecutive_error_count
    consecutive_error_count = 0


def error(e):
    global consecutive_error_count, error_image
    append_to_log(e)
    consecutive_error_count += 1
    if consecutive_error_count >= ERROR_WARN_LIMIT:
        face_framer.display_image_to_epd(error_image)


def append_to_log(text):
    with open(ERROR_LOG_LOCATION, 'a+') as logfile:
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
        logfile.write('\n\n{}:\n{}'.format(timestamp, text))


def pre_shutdown():
    face_framer.display_image_to_epd(shutdown_image)


end_setup()
print('Running...')
while True:
    loop()
