from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.index,name='home'),
    path('news_search/', views.news_search, name='news_search'),
    path('login/', views.login_menu, name='login'),
    path('logoutUser/', views.logoutUser, name='logoutUser'),
    path('register/', views.register, name='register'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('sentiment-analysis/', views.sentiment_analysis_view, name='sentiment_analysis'),
    path('review_page/', views.review_page, name='review_page'),
]
