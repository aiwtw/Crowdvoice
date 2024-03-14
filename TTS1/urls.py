"""TTS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.contrib import admin
from rest_framework import routers
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from voice import views
from rest_framework_jwt.views import obtain_jwt_token
from comment.views import CommentViewSet, IncreaseVoiceSharedLikeView, IncreaseCommentLikeView
from django.conf.urls.static import static
from TTS1 import settings


router = routers.DefaultRouter()
router.register('user', views.UserViewSet)
router.register(r'comment', CommentViewSet)

urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path("voice/", views.VoiceGenerateView.as_view()),
    path('login/',obtain_jwt_token),
    path('wx/',views.Login.as_view()),
    path('personalvoice/',views.PersonalVoiceView.as_view()),
    path('pubvoice/',views.PubVoiceView.as_view()),
    path("usersound/", views.Usersound.as_view({"get": "get", "post": "upload","delete": "delete_data","put": "user_description"})),
    path('voice_share/', include('voice_share.urls', namespace='voice_share')),
    path('like/comment/<int:pk>/', IncreaseCommentLikeView.as_view()),
    path('like/voice_share/<int:pk>/', IncreaseVoiceSharedLikeView.as_view()),
]
urlpatterns += router.urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)