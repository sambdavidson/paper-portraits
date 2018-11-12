from PIL import Image
from shutil import copyfile
import face_recognition
import subprocess
import sys

input_image = "sample/capture.jpg"
output_image = "sample/face.jpg"

capture_path = "sample/capture.jpg"

ERROR_LIMIT = 10
error_count = 0


def loop():
    reset_error_count()
    capture_image_to_path(capture_path)
    real_image = Image.open(input_image)
    numpy_image = face_recognition.load_image_file(input_image)
    face_locations = face_recognition.face_locations(numpy_image)
    if len(face_locations) > 0:
        up = face_locations[0][0]
        down = face_locations[0][2]
        left = face_locations[0][3]
        right = face_locations[0][1]
        face = real_image.crop((left, up, right, down))
        face.save(output_image)
        print("Drawing face!", output_image)
        subprocess.run(['fbi', '-T', '2', '-a', output_image])
    else:
        print("No faces found")

# Captures image from webcam and saves to the specified path
def capture_image_to_path(path):
    try:
        subprocess.run(['fswebcam', '-r', '640x480', '--no-banner', '--save', path], check=True)
    except subprocess.CalledProcessError as e:
        error(e)


def reset_error_count():
    global error_count
    error_count = 0


def error(e):
    global error_count
    print('Error: {}'.format(e))
    error_count += 1
    if error_count == ERROR_LIMIT:
        sys.exit()


while True:
    loop()