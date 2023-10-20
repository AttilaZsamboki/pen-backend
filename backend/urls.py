from django.urls import path
from . import views

urlpatterns = [
    path("minicrm_webhook/", views.CalculateDistance.as_view()),
    path("felmeres_questions/", views.FelmeresQuestionsList.as_view()),
    path("felmeres_questions/<pk>/", views.FelmeresQuestionDetail.as_view()),
    path("order_webhook/", views.OrderWebhook.as_view()),
    path("products", views.ProductsList.as_view()),
    path("products/<int:pk>/", views.ProductsDetail.as_view()),
    path("product_attributes", views.ProductAttributesList.as_view()),
    path("product_attributes/<int:pk>/", views.ProductAttributesDetail.as_view()),
    path("filters", views.FiltersList.as_view()),
    path("filters/<int:pk>/", views.FiltersDetail.as_view()),
    path("questions/", views.QuestionsList.as_view()),
    path("questions/<int:pk>/", views.QuestionsDetail.as_view()),
    path("templates/", views.TemplateList.as_view()),
    path("templates/<int:pk>/", views.TemplateDetail.as_view()),
    path("product_templates/", views.ProductTemplatesList.as_view()),
    path("product_templates/<int:pk>/", views.ProductTemplateDetail.as_view()),
    path("felmeresek/", views.FelmeresekList.as_view()),
    path("felmeresek/<int:pk>/", views.FelmeresekDetail.as_view()),
    path("felmeres_items/", views.FelmeresItemsList.as_view()),
    path("felmeres_items/<int:pk>/", views.FelmeresItemsDetail.as_view()),
    path("offer_webhook/", views.OfferWebhook.as_view()),
    path("question_products/", views.QuestionProductsList.as_view()),
    path("question_products/<int:pk>/", views.QuestionProductsDetail.as_view()),
    path("erp_sync/login", views.UnasLogin.as_view(), name="unas_login"),
    path("erp_sync/getOrder", views.UnasGetOrder.as_view()),
    path("erp_sync/setProduct", views.UnasSetProduct.as_view()),
    path("filter_items/", views.FilterItemsList.as_view()),
    path("filter_items/<int:pk>/", views.FilterItemsDetail.as_view()),
    path("cancel_offer/", views.CancelOffer.as_view()),
    path("save-image/", views.upload_file),
    path("felmeres-pictures/", views.FelmeresPicturesList.as_view()),
    path("felmeres-pictures/<int:pk>/", views.FelmeresPicturesDetail.as_view()),
    path("felmeres-notes/", views.FelmeresNotesList.as_view()),
    path("felmeres-notes/<int:pk>/", views.FelmeresNotesDetail.as_view()),
]
