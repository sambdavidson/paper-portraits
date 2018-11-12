from PIL import Image
from shutil import copyfile
import face_recognition
import subprocess

input_image = "sample/capture.jpg"
working_image = "sample/working.jpg"
output_image = "sample/face.jpg"

while True:
    # Copy the input image to working image because input is being modified constantly
    copyfile(input_image, working_image)

    real_image = Image.open(working_image)
    real_image.show()
    numpy_image = face_recognition.load_image_file(working_image)
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
