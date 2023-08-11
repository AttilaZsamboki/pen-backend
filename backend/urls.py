from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('pen_minicrm_webhook/', views.PenCalculateDistance.as_view()),
    path('pen_googlesheet_webhook/', views.PenGoogleSheetWebhook.as_view()),
]