# FaceRecognitionImage is a wrapper that consumes the ageitgey face recognition library but takes some shortcuts.
# Rather than recomputing the raw face locations a bunch of times. They are saved and reused.
# Accesses a bunch of protected members. I am OK with that!

import face_recognition
import numpy


class FaceRecognitionImage:
    def __init__(self, numpy_image):
        self.numpy_image = numpy_image
        self.raw_face_locations = face_recognition._raw_face_locations(numpy_image)

    def face_locations(self):
        return [face_recognition._trim_css_to_bounds(face_recognition._rect_to_css(face.rect), self.numpy_image.shape)
                for face in self.raw_face_locations]

    def face_encodings(self):
        pose_predictor = face_recognition.pose_predictor_5_point
        raw_landmarks = [pose_predictor(self.numpy_image, face_location) for face_location in self.raw_face_locations]
        return [numpy.array(face_recognition.face_encoder.compute_face_descriptor(self.numpy_image, raw_landmark_set, 1)) for
                raw_landmark_set in raw_landmarks]

    def n_biggest_face_locations(self, n):
        if n < len(self.raw_face_locations):
            return None
        return sorted(self.face_locations(), key=box_area)[(-1*n):]

    def n_biggest_face_encodings(self, n):
        locations = [face_recognition._css_to_rect(face_location) for face_location in self.n_biggest_face_locations(n)]
        pose_predictor = face_recognition.pose_predictor_5_point
        raw_landmarks = [pose_predictor(self.numpy_image, face_location) for face_location in locations]
        return [
            numpy.array(face_recognition.face_encoder.compute_face_descriptor(self.numpy_image, raw_landmark_set, 1))
            for
            raw_landmark_set in raw_landmarks]

    def biggest_two_face_distance(self):
        encodings = self.n_biggest_face_encodings(2)

        return face_recognition.face_distance(encodings[0], encodings[1])


def box_area(box):
    return (box[2] - box[0]) * (box[1] - box[3])
