from PIL import Image
from io import BytesIO
from picamera import PiCamera
import face_recognition
import numpy

CAMERA_WIDTH = 3280
CAMERA_HEIGHT = 2464
FACIAL_RECOGNITION_IMAGE_SCALE = 0.125
# Face encoding difference must be at least this before a new face is drawn
NEW_FACE_ENCODINGS_TOLERANCE = 0.3


class FaceFramer:
    def __init__(self, epd_module):
        print('Initializing FaceFramer...')
        self.last_face_encodings = None
        self.displayed_face_encodings = None
        print('EPD')
        self.epd = epd_module.EPD()
        self.epd.init()
        self.epd_width = epd_module.EPD_WIDTH
        self.epd_height = epd_module.EPD_HEIGHT
        print('PiCamera')
        self.camera = PiCamera()
        self.camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
        print('... Done.')

    def display_image(self, image):
        self.epd.display_frame(self.epd.get_frame_buffer(image))

    def find_new_face_and_display_to_epd(self):
        """Returns new face captured and displayed to EPD. Returns None if no new face was found."""
        img = self.__capture_photo()
        face, enc = self.__largest_face_location_and_encodings(img)
        if face is None or enc is None:
            return None

        if self.last_face_encodings is None:
            self.last_face_encodings = enc
            return None

        # A short distance means the same person stared for a long while AND the photo wasn't very blurry.
        # A large distance means its either a different person or one photo was blurry and gave bad encodings.
        if face_recognition.face_distance([enc], self.last_face_encodings) > NEW_FACE_ENCODINGS_TOLERANCE:
            self.last_face_encodings = enc
            return None

        # TODO: Add a condition requiring a new person before the face changes. Potentially toggle based on buttons
        # if face_distance_from_displayed_face(...) < NEW_FACE_ENCODINGS_TOLERANCE: don't display

        self.last_face_encodings = enc
        self.displayed_face_encodings = enc
        # Crop, draw, and return face.
        epd_face = self.__crop_face_to_epd(img, face).convert('1')
        self.display_image(epd_face)
        return epd_face

    def __capture_photo(self):
        """Captures a photo from the PiCamera and returns it as a PIL Image."""
        stream = BytesIO()
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        return Image.open(stream)

    def __largest_face_location_and_encodings(self, pil_image):
        """Returns a tuple of the largest face location and its encoding or None if no face is found."""
        cv_width = int(pil_image.width * FACIAL_RECOGNITION_IMAGE_SCALE)
        cv_height = int(pil_image.height * FACIAL_RECOGNITION_IMAGE_SCALE)
        numpy_image = numpy.array(pil_image.resize([cv_width, cv_height]))
        face_locations = face_recognition.face_locations(numpy_image)

        if len(face_locations) == 0:
            return None, None

        largest_face = self.__largest_bounding_box(face_locations)
        face_encodings = face_recognition.face_encodings(numpy_image, known_face_locations=[largest_face])

        if len(face_encodings) == 0:
            return None, None

        largest_face_rescaled = (int(largest_face[3] / FACIAL_RECOGNITION_IMAGE_SCALE),
                                 int(largest_face[0] / FACIAL_RECOGNITION_IMAGE_SCALE),
                                 int(largest_face[1] / FACIAL_RECOGNITION_IMAGE_SCALE),
                                 int(largest_face[2] / FACIAL_RECOGNITION_IMAGE_SCALE))
        return largest_face_rescaled, face_encodings[0]

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
        print(extra_height)
        y1 = max(y1 - int(extra_height / 2), 0)
        y2 = min(y2 + int(extra_height / 2), pil_image.height)
        print(x1, y1, x2, y2, (x2 - x1) / (y2 - y1))
        return pil_image.crop((x1, y1, x2, y2)).resize((w, h)).rotate(270, expand=True)
