from django.shortcuts import render, HttpResponse, redirect
from django.db import models
from .models import User, Device, Event, Media
import bcrypt, sys, os, base64, datetime, hashlib, hmac 
from django.contrib import messages
import boto3, csv
client = boto3.client('s3') #low-level functional API
resource = boto3.resource('s3') #high-level object-oriented API
test_bucket = resource.Bucket('pi-1') #subsitute this for your s3 bucket name. 

def index(request):
    return render(request, "homepage.html")
def registerLoginPage(request):
    return render(request, "registerPage.html")
def adminLogin(request):
    return render(request, "adminLogin.html")

def returnAllUsers(request):
    allUsers = test_bucket.objects.filter(Prefix="user")
    allUsersDict = {}
    for i in range(1, 100):
        userName = "user" + str(i)
        objs = list(test_bucket.objects.filter(Prefix=userName))
        if len(objs) > 0:
            bucket_images = userName + "/images"
            bucket_videos = userName + "/videos"
            throw_images = bucket_images + "/"
            throw_videos = bucket_videos + "/"
            this_users_images = test_bucket.objects.filter(Prefix=bucket_images)
            this_users_videos = test_bucket.objects.filter(Prefix=bucket_videos)
            thisUser = test_bucket.objects.filter(Prefix=userName)
            allImages = []
            allVideos = []
            images = test_bucket.objects.filter(Prefix="/images")
            for image in this_users_images:
                if image.key != throw_images:
                    allImages.append(image.key)
            videos = test_bucket.objects.filter(Prefix=userName + "/videos")
            for video in this_users_videos:
                if video.key != throw_videos:
                    allVideos.append(video.key)
                allVideos.append(video.key)
            newDict = {"images": allImages,
                        "videos": allVideos,        
            }
            allUsersDict[userName] = newDict
        else:
            return allUsersDict
        # if test_bucket.objects.filter(Prefix=userName).count() > 0:
        #     thisUser = test_bucket.objects.filter(Prefix=userName)
        #     allUsersDict.update({userName:thisUser})
    return allUsersDict

def returnOneUser(request):
    thisUserInfo = {}
    device_number = request.session['deviceId']
    userName = "user" + str(device_number)
    bucket_images = userName + "/images"
    bucket_videos = userName + "/videos"
    throw_images = bucket_images + "/"
    throw_videos = bucket_videos + "/"
    this_users_images = test_bucket.objects.filter(Prefix=bucket_images)
    this_users_videos = test_bucket.objects.filter(Prefix=bucket_videos)
    thisUser = test_bucket.objects.filter(Prefix=userName)
    allImages = []
    allVideos = []
    images = test_bucket.objects.filter(Prefix="/images")
    for image in this_users_images:
        if image.key != throw_images:
            allImages.append(image.key)
    videos = test_bucket.objects.filter(Prefix=userName + "/videos")
    for video in this_users_videos:
        if video.key != throw_videos:
            allVideos.append(video.key)
    newDict = {"images": allImages,
                "videos": allVideos,        
    } 
    thisUserInfo[userName] = newDict
    return thisUserInfo

def createUser(request):
    if request.method=="POST":
        errors = User.objects.basic_validator(request.POST)
        if len(errors):
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/registerLoginPage', errors)
        else:
            imgCount = 0
            vidCount = 0
            device_number = request.POST['deviceNumber']
            bucket_select = "user" + device_number
            bucket_images = bucket_select + "/images"
            bucket_videos = bucket_select + "/videos"
            throw_images = bucket_images + "/"
            throw_videos = bucket_videos + "/"
            this_users_images = test_bucket.objects.filter(Prefix=bucket_images)
            this_users_videos = test_bucket.objects.filter(Prefix=bucket_videos)
            newEmail = request.POST['usersEmail']
            print(newEmail.lower())
            User.objects.create(full_name=request.POST['usersName'], email_address=newEmail.lower(), phone_number=request.POST['usersPhone'], number_pics = imgCount, number_vids = vidCount, device_key_name=request.POST['deviceNumber'])
            last_user = User.objects.last()
            request.session['user_id'] = last_user.id
            Device.objects.create(device_owner = User.objects.get(device_key_name = device_number), device_key_name = "SerialNumber", number_pics = imgCount, number_vids = vidCount)
            user_with_id = User.objects.get(id=request.session['user_id'])
            request.session["deviceId"] = request.POST['deviceNumber']
            # The above line will be changed to S3 syntax to send the new user information to the database and will create a new user.
            return redirect('/userPage')
    return redirect('/')

def createEvent(request):
    if request.method == "POST":
        errors = Event.objects.basic_validator(request.POST)
        print(errors)
        if len(errors):
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/godMode', errors)
        else:
            Event.objects.create(name=request.POST['eventName'], venue_name=request.POST['venueName'], address=request.POST['address'], start_date=request.POST['startDate'], end_date=request.POST['endDate'])
    return redirect("/godMode")

