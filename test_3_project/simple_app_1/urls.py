from django.urls import path
from .api import ItemView, ItemPaymentView, OrderPaymentView, OrderView, OrderCreateView, SuccessView, CancelView

urlpatterns = [
    path('buy/<int:pk>', ItemPaymentView.as_view(), name='buy'),
    path('item/<int:pk>', ItemView.as_view(), name='item'),
    path('success', SuccessView.as_view(), name='success'),
    path('cancel', CancelView.as_view(), name='cancel'),

    path('order/create', OrderCreateView.as_view(), name='order_create'),
    path('buy_all/<int:order_id>', OrderPaymentView.as_view(), name='buy_all'),
    path('order/<int:order_id>', OrderView.as_view(), name='order'),

]
