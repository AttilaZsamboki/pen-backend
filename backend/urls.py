from django.urls import path
from . import views

urlpatterns = [
    path('minicrm_webhook/', views.CalculateDistance.as_view()),
    path('googlesheet_webhook/', views.GoogleSheetWebhook.as_view()),
    path('felmeres_questions', views.FelmeresQuestionsList.as_view()),
    path('felmeres_questions/<pk>/', views.FelmeresQuestionDetail.as_view()),
    path('felmeresek_notes', views.FelmeresekNotesList.as_view()),
    path('felmeresek_notes/<int:pk>/', views.FelmeresekNotesDetail.as_view()),
    path('order_webhook/', views.OrderWebhook.as_view()),
    path('products', views.ProductsList.as_view()),
    path('products/<int:pk>/', views.ProductsDetail.as_view()),
    path('product_attributes', views.ProductAttributesList.as_view()),
    path('product_attributes/<int:pk>/', views.ProductAttributesDetail.as_view()),
    path('filters', views.FiltersList.as_view()),
    path('filters/<int:pk>/', views.FiltersDetail.as_view()),
    path('questions/', views.QuestionsList.as_view()),
    path('questions/<int:pk>/', views.QuestionsDetail.as_view()),
    path('templates/', views.TemplateSerializerList.as_view()),
    path('templates/<int:pk>/', views.TemplateSerializerDetail.as_view()),
    path('product_templates/', views.ProductTemplateSerializerList.as_view()),
    path('product_templates/<int:pk>/', views.ProductTemplateSerializerDetail.as_view()),
    path('felmeresek/', views.FelmeresekList.as_view()),
    path('felmeresek/<int:pk>/', views.FelmeresekDetail.as_view()),
    path('felmeres_items/', views.FelmeresItemsList.as_view()),
    path('felmeres_items/<int:pk>/', views.FelmeresItemsDetail.as_view()),
]