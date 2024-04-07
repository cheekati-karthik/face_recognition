import face_recognition
import cv2
import os

# Function to load images and their corresponding labels
def load_images_from_folder(folder):
    images = []
    labels = []
    for root, dirs, files in os.walk(folder):
        for name in dirs:
            person_folder = os.path.join(root, name)
            for filename in os.listdir(person_folder):
                img_path = os.path.join(person_folder, filename)
                image = face_recognition.load_image_file(img_path)
                encoding = face_recognition.face_encodings(image)
                if len(encoding) > 0:
                    images.append(encoding[0])
                    labels.append(name)
    return images, labels

# Load training data
train_folder = "media"
known_face_encodings, known_face_labels = load_images_from_folder(train_folder)

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Initialize the webcam
video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Resize frame for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all face locations and encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match is found, use the label of the known face
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_labels[first_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame was resized
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()