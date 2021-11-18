from django.urls import path

from . import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', views.userLogin, name='login'),
    path('counselor/', views.counselor, name='counselor'),
    path('counseling/<int:user_id>/', views.counseling, name='counseling'),
    path('user_info/', views.user_info, name='user_info'),
    path('outbound/', views.outbound, name='outbound'),
    path('system/', views.system, name='system'),
    path('data/', views.data, name='data'),
    path('register/', views.register, name='register'),
    path('phonecall/', views.phonecall, name="phonecall"),
    path('chat/', views.chat, name='chat'),
]