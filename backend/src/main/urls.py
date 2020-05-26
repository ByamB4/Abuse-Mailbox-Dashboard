from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('action/full', views.ActionView.as_view(), name='action-full')
]