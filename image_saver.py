import time
import datetime
import os

# TODO: Consider online storage buckets for these images. Something like Google GCS or something similar.

FACE_FOLDER = os.path.join(os.path.dirname(__file__), 'faces')
# Ensure FACE_FOLDER exists
if not os.path.isdir(FACE_FOLDER):
    os.mkdir(FACE_FOLDER)

# Figure out the max photos we should save. 4GB of free space gives us like 100,000+ photos which is a LOT.
# This is just a precaution in case this thing is sitting there seeing faces non-stop for weeks straight.
IMAGE_SIZE_APPROX = 30000  # 30kb
statvfs = os.statvfs('/')
free_space = statvfs.f_frsize * statvfs.f_bavail
MAX_IMAGE_SAVED_COUNT = int((free_space * 0.7) / IMAGE_SIZE_APPROX)

# Counter of saved images so far.
saved_images = 0


def set_google_cloud_identity_filepath(filepath):
    print('foo')


def save_image(image):
    """Save passed image to the face folder.
    Encodes current timestamp as file name.
    """
    global saved_images
    if saved_images >= MAX_IMAGE_SAVED_COUNT:
        return
    saved_images += 1

    filename = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S.png')
    image.save(os.path.join(FACE_FOLDER, filename), "PNG")
