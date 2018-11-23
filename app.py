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

def capture_loop():
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

    face_location = face_locations[0]

    pil_face = pil_image.crop((int(face_location[3] / face_image_scale),
                           int(face_location[0] / face_image_scale),
                           int(face_location[1] / face_image_scale),
                           int(face_location[2] / face_image_scale)))

    displayed_face = face_crop_to_epd(pil_face)
    print('render')
    epd.display_frame(epd.get_frame_buffer(displayed_face))


def face_crop_to_epd(pil_face):
    return crop_match_width(pil_face, epd7in5.EPD_HEIGHT, epd7in5.EPD_WIDTH).rotate(270, expand=True)
    #return crop_match_height(pil_face, epd7in5.EPD_HEIGHT, epd7in5.EPD_WIDTH).rotate(270, expand=True)


def crop_match_height(pil_face, width, height):
    resize_ratio = pil_face.height / height
    resize_width = int(pil_face.width / resize_ratio)
    resized_face = pil_face.resize((resize_width, height))
    extra_width = resize_width - width
    x1 = max(min(extra_width / 2, resize_width),0)
    y1 = 0
    x2 = max(min(resize_width - (extra_width / 2), resize_width), 0)
    y2 = height
    cropped_face = resized_face.crop((x1, y1, x2, y2))
    return cropped_face


def crop_match_width(pil_face, width, height):
    resize_ratio = pil_face.width / width
    resize_height = int(pil_face.height / resize_ratio)
    resized_face = pil_face.resize((width, resize_height))
    out_image = Image.new("RGB", (width, height), color="white")
    extra_height = height - resize_height
    y1 = max(min(extra_height / 2), height, 0)
    y2 = max(min(height - (extra_height / 2), height), 0)
    out_image.paste(resized_face, box=(0, y1, width, y2))
    return out_image


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
    capture_loop()
