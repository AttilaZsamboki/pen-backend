from django.urls import path
from . import views

urlpatterns = [
    path('minicrm_webhook/', views.CalculateDistance.as_view()),
    path('googlesheet_webhook/', views.GoogleSheetWebhook.as_view()),
    path('felmeresek', views.FelmeresekList.as_view()),
    path('felmeresek/<pk>/', views.FelmeresekDetail.as_view()),
    path('felmeresek_notes', views.FelmeresekNotesList.as_view()),
    path('felmeresek_notes/<int:pk>/', views.FelmeresekNotesDetail.as_view()),
    path('order_webhook/', views.OrderWebhook.as_view()),
    path('products', views.ProductsList.as_view()),
    path('products/<int:pk>/', views.ProductsDetail.as_view()),
]