from django.urls import path
from .views import create_request, get_request_status, token, recorder, home_view


urlpatterns = [
    path('', home_view, name="home"),
    path('uploader', create_request, name='create_request'),
    path('results/<str:id_request>/', get_request_status, name='result'),
    path('token', token, name='token'),
    path('recorder', recorder,  name='recorder')
]