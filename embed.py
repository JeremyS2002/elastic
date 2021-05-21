import face_recognition
import pickle
import cv2
import os
 
knownEncodings = []
knownNames = []
for file in os.listdir('db'):
    imagePath = os.path.join("db", file)
    # extract the person name from the image path
    name = os.path.splitext(imagePath.split(os.path.sep)[-1])[0]
    # load the input image and convert it from BGR (OpenCV ordering)
    # to dlib ordering (RGB)
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #Use Face_recognition to locate faces
    boxes = face_recognition.face_locations(rgb)
    # compute the facial embedding for the face
    encodings = face_recognition.face_encodings(rgb, boxes, model="large")
    # loop over the encodings
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)

data = {"encodings": knownEncodings, "names": knownNames}
f = open("face_enc", "wb")
f.write(pickle.dumps(data))
f.close()
