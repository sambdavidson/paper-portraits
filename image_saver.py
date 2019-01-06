import time
import datetime
import os
import socket
import debug_print
from google.cloud import storage

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

# Google Cloud Bucket
GOOGLE_CLOUD_BUCKET_NAME = 'paper-portraits-faces'
google_cloud_client = None


def set_google_cloud_identity(filepath):
    global google_cloud_client
    print('Loading Google Cloud Identity: ', filepath)
    google_cloud_client = storage.Client.from_service_account_json(filepath)


def save_image(image):
    """Save passed image to the face folder.
    Encodes current timestamp as file name.
    """
    global saved_images
    if saved_images >= MAX_IMAGE_SAVED_COUNT:
        return
    saved_images += 1

    image_name = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S.png')
    image_path = os.path.join(FACE_FOLDER, image_name)
    image.save(image_path, "PNG")
    if has_internet_access():
        save_to_google_cloud(image_name, image_path)


def save_to_google_cloud(image_name, image_path):
    if google_cloud_client is None:
        return
    try:
        bucket = google_cloud_client.get_bucket(GOOGLE_CLOUD_BUCKET_NAME)
        image_blob = bucket.blob(image_name)
        image_blob.upload_from_filename(image_path)
    except Exception as e:
        debug_print.error('Error uploading image ({}) to GCP Storage: {}', image_name, e)


def has_internet_access():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False
