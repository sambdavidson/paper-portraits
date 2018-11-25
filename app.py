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

last_face = None


def capture_loop():
    global capture_image_width, capture_image_height, face_image_scale, camera, last_face
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

    print('Sharpness', sharpness(pil_image))
    face_location = largest_face_location(face_locations)

    face_encodings = face_recognition.face_encodings(numpy_image, known_face_locations=[face_location])

    if len(face_encodings) == 0:
        print('no encoding')
        return

    if last_face is not None:
        print('Distance from last', face_recognition.face_distance(face_encodings, last_face))
    last_face = face_encodings[0]

    face_location = (int(face_location[3] / face_image_scale),
                     int(face_location[0] / face_image_scale),
                     int(face_location[1] / face_image_scale),
                     int(face_location[2] / face_image_scale))

    displayed_face = face_crop_to_epd(pil_image, face_location)
    print('render')
    epd.display_frame(epd.get_frame_buffer(displayed_face))


def largest_face_location(face_locations):
    largest = None
    largest_area = 0
    for face_location in face_locations:
        area = (face_location[2] - face_location[0]) * (face_location[1] - face_location[3])
        if area > largest_area:
            largest_area = area
            largest = face_location
    return largest


def face_crop_to_epd(original, face_location):
    return crop_match_width(original, face_location, epd7in5.EPD_HEIGHT, epd7in5.EPD_WIDTH).rotate(270, expand=True)


def sharpness(image):
    im = image.convert('L')
    array = numpy.asarray(im, dtype=numpy.int32)
    gy, gx = numpy.gradient(array)
    gnorm = numpy.sqrt(gx**2 + gy**2)
    return numpy.average(gnorm)

def crop_match_width(original, face_location, width, height):
    x1 = face_location[0]
    y1 = face_location[1]
    x2 = face_location[2]
    y2 = face_location[3]
    face_width = x2 - x1
    face_height = y2 - y1
    aspect_ratio = height / width
    new_height = face_width * aspect_ratio
    extra_height = int(new_height - face_height)
    print(extra_height)
    y1 = max(y1 - int(extra_height / 2), 0)
    y2 = min(y2 + int(extra_height / 2), original.height)
    print(x1, y1, x2, y2, (x2 - x1) / (y2 - y1))
    return original.crop((x1, y1, x2, y2)).resize((width, height))


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
