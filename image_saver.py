import time
import datetime
import os

FACE_FOLDER = os.path.join(os.path.dirname(__file__), 'faces')
# Ensure FACE_FOLDER exists
if not os.path.isdir(FACE_FOLDER):
    os.mkdir(FACE_FOLDER)

# TODO: Figure out how big a face is and set limits based on SD card.


def save_image(image):
    """Save passed image to the face folder.
    Encodes current timestamp as file name.
    """
    filename = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S.png')
    image.save(os.path.join(FACE_FOLDER, filename), "PNG")
