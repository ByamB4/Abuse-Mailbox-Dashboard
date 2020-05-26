from django.urls import path
from .views import MailListView, MailChartView

urlpatterns = [
    path('', MailListView.as_view()),
    path('chart/', MailChartView.as_view())
]