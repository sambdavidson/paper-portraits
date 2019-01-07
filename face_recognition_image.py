# FaceRecognitionImage is a wrapper that consumes the ageitgey face recognition library but takes some shortcuts.
# Rather than recomputing the raw face locations a bunch of times. They are saved and reused.
# Accesses a bunch of protected members. I am OK with that!

from face_recognition import api
import numpy


class FaceRecognitionImage:
    def __init__(self, pil_image, scale):
        self.pil_image = pil_image
        self.cv_scale = scale
        self.numpy_image = shrunken_numpy_image(pil_image, scale)
        self.raw_face_locations = api._raw_face_locations(self.numpy_image)
        self._largest_face_encoding = None
        self._largest_face_location = None

    def faces_exist_in_image(self):
        return len(self.raw_face_locations) > 0

    def _face_locations(self):
        return [api._trim_css_to_bounds(api._rect_to_css(face.rect), self.numpy_image.shape)
                for face in self.raw_face_locations]

    def face_encodings(self):
        pose_predictor = api.pose_predictor_5_point
        raw_landmarks = [pose_predictor(self.numpy_image, face_location) for face_location in self.raw_face_locations]

        self._largest_face_encoding = [numpy.array(api.face_encoder.compute_face_descriptor(self.numpy_image, raw_landmark_set, 1)) for
                raw_landmark_set in raw_landmarks]
        return self._largest_face_encoding

    def largest_face_location(self):
        if len(self.raw_face_locations) == 0:
            return None
        if self._largest_face_location is not None:
            return self._largest_face_location

        l = sorted(self._face_locations(), key=box_area)[(-1):]

        self._largest_face_location = (int(l[3] * self.cv_scale), int(l[0] * self.cv_scale),
                                       int(l[1] * self.cv_scale), int(l[2] * self.cv_scale))
        return self._largest_face_location


    def largest_face_encodings(self):
        if len(self.raw_face_locations) == 0:
            return None
        if self._largest_face_encoding is not None:
            return self._largest_face_encoding

        locations = [api._css_to_rect(face_location) for face_location in self.largest_face_location()]
        pose_predictor = api.pose_predictor_5_point
        raw_landmarks = [pose_predictor(self.numpy_image, face_location) for face_location in locations]
        self._largest_face_encoding = [
            numpy.array(api.face_encoder.compute_face_descriptor(self.numpy_image, raw_landmark_set, 1))
            for
            raw_landmark_set in raw_landmarks]
        return self._largest_face_encoding


def shrunken_numpy_image(pil_image, scale):
    cv_width = int(pil_image.width / scale)
    cv_height = int(pil_image.height / scale)
    return numpy.array(pil_image.resize([cv_width, cv_height]))


def box_area(box):
    return (box[2] - box[0]) * (box[1] - box[3])
