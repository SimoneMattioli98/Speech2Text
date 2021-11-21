from audio.models import Request
import torchaudio
from webServer.settings import MEDIA_ROOT
import os
import torch
from django.utils import timezone
import moviepy.editor as mp
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

#atomic function for trascription
#get the request and trascribe the audio. If there are no errors the record is deleted,
#the result is registered. Otherwise the error is written on the result field
def transcribe(request, wav2vec2):

    try:   

        if request.record_type == 'Video':
            extract_audio(request)
        
        transcribe_audio(request, wav2vec2)

    except Exception as e:
        request.status = 'Failed'
        request.result = str(e)
        request.save()
        

def extract_audio(request):
    path = os.path.join(MEDIA_ROOT, str(request.record))
    video = mp.VideoFileClip(path)
    path_to_audio = f"{os.path.splitext(path)[0]}.mp3"
    video.audio.write_audiofile(path_to_audio)
    request.record_type = 'Audio'
    request.record = f"{os.path.splitext(str(request.record))[0]}.mp3"
    request.save()
    os.remove(path)


    

def transcribe_audio(request, wav2vec2):
    path_to_file = os.path.join(MEDIA_ROOT, str(request.record))
    info = torchaudio.info(path_to_file)
    resampler = torchaudio.transforms.Resample(orig_freq=info.sample_rate, new_freq=16_000)
    speech, _ = torchaudio.load(path_to_file)    

    # stereo (2, n) to mono (1,n) conversion
    if speech.shape[0] == 2:
        speech = torch.mean(speech, dim=0).unsqueeze(0)

    speech = resampler.forward(speech.squeeze(0)).numpy()
    features = wav2vec2.processor(speech, sampling_rate=resampler.new_freq, padding=True, return_tensors="pt")
    input_values = features.input_values
    attention_mask = features.attention_mask
    
    with torch.no_grad():
        logits = wav2vec2.model(input_values, attention_mask=attention_mask).logits

    pred_ids = torch.argmax(logits, dim=-1)
    prediction = wav2vec2.processor.batch_decode(pred_ids)
    request.result = prediction 
    request.end_date = timezone.now()
    request.status = 'Completed'
    # os.remove(path_to_file)
    request.save()
