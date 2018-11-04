import face_recognition

image = face_recognition.load_image_file("obama.jpg")

face_locations = face_recognitions.face_locations(image)

print face_locations[0]