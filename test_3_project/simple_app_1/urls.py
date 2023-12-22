from django.urls import path
from .api import SessionIdView, ItemView

urlpatterns = [
    path('buy/<int:pk>', SessionIdView.as_view(), name='buy'),
    path('item/<int:pk>', ItemView.as_view(), name='item'),
]
