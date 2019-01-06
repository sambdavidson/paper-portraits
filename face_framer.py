from PIL import Image
from io import BytesIO
from picamera import PiCamera
import face_recognition
import numpy
import leds
import debug_print
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
        self.last_face_encodings = None
        self.displayed_face_encodings = None
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
        img = self.__capture_photo()
        dft.time_action('__capture_photo')
        dft.start_function('__largest_face_location_and_encodings')
        face, enc = self.__largest_face_location_and_encodings(img)
        dft.function_return()

        if face is None or enc is None:
            debug_print.info('No face found.')
            return None

        if self.last_face_encodings is None:
            self.last_face_encodings = enc
            if self.require_two_same_face:
                debug_print.info('First face.')
                return None
        # A short distance means the same person stared for a long while AND the photo wasn't very blurry.
        # A large distance means its either a different person or one photo was blurry and gave bad encodings.
        if self.require_two_same_face and \
                face_recognition.face_distance([enc], self.last_face_encodings) > SAME_FACE_ENCODINGS_TOLERANCE:
            self.last_face_encodings = enc
            debug_print.info('Two different faces in a row.')
            return None

        # Check if its a new face/person, if not don't display it.
        # I think this gives this feeling like you have made your mark and its now a portrait of you, until of course
        # someone new comes along. I think it is up the context on whether this is a good UX. Can be toggled with the
        # function
        if self.require_new_face and self.displayed_face_encodings is not None and \
                face_recognition.face_distance([enc], self.displayed_face_encodings) < SAME_FACE_ENCODINGS_TOLERANCE:
            # Face too similar, probably the same person
            debug_print.info('Face too similar to previous.')
            return None
        dft.time_action('face_distances')
        self.last_face_encodings = enc
        self.displayed_face_encodings = enc
        # Crop, draw, and return face.
        return self.__crop_face_to_epd(img, face).convert('1')

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

    def __largest_face_location_and_encodings(self, pil_image):
        """Returns a tuple of the largest face location and its encoding or None if no face is found."""
        cv_width = int(pil_image.width / FACIAL_RECOGNITION_IMAGE_SCALE)
        cv_height = int(pil_image.height / FACIAL_RECOGNITION_IMAGE_SCALE)
        numpy_image = numpy.array(pil_image.resize([cv_width, cv_height]))
        face_locations = face_recognition.face_locations(numpy_image)
        if len(face_locations) == 0:
            return None, None

        largest_face = self.__largest_bounding_box(face_locations)
        face_encodings = face_recognition.face_encodings(numpy_image, known_face_locations=[largest_face])
        if len(face_encodings) == 0:
            return None, None

        largest_face_rescaled = (int(largest_face[3] * FACIAL_RECOGNITION_IMAGE_SCALE),
                                 int(largest_face[0] * FACIAL_RECOGNITION_IMAGE_SCALE),
                                 int(largest_face[1] * FACIAL_RECOGNITION_IMAGE_SCALE),
                                 int(largest_face[2] * FACIAL_RECOGNITION_IMAGE_SCALE))
        return largest_face_rescaled, face_encodings[0]

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


# Assumes all image sizes are equal to CAMERA resolutions.
def horizontal_join_images(img1, img2):
    new_image = Image.new('RGB', (CAMERA_WIDTH * 2, CAMERA_HEIGHT))
    new_image.paste(img1, (0, 0))
    new_image.paste(img2, (CAMERA_WIDTH, 0))
