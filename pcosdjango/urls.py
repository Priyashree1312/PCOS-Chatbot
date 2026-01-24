from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('/chat/', permanent=False)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chatbot.urls')),  # ← CRITICAL LINE
    path('', home_redirect, name='home'),
]
