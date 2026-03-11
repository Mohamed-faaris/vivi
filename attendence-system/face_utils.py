import face_recognition
import numpy as np
import pickle


def get_face_encoding(image):
    encodings = face_recognition.face_encodings(image)

    if len(encodings) > 0:
        return encodings[0]

    return None


def detect_face(image):
    face_recognition.face_locations(image)
    locs = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, locs)

    if len(encodings) > 0:
        return locs[0], encodings[0]

    return None, None


def crop_face(image, face_location):
    top, right, bottom, left = face_location
    return image[top:bottom, left:right]


def encode_to_blob(encoding):
    return pickle.dumps(encoding)


def decode_blob(blob):
    return pickle.loads(blob)


def compare_faces(known_encodings, face_encoding):
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    face_distances = face_recognition.face_distance(known_encodings, face_encoding)

    if len(face_distances) == 0:
        return None

    best_match = np.argmin(face_distances)

    if matches[best_match]:
        return best_match

    return None