def login(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)
        if len(errors):
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/registerLoginPage', errors)
        checkEmail = request.POST['emailsLogin']
        passEmail = checkEmail.lower()
        if User.objects.filter(email_address=passEmail):
            user = User.objects.get(email_address=passEmail)
            if user.device_key_name == request.POST['deviceNumber']:
                request.session['user_id'] = user.id
                request.session["deviceId"] = request.POST['deviceNumber']
                return redirect('/userPage')
    return redirect('/')

def userPage(request):
    allUsers = test_bucket.objects.filter(Prefix="user")
    user_id = User.objects.get(id=request.session['user_id'])
    device_id = Device.objects.get(device_owner = user_id.id)
    device_number = user_id.device_key_name
    bucket_select = "user" + device_number
    bucket_images = bucket_select + "/images"
    throw_images = bucket_images + "/"
    bucket_videos = bucket_select + "/videos"
    throw_videos = bucket_videos + "/"
    file_name = bucket_select + "/"
    this_users_files = test_bucket.objects.filter(Prefix=bucket_select)
    this_users_images = test_bucket.objects.filter(Prefix=bucket_images)
    this_users_videos = test_bucket.objects.filter(Prefix=bucket_videos)
    imgCount = 0
    for image in this_users_images:
        imgCount += 1
    vidCount = 0
    for vid in this_users_videos:
        vidCount += 1
    user_id.number_pics = imgCount
    user_id.number_vids = vidCount
    device_id.number_pics = imgCount
    device_id.number_vids = vidCount
    user_id.save()
    device_id.save()
    context = {
        'name':user_id.full_name,
        'this_user': this_users_files,
        'this_user_images': this_users_images,
        'this_user_videos': this_users_videos,
        'file_name': file_name,
        'not_bucket_select_img': throw_images,
        'not_bucket_select_vid': throw_videos,
        "allEvents": Event.objects.all(),
    }
    imagesVideos = {
        'userName':user_id.full_name,
        'images': this_users_images,
        'videos': this_users_videos,
    }
    return render(request, "eventPage.html", context, imagesVideos)

def updateSqlDatabase(request):
    for s3Image in this_users_images:
        for image in this_user_media:
            checkImage = bucket_images + "/" + image.s3_key
            print(checkImage)
            if test_bucket.objects.filter(Prefix=image.s3_key):
                print("matching")
    return redirect("/userPage")

def viewImage(request):
    return render(request, "viewImage.html")

def godModeCheck(request):
    if request.method == "POST":
        if request.POST['godModeLogin'] == "Dylan Rose" and request.POST['godModePassword'] == "isourboss":
            request.session['user_id'] = 0
            return redirect('/godMode')
        else:
            return redirect('/adminLogin')

def godMode(request):
    if request.session['user_id'] != 0:
        print("get out of here")
        return redirect('/adminLogin')
    else:
        event_images = Media.objects.filter(event=1)
        context = {
            'users': User.objects.all(),
            'devices': Device.objects.all(),
            'events': Event.objects.all()
        }
        context['objects'] = test_bucket.objects.filter(Prefix='user')
        context['battery'] = test_bucket.objects.filter(Prefix='user2/battery.csv')
        return render(request, "godMode.html", context)

def viewUserInfoGodMode(request, user_num):
    user_id = User.objects.get(device_key_name=user_num)
    bucket_select = "user" + user_num
    bucket_images = bucket_select + "/images"
    throw_images = bucket_images + "/"
    bucket_videos = bucket_select + "/videos"
    throw_videos = bucket_videos + "/"
    file_name = bucket_select + "/"
    # key_name = throw_images + "battery.csv"
    # obj = client.get_object(Bucket='test_bucket', Key=key_name)
    # grid_sizes = pd.read_csv(obj['Body'])
    this_users_files = test_bucket.objects.filter(Prefix=bucket_select)
    this_users_images = test_bucket.objects.filter(Prefix=bucket_images)
    this_users_videos = test_bucket.objects.filter(Prefix=bucket_videos)
    battery_select = bucket_select + "/battery.csv"
    battery_info = test_bucket.objects.filter(Prefix=battery_select)
    context = {
        'name':user_num,
        'file_name': file_name,
        'this_user_images': this_users_images,
        'this_user_videos': this_users_videos,
        'not_bucket_select_img': throw_images,
        'not_bucket_select_vid': throw_videos,
    }
    return render(request, "viewUserInfoGodMode.html", context)

def logout(request):
    request.session.clear()
    return redirect('/')

def deleteUser(request, user_id):
    User.objects.get(id=user_id).delete()
    return redirect('/godMode')

def deleteImage(request, match, url):
    print("Delete Image " + match)
    # client.delete_object(Bucket='test_bucket', Key=match)
    return redirect('/' + url)
    