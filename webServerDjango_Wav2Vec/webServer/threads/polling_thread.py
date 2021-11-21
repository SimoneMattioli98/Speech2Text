from threading import Thread
import time
from audio.models import Request
from django.db.models import Q
from transcriptions.transcription import transcribe
import sys

class PollingThread(Thread):

    def __init__(self, wav2vec2_long, wav2vec2_short):
        Thread.__init__(self)
        self.wav2vec2_long = wav2vec2_long
        self.wav2vec2_short = wav2vec2_short

        print("Initializing polling thread!")


    def run(self) -> None:
        print("Running polling thread!")
        while(True):
            #start = time.perf_counter()

            time.sleep(1)

            request_choosen = Request.objects.order_by('start_date')\
                                             .filter(Q(status='Pending'))\
                                             .first()
            if request_choosen is not None:
                request_choosen.status = 'Transcribing'
                request_choosen.save()
                if request_choosen.model_choosen == "Jonatas-Short":
                    transcribe(request_choosen, self.wav2vec2_short)
                else:
                    transcribe(request_choosen, self.wav2vec2_long)
            #finish = time.perf_counter()
