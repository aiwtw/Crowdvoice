from django.urls import path
from voice_share import views

app_name = 'voice_share'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('<int:pk>/', views.ArticleDetail.as_view(), name='article-detail'),
    path('new_share/', views.VoiceShare.as_view(), name='share'),
]
