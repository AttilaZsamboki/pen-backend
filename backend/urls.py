from django.urls import path
from . import views

urlpatterns = [
    path('minicrm_webhook/', views.CalculateDistance.as_view()),
    path('googlesheet_webhook/', views.GoogleSheetWebhook.as_view()),
    path('felmeresek', views.FelmeresekList.as_view()),
    path('felmeresek/<id>/', views.FelmeresekDetail.as_view()),
    path('felmeresek_notes', views.FelmeresekNotesList.as_view()),
    path('felmeresek_notes/<id>/', views.FelmeresekNotesDetail.as_view()),
]