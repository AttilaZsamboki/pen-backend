from django.urls import path
from . import views

urlpatterns = [
    path('minicrm_webhook/', views.CalculateDistance.as_view()),
    path('googlesheet_webhook/', views.GoogleSheetWebhook.as_view()),
    path('felmeresek', views.FelmeresekList.as_view()),
    path('felmeresek/<int:pk>', views.FelmeresekDetail.as_view()),
]