from PIL import Image
from io import BytesIO
from picamera import PiCamera
import face_recognition
import numpy
import leds
import debug_print
import face_recognition_image
from function_timer import default as dft

CAMERA_WIDTH = 2464  # Max width is 3280, square for facial recognition speed.
CAMERA_HEIGHT = 2464
# Factors of 2464: 2, 2, 2, 2, 2, 7, 11
FACIAL_RECOGNITION_IMAGE_SCALE = 14  # 2464 / 14 = 176:
# Face encoding difference must be at least this before we recognize it as a different face.
SAME_FACE_ENCODINGS_TOLERANCE = 0.3


class FaceFramer:
    def __init__(self, epd_module):
        print('Initializing FaceFramer...')
        self.last_fr_image = None
        self.displayed_fr_image = None
        self.require_new_face = False
        self.require_two_same_face = True
        self.no_display = False
        print('EPD')
        self.epd = epd_module.EPD()
        self.epd_width = epd_module.EPD_WIDTH
        self.epd_height = epd_module.EPD_HEIGHT
        print('PiCamera')
        self.camera = PiCamera()
        self.camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
        print('... Done.')

    def set_no_display(self, no_display):
        self.no_display = no_display

    def display_image_to_epd(self, image):
        if self.no_display:
            return
        dft.start_function('epd init')
        self.epd.init()
        dft.function_return()
        dft.start_function('get_frame_buffer')
        frame_buffer = self.epd.get_frame_buffer(image)
        dft.function_return()
        dft.start_function('display_frame')
        self.epd.display_frame(frame_buffer)
        dft.function_return()
        dft.start_function('epd sleep')
        self.epd.sleep()
        dft.function_return()

    def find_face(self):
        """Returns new face captured in PiCamera. Returns None if no new face was found."""
        image = self.__capture_photo()
        dft.time_action('__capture_photo')
        fr_image = face_recognition_image.FaceRecognitionImage(image, FACIAL_RECOGNITION_IMAGE_SCALE)
        dft.time_action('FaceRecognitionImage generation')

        if not fr_image.faces_exist_in_image():
            debug_print.info('No face found in capture.')
            return None

        if self.last_fr_image is None:
            if self.require_two_same_face:
                self.last_fr_image = fr_image
                debug_print.info('First face found but two are requires to display.')
                return None

        # A short distance means the same person stared for a long while AND the photo wasn't very blurry.
        # A large distance means its either a different person or one photo was blurry and gave bad encodings.
        if self.require_two_same_face and \
                face_recognition.face_distance([fr_image.largest_face_encodings()],
                                               self.last_fr_image.largest_face_encodings()) \
                > SAME_FACE_ENCODINGS_TOLERANCE:
            self.last_fr_image = fr_image
            debug_print.info('Last two faces were likely different. Settings require them to likely match.')
            return None
        dft.time_action('face_distance last two')
        # Check if its a new face/person, if not don't display it.
        # I think this gives this feeling like you have made your mark and its now a portrait of you, until of course
        # someone new comes along. I think it is up the context on whether this is a good UX. Can be toggled with the
        # function
        if self.require_new_face and self.displayed_fr_image is not None and \
                face_recognition.face_distance([fr_image.largest_face_encodings()],
                                               self.displayed_fr_image.largest_face_encodings()) \
                < SAME_FACE_ENCODINGS_TOLERANCE:
            # Face too similar, probably the same person
            self.last_fr_image = fr_image
            debug_print.info('Found face too similar to displayed face. Settings require a likely new person.')
            return None
        dft.time_action('face_distance displayed and next')
        self.last_fr_image = fr_image
        self.displayed_fr_image = fr_image
        # Crop, draw, and return face.
        return self.__crop_face_to_epd(image, fr_image.largest_face_location()).convert('1')

    def change_require_new_face(self, require=None):
        """Toggles whether we require a new face outside of the tolerances before displaying.
        Supplying require=True or require=False sets the requirement to that bool instead."""
        if require is not None:
            self.require_two_same_face = require
        else:
            self.require_two_same_face = not self.require_two_same_face

        if self.require_two_same_face:
            debug_print.info('Enable require a new face than the one currently displayed.')
            leds.blink_green_led()
        else:
            debug_print.info('Disable require a new face than the one currently displayed.')
            leds.blink_red_led()

    def change_require_two_same_face(self, require=None):
        """Toggles whether we require a new face outside of the tolerances before displaying.
        Supplying require=True or require=False sets the requirement to that bool instead."""
        if require is not None:
            self.require_new_face = require
        else:
            self.require_new_face = not self.require_new_face

        if self.require_new_face:
            debug_print.info('Enable require of two same face in a row.')
            leds.blink_green_led()
        else:
            leds.blink_red_led()

    def __capture_photo(self):
        """Captures a photo from the PiCamera and returns it as a PIL Image."""
        stream = BytesIO()
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        return Image.open(stream)

    def __crop_face_to_epd(self, pil_image, face_location):
        """Crops the input PIL Image to fit the face at face_location to the EPD width and height."""
        w = self.epd_height  # Swap because we are looking at the face in portrait but the actual display is landscape.
        h = self.epd_width  # Swap because we are looking at the face in portrait but the actual display is landscape.
        x1 = face_location[0]
        y1 = face_location[1]
        x2 = face_location[2]
        y2 = face_location[3]
        face_width = x2 - x1
        face_height = y2 - y1
        aspect_ratio = h / w
        new_height = face_width * aspect_ratio
        extra_height = int(new_height - face_height)
        y1 = max(y1 - int(extra_height / 2), 0)
        y2 = min(y2 + int(extra_height / 2), pil_image.height)
        return pil_image.crop((x1, y1, x2, y2)).resize((w, h)).rotate(270, expand=True)

    @staticmethod
    def __largest_bounding_box(bounding_boxes):
        """Returns the largest of an input array of bounding boxes. Returns None if array empty."""
        largest = None
        largest_area = 0
        for bounding_box in bounding_boxes:
            area = (bounding_box[2] - bounding_box[0]) * (bounding_box[1] - bounding_box[3])
            if area > largest_area:
                largest_area = area
                largest = bounding_box
        return largest


