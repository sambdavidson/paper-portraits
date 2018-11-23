from PIL import Image, ImageDraw, ImageFont
from picamera import PiCamera
from io import BytesIO
import face_recognition
import subprocess
import sys
import numpy
import epd7in5

capture_path = "sample/capture.jpg"
output_path = "sample/face.jpg"

ERROR_LIMIT = 10
error_count = 0
capture_image_width = 3280
capture_image_height = 2464
face_image_scale = 0.125

print('Initializing EPD')
epd = epd7in5.EPD()
epd.init()

print('Initializing PiCamera')
camera = PiCamera()
camera.resolution = (capture_image_width, capture_image_height)

def loop():
    global capture_image_width, capture_image_height, face_image_scale, camera
    reset_error_count()

    stream = BytesIO()
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    pil_image = Image.open(stream)
    numpy_image = numpy.array(pil_image.resize([int(capture_image_width * face_image_scale),
                                                int(capture_image_height * face_image_scale)]))
    face_locations = face_recognition.face_locations(numpy_image)

    if len(face_locations) == 0:
        return
    
    face_landmarks_list = face_recognition.face_landmarks(numpy_image, face_locations=face_locations[:1])

    if len(face_landmarks_list) == 0:
        print('No landmarks for found for face location')
        return

    print('editing')
    face_location = face_locations[0]
    face_landmarks = face_landmarks_list[0]

    pil_face = pil_image.crop((int(face_location[3] / face_image_scale),
                           int(face_location[0] / face_image_scale),
                           int(face_location[1] / face_image_scale),
                           int(face_location[2] / face_image_scale)))

    displayed_face = face_crop_to_epd(pil_face)
    print('render')
    epd.display_frame(epd.get_frame_buffer(displayed_face))


def face_crop_to_epd(pil_face):
    # Compared to EPD_WIDTH because the image will be displayed rotated 90deg
    resize_ratio = pil_face.height / epd7in5.EPD_WIDTH
    resize_width = int(pil_face.width / resize_ratio)
    resized_face = pil_face.resize((resize_width, epd7in5.EPD_WIDTH))
    extra_width = resize_width - epd7in5.EPD_HEIGHT
    cropped_face = resized_face.crop((extra_width/2, 0, resize_width - (extra_width/2), epd7in5.EPD_WIDTH))
    return cropped_face.rotate(270, expand=True)

# Captures image from webcam and saves to the specified path
def capture_image_to_path(path):
    global capture_image_width, capture_image_height
    retry = True
    while retry:
        print('fswebcam start')
        try:
            subprocess.run(['fswebcam', '-r', '{}x{}'.format(capture_image_width, capture_image_height), '-q',
                            '--no-banner', '--save', path], check=True)
            print('fswebcam done')
            retry = False
        except subprocess.CalledProcessError as e:
            error(e)


# Set drawn image
def set_drawn_image(path):
    print('killall')
    subprocess.run(['killall', 'fbi'])
    retry = True
    while retry:
        print('fbi')
        try:
            subprocess.run(['fbi', '-T', '2', '-a', path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            retry = False
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

print('Running main loop...')
while True:
    loop()
