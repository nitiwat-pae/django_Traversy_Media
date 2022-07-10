from multiprocessing import context
from typing import Type
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.

# rooms = [
#     {'id':1, 'name':'Lets learn python !'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend developers'}
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
            
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
        
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    
    if request.method == 'POST':
        print(request.POST)
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # commit=False is just return an object but has not save to database yet
            user.username = user.username.lower()
            user.save()
            # hint : If auto login after register, Please code as following below
            # login(request, user)   ---> Receive parameter to auto login
            # return redirect('home')  ---> Go to home page
            messages.success(request, 'Congraturations, your account has been successfully created !')
            return redirect('home')
        else:
            messages.error(request, 'Something error when you submit register !')
    
    context = {'page': page, 'form':form}
    return render(request, 'base/login_register.html', context)

def home(request):
    # print('request.GET is', request.GET) # <QueryDict: {'q': ['Python']}>
    # q = request.GET.get('q')
    # print(q) # Python
    
    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''
    
    print(q)
    # Another If condition pattern
    # q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    # icontains will ignore sensitive case
    # contains will focus sensitive case
    # rooms = Room.objects.all()
    rooms = Room.objects.filter( 
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    room_count = rooms.count
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
        )
    topics = Topic.objects.all()[0:5] # To limit topics at home page
    context = {'rooms':rooms, 'topics': topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() # message_set is pointer to class Message in models
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room':room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk) # Get user 1 id
    rooms = user.room_set.all() # Get all rooms which are under the user
    room_messages = user.message_set.all() # Get all room_messages which are under user
    topics = Topic.objects.all() # Get all topic from models.py
    context = {'user':user,'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)
        
        ''' ---- For original coding before update CSS part ----
        # print(request.POST)
        form = RoomForm(request.POST)
        if form.is_valid(): # Check any field correct or not ?
            #form.save() # Save data into database
            room = form.save(commit=False) # save but does not commit
            room.host = request.user # To add host to form
            room.save() # Save to database
            return redirect('home')
        ---- For original coding before update CSS part ---- '''
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    
    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk) # get any value existing from Room object
    form = RoomForm(instance=room) # instance is pre-fill and get data to pre-fill from room
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
        ''' ---- For original coding before update CSS part ----
        # print(request.POST)
        form = RoomForm(request.POST, instance=room) # To let django know which room will be updated --> Must use instance
        if form.is_valid():
            form.save()
            return redirect('home')
        ---- For original coding before update CSS part ---- '''
    
    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    context = {'obj':room}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    
    # get 'q' value from url at html
    # use for redirect at the bottom of this function
    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''
    
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        message.delete()
        
        # Self add condition not in video youtube --> So proud !!! haha-----------------
        # Cross check between messages and participants in a room
        # if not found participant in messages then remove it
        room = Room.objects.get(id=message.room.id)
        room_messages = room.message_set.all()
        participants = room.participants.all()
        list_messages = []
        for room_message in room_messages:
            list_messages.append(room_message.user)
        for user in participants:
            if user not in list_messages:
                room.participants.remove(user)
        # Self add condition not in video youtube --> So proud !!! haha-----------------
        
        # separate redirect
        if q == 'home':
            return redirect('home')
        else:
            return redirect('room', message.room.id)
    
    context = {'obj':message}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=request.user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    
    context = {'form':form}
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context={'topics':topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()
    context={'room_messages':room_messages}
    return render(request, 'base/activity.html', context)