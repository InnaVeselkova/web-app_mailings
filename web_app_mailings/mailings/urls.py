from django.urls import path

from .views import HomeListView

app_name = 'mailings'

urlpatterns = [

    path('mailing/', HomeListView.as_view(), name='home'),

]