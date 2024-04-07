from django.shortcuts import render, redirect
from .forms import PhotoForm
from .models import Photo
import os 
from django.conf import settings
import pickle  # Import pickle module
import cv2
import numpy as np
import face_recognition
from django.http import StreamingHttpResponse,JsonResponse
from django.views.decorators import gzip

def home(request):
    return render(request,'home.html')


def upload_photos(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            images = request.FILES.getlist('images')

            # Create folder if it doesn't exist
            folder_path = os.path.join(settings.MEDIA_ROOT, user.username)
            os.makedirs(folder_path, exist_ok=True)

            for image in images:
                # Save the image to the folder
                image_path = os.path.join(folder_path, image.name)
                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                # Create a new Photo object for each image
                Photo.objects.create(user=user, image=image_path)

            return redirect('success')
    else:
        form = PhotoForm()
    return render(request, 'upload_photos.html', {'form': form})
    

def upload_success(request):
    return render(request, 'upload_success.html')

def load_images_from_folder(folder):
    images = []
    classNames = []
    for class_folder in os.listdir(folder):
        class_path = os.path.join(folder, class_folder)
        if os.path.isdir(class_path):
            for filename in os.listdir(class_path):
                img_path = os.path.join(class_path, filename)
                curImg = cv2.imread(img_path)
                if curImg is not None:
                    images.append(curImg)
                    classNames.append(class_folder)
    return images, classNames

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(img)
        if len(face_encodings) > 0:
            encode = face_encodings[0]
            encodeList.append(encode)
        else:
            print("No face found in one of the images.")
    return encodeList

def training(request):
    path = 'media'
    print(path)
    images, classNames = load_images_from_folder(path)
    print(classNames)
    attendance_set = set()
    encodeListKnown = findEncodings(images)
    pickle_file = 'trained_model.pkl'
    if os.path.exists(pickle_file):
        os.remove(pickle_file)
    with open(pickle_file, 'wb') as f:
        pickle.dump(encodeListKnown, f)
    # Save classNames in a separate pickle file
    with open('classNames.pkl', 'wb') as f:
        pickle.dump(classNames, f)
    return render(request,"train_success.html")

def generate_frames():
    cap = cv2.VideoCapture(0)
    pickle_file = 'trained_model.pkl'
    with open(pickle_file, 'rb') as f:
        encodeListKnown = pickle.load(f)
    # Load classNames from the separate pickle file
    with open('classNames.pkl', 'rb') as f:
        classNames = pickle.load(f)

    while True:
    
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # Perform face recognition (you'll need to define `encodeListKnown` and `classNames`)
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            if len(faceDis) > 0:
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        # Convert the image to JPEG format
        _, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def face_recognition_view(request):
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


