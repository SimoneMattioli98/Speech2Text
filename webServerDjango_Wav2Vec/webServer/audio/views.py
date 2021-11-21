from django.shortcuts import redirect, render
from .forms import AudioForm, TokenForm
import uuid
from .models import Request
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.files.base import File
import io

from  django.core.files import base

# Create your views here.

def get_request_from_id(id):
    return Request.objects.get(id_request = id)

def home_view(request):
    return render(request, "home.html")

def create_request(request):

    pending_request_id = None
    form = AudioForm() 

    if request.COOKIES.get('pending_request_id') != None:
        pending_request_id = request.COOKIES['pending_request_id']

    if request.method == 'POST': 
        
        form = AudioForm(request.POST,request.FILES or None) 
        if form.is_valid(): 
            pending_request_id = form.save(commit=False)
            pending_request_id.id_request = str(uuid.uuid4())
            pending_request_id.save()

        
    context = {
        'form': form,
        'pending_request_id': pending_request_id
    }

    response = render(request, 'audio.html', context)

    if pending_request_id != None:
        response.set_cookie('pending_request_id', pending_request_id)

    return response


def get_request_status(request, id_request):

    content = None

    if request.method == 'GET':
        try:
            single_request = get_request_from_id(id_request)
            content = single_request
        except Request.DoesNotExist:
            messages.error(request,'The request id you entered does not exist, please try again')

    
    context = {
        'content': content
    }

    return render(request, 'result.html', context)


def token(request):
    token = None
    form = TokenForm()

    if request.COOKIES.get('pending_request_id') != None:
        token = request.COOKIES['pending_request_id']

    if request.method == "POST":
        form = TokenForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data["token"]

            response = redirect(f"results/{token}")
            response.delete_cookie('token')
            return response


    if token != None:
        form = TokenForm(initial={'token': token})

    context = {
        'form': form,
        'token': token
    }


    return render(request, 'token.html', context)


def recorder(request):
    pending_request_id = None

    if request.COOKIES.get('pending_request_id') != None:
        pending_request_id = request.COOKIES['pending_request_id']

    if request.method == "POST":
        audio_data = request.FILES.get('audio_data')
        model_choosen = request.POST.get('model_choosen')
        
        pending_request_id = Request()
        pending_request_id.id_request = str(uuid.uuid4())
        pending_request_id.record = audio_data
        pending_request_id.model_choosen = model_choosen
        pending_request_id.save()

    context = {
        'pending_request_id': pending_request_id
    }

    response = render(request, 'recorder.html', context)

    if pending_request_id != None:
        response.set_cookie('pending_request_id', pending_request_id)

    return response