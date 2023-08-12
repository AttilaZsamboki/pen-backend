from django.urls import path
from . import views

urlpatterns = [
    path('pen_minicrm_webhook/', views.PenCalculateDistance.as_view()),
    path('pen_googlesheet_webhook/', views.PenGoogleSheetWebhook.as_view()),
    path('cron/szamlazz/', views.CronSzamlazz.as_view()),
]