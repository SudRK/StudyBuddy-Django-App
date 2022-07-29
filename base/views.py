import email
from urllib import request
from django.contrib.auth.models import User
from pydoc_data.topics import topics
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Message, Room, Topic, User,ForgotPassword
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model

# imported for password change
from django.contrib.auth.forms import PasswordChangeForm

# imported for forgot password
import uuid
from .helpers import send_forgot_password_email
from .helpers import account_activation_email
from .forms import ChangePasswordCustomForm

# imported for registration email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .token import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from verify_email.email_handler import send_verification_email

from base import token

# imported for resending email
# from .forms import ResendActivationEmailForm

# Create your views here.

User=get_user_model()
def loginPage(request):
    page = 'login'
    
    # if request.user.is_authenticated:
    #     return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        status = True
        try:
            user = User.objects.get(email=email)
            if user.is_active != True:
                status = False
                messages.error(request, f'Oops, {user.email} not verified, so please verify your email!')
        except:
            messages.error(request, 'User does not exist!')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            
            login(request, user)
            #request.session.set_expiry(600) #Expire session in 10 minutes.
            return redirect('home') 
        else:
            if status == True:
                messages.error(request, 'Username or Password are incorrect!')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def register(request):
    page = 'register'
    form = MyUserCreationForm()

    if request.method == 'POST':
        # save form in the memory and not in the database
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # login(request, user)
            # return redirect('login')
            
            # to get the domain of the current site
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            account_activation_email(request=request, email=user.email, token=token, uidb64=uid)
            # messages.success(request, 'Form submission successful, please check your email')
            return render(request, 'base/email_active_sent.html')
        else:
            messages.error(request, form.errors)
            form = MyUserCreationForm()
    return render(request, 'base/login_register.html', {'form':form})

# view for resending verification email
def ResendMail(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user=User.objects.get(email=email)
        if not user:
            messages.error(request,"Please register your email address!")
        token = account_activation_token.make_token(user)
        print(token)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        account_activation_email(request=request, email=email, token=token, uidb64=uid)
        return HttpResponse('Please check your email for verification mail.')
    return render(request, 'base/email_active_sent.html')

# View for account activation
def Activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk = uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f'Thank You! Account verified successfully on {user.email}')
        return redirect('login')
    else:
        return


def logoutUser(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login') #login_required redirect directly to login page before any activity
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by("-created")
    context =  {'rooms': rooms,'topics':topics, 'room_count':room_count, 'room_messages': room_messages, 'q':q}
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.msg_for_room.all().order_by('created')
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
        
    context = {'room':room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    room = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'room':room, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed to update!')
        
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')    
        room.save()
        return redirect('home')
    
    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You are not allowed to update!')
        
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed to delete!')
        
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages})

def changepwd(request):
    if request.user.is_authenticated:
        user = request.user
        form = PasswordChangeForm(user)
        if request.method == 'POST':
            form = PasswordChangeForm(data=request.POST, user=request.user)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return redirect('home')
            else:
                form = PasswordChangeForm(user=request.user)
        return render(request, 'base/changepassword.html', {'form':form})
    else:
        return redirect('login')

# view for sending email for forgot password
 
def sendemail(request):
    if request.method=="POST":
        email=request.POST.get('email')
        user_obj=User.objects.filter(email=email).first()
        if not user_obj:
            messages.error(request, "User Not Found!!!!")
        else:
            user_obj_token=ForgotPassword.objects.filter(user__username=user_obj.username).first()
            token=str(uuid.uuid4())
            if user_obj_token:
                user_obj_token.forgot_password_token=token
                user_obj_token.save()
            else:
                new_token_obj=ForgotPassword.objects.create(user=user_obj,forgot_password_token=token)
                new_token_obj.save()
            send_forgot_password_email(request,token,email, "change_password")
            messages.success(request, "Email Sent Successfully!!!")
    return render(request, 'base/send_email.html')

# view for changing forgotten password

def Change_password(request,token):
    if request.method == 'POST':
        form = ChangePasswordCustomForm(request.POST)
        if form.is_valid():
            print("hello")
            user_obj=ForgotPassword.objects.filter(forgot_password_token=token).first()
            if user_obj: 
                password=form.cleaned_data.get("new_password2")
                user_obj.user.set_password(password)
                user_obj.user.save()
                print(user_obj.user,password)
                messages.success(request, 'Your password was successfully updated!')
                user_obj.delete()
                return render(request, 'base/success.html')
            else:
                return render(request, 'base/error.html')
        else:
            print(form.errors)
            return render(request, 'base/error.html')
    else:
        user_obj=ForgotPassword.objects.filter(forgot_password_token=token).first()
        if user_obj:
            form = ChangePasswordCustomForm()
        else:
            return render(request, 'base/error.html')
    return render(request, 'base/reset_password.html', {
        'form': form
    })
