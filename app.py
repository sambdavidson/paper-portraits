from PIL import Image
import sys
import os
import face_framer
import epd7in5
import image_saver


ERROR_LIMIT = 10
ERROR_IMAGE_LOCATION = os.path.join(os.path.dirname(__file__), 'error_screen.png')
ERROR_LOG_LOCATION = os.path.join(os.path.dirname(__file__), 'log.txt')

error_count = 0
face_framer = face_framer.FaceFramer(epd7in5)
error_image = Image.open(ERROR_IMAGE_LOCATION)


def loop():
    """Main loop that runs FaceFramer work. Captures errors."""
    try:
        face = face_framer.find_new_face()
        if face is None:
            return
        face_framer.display_image_to_epd(face)
        image_saver.save_image(face.rotate(90, expand=True))
        reset_error_count()
    except Exception as e:
        error(e)


def reset_error_count():
    global error_count
    error_count = 0


def error(e):
    global error_count, error_image
    print('Error: {}'.format(e)) # TODO: Remove this to avoid STDOUT overflow
    error_count += 1
    if error_count == ERROR_LIMIT:
        face_framer.display_image_to_epd(error_image)
        sys.exit()


print('Running main loop...')
face_framer.display_image_to_epd(error_image)
while True:
    loop()
