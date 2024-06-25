from django.urls import path

from api.views.catalogs import CatalogsView


urlpatterns = [
    path('catalogs/', CatalogsView.as_view()),
]
