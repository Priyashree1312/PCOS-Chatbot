from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),           # /chat/ → HTML page
    path('chat/', views.chat_api, name='chat_api'),   # /chat/chat/ → API  
    path('health/', views.health_check, name='health_check'),
    path('test-rag/', views.test_rag, name='test_rag'),
]
