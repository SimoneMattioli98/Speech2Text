from django.db import models
from django.utils import timezone
import uuid, os

# Create your models here.


def get_file_path(instance, filename):
    basefilename, file_extension= os.path.splitext(filename)
    return f'{basefilename}{str(uuid.uuid4())}{file_extension}'

# request model 
class Request(models.Model):

    STATUS = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Transcribing', 'Transcribing'),
        ('Failed', 'Failed')
    )

    RECORD_TYPE = (
        ('Video', 'Video'),
        ('Audio', 'Audio')
    )

    MODELS_AVAILLABLE = (
        ('Jonatas-Short', 'Jonatas-Short'),
        ('Finetuned on MLLS-Long','Finetuned on MLLS-Long')
    )

    id_request = models.CharField(primary_key=True, max_length=100)
    record = models.FileField(upload_to=get_file_path, null=True)
    model_choosen = models.CharField(
        max_length=100,
        choices=MODELS_AVAILLABLE,
        default='Jonatas-Short')
    record_type = models.CharField(
        max_length=100,
        choices=RECORD_TYPE,
        default='Audio'
    ) 
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=32,
        choices=STATUS,
        default='Pending'
    ) 
    result = models.TextField()

    def __str__(self):
        return self.id_request

