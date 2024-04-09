from django.shortcuts import render, redirect
from .forms import PhotoForm,StudentForm
from .models import Photo,StudentDetail
import os 
from django.conf import settings
import pickle  # Import pickle module
import cv2
import numpy as np
import face_recognition
from django.http import StreamingHttpResponse,JsonResponse
from django.views.decorators import gzip
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .models import Attendance
from django.contrib.auth.models import User

def home(request):
    is_admin = request.user.is_staff
    photo_exist=True
    if request.user.is_authenticated:
        photo_exist = len(Photo.objects.filter(user=request.user))<4

    context={
        'is_admin':is_admin,
        'photo_exist':photo_exist,
    }
    return render(request,'home.html',context)


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

@login_required
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
                    user = User.objects.get(username=name)  # Assuming 'User' is your user model
                    now = datetime.now()
                    today_date = now.date()
                    time_in = now.time()
                    try:
                        attendance = Attendance.objects.get(user=user,date = now.date())
                        time_recorded = datetime.combine(attendance.date, attendance.time_in)
                        current_time = datetime.now()
                        time_difference = current_time - time_recorded
                        if time_difference > timedelta(hours=6) and attendance.time_out!='00:00':
                            attendance.time_out=time_in
                            attendance.save()
                        else:
                            continue
                    except Attendance.DoesNotExist:
                        attendance = Attendance.objects.create(user=user,date=today_date,time_in=time_in,time_out='00:00')
        _, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def face_recognition_view(request):
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def studentattendance(request):
    user= request.user
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        # Filter Attendance records based on provided parameters
        attendance_records = Attendance.objects.filter(
            date__range=[from_date, to_date]
        )
        attendance_records = attendance_records.filter(
                user__username=user
            )
        
        context={ 'attendance_records' : attendance_records }
        
        return render(request, 'studentattendance.html', context)
    else:
        return render(request, 'studentattendance.html')

    

def staffattendance(request):
    users = User.objects.all()
    context = {
            'users': users,
        }
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        class_choice = request.POST.get('class_choice')
        department_choice = request.POST.get('department_choice')
        username = request.POST.get('username')
        # Filter Attendance records based on provided parameters
        attendance_records = Attendance.objects.filter(
            date__range=[from_date, to_date]
        )
        
        # If class_choice is not 'All', filter by class
        if class_choice != 'ALL':
            attendance_records = attendance_records.filter(
                user__studentdetail__Class=class_choice
            )
        
        # If department_choice is not 'All', filter by department
        if department_choice != 'ALL':
            attendance_records = attendance_records.filter(
                user__studentdetail__department=department_choice
            )

        if username!='ALL':
            attendance_records = attendance_records.filter(
                user__username=username
            )
        
        context ['attendance_records']= attendance_records
        
        return render(request, 'staffattendance.html', context)
    else:
        return render(request, 'staffattendance.html',context)
@login_required
def details(request):
    user = request.user
    try:
        student_details = StudentDetail.objects.get(user=user)
        form = StudentForm(instance=student_details)
        is_edit = True
    except StudentDetail.DoesNotExist:
        form = StudentForm()
        is_edit = False

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student_details if is_edit else None)
        if form.is_valid():
            form.instance.user = user
            form.save()  # This saves the data to the database
            return redirect('success')  # Redirect to a success page after saving

    return render(request, 'details.html', {'form': form, 'is_edit': is_edit})

# Success view if needed
def success(request):
    return render(request, 'success.html')
