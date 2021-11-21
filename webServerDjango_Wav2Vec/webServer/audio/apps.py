from django.apps import AppConfig
import sys
from manage import config


class AudioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audio'

    # function called once the django server has been loaded
    # def ready(self) -> None:

    #     if 'runserver' in sys.argv:    
    #         from threads.polling_thread import PollingThread
    #         from transcriptions.wav2vec2 import Wav2Vec2
            
    #         wav2vec2_short = Wav2Vec2(config.jonatas, config.jonatas)
    #         wav2vec2_long = Wav2Vec2(config.finetuned, config.jonatas)
    #         th = PollingThread(wav2vec2_long, wav2vec2_short)
    #         th.start()