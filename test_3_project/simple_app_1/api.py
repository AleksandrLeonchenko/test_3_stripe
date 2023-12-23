import os
import stripe
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from typing import Any, Dict

from .models import Item, Order, OrderItem
from .serializers import OrderCreateSerializer
from .service import PaymentSessionCreator


class ItemPaymentView(APIView):
    """
    Представление для GET-запроса для создания платежной сессии.

    """
    def get(self, request, pk: int) -> Response:
        """
        Обрабатывает GET-запрос для создания платежной сессии.

        Parameters:
            - request: Объект, представляющий входящий HTTP-запрос.
            - pk (int): Первичный ключ товара для создания платежной сессии.

        Returns:
            - Response: Объект HTTP-ответа, содержащий session_id для платежной сессии.
        """
        item = get_object_or_404(Item, pk=pk)
        session_creator = PaymentSessionCreator()
        payment_data = {
            'payment_method_types': ['card'],
            'line_items': [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.name,
                            'description': item.description,
                        },
                        'unit_amount': int(item.price * 100),
                    },
                    'quantity': 1,
                }
            ],
            'mode': 'payment',
            'success_url': 'https://xxx.com/success',
            'cancel_url': 'https://yyy.com/cancel',
        }
        session_id = session_creator.create_session(payment_data)
        return Response({'session_id': session_id})


class ItemView(TemplateView):
    """
    Представление для отображения информации о товаре.

    Attributes:
        - template_name: str, имя шаблона для отображения

    """
    template_name = "simple_app_1/item.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Получение контекста данных для отображения информации о товаре.

        Parameters:
            - kwargs: Any, дополнительные аргументы

        Returns:
            - Dict[str, Any]: Словарь с контекстом данных для использования в шаблоне
        """
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['stripe_public_key'] = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        context['item'] = Item.objects.get(id=pk)
        return context


class OrderCreateView(APIView):
    """
    Представление для POST-запроса для создания заказа.

    """
    def post(self, request) -> Response:
        """
        Обрабатывает POST-запрос для создания заказа.

        Parameters:
            - request: Объект, представляющий входящий HTTP-запрос.

        Returns:
            - Response: Объект HTTP-ответа, содержащий информацию о созданном заказе или ошибки валидации.
        """
        serializer = OrderCreateSerializer(data=request.data)

        if serializer.is_valid():
            order_items_data = serializer.validated_data['items']

            order = Order.objects.create()
            for item_data in order_items_data:
                item = Item.objects.get(id=item_data['item_id'])
                quantity = item_data['quantity']
                order_item = OrderItem.objects.create(order=order, item=item,
                                                      quantity=quantity)  # Создание заказанного товара и добавление к заказу
                order.items.add(item)  # Добавление товара к заказу

            print('----order.id----', order.id)
            print('---total_price-----', order.total_price)

            return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderPaymentView(APIView):
    """
    Представление для GET-запроса для оплаты заказа.

    """
    def get(self, request, order_id: int) -> Response:
        """
        Обрабатывает GET-запрос для оплаты заказа.

        Parameters:
            - request: Объект, представляющий входящий HTTP-запрос.
            - order_id (int): Идентификатор заказа для оплаты.

        Returns:
            - Response: Объект HTTP-ответа, содержащий session_id для платежной сессии.
        """
        order = get_object_or_404(Order, pk=order_id)
        session_creator = PaymentSessionCreator()
        payment_data = {
            'payment_method_types': ['card'],
            'line_items': [
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Order payment',
                        },
                        'unit_amount': int(order.total_price * 100),
                    },
                    'quantity': 1,
                }
            ],
            'mode': 'payment',
            'success_url': 'https://zzz.com/success',
            'cancel_url': 'https://sss.com/cancel',
        }
        session_id = session_creator.create_session(payment_data)
        return Response({'session_id': session_id})


class OrderView(TemplateView):
    """
    Представление для отображения информации о заказе.

    Attributes:
        - template_name (str): Имя шаблона, используемого для отображения информации о заказе.
    """
    template_name = "simple_app_1/order.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Обрабатывает GET-запрос для оплаты заказа.

        Parameters:
            - request: Объект, представляющий входящий HTTP-запрос.
            - order_id (int): Идентификатор заказа для оплаты.

        Returns:
            - Response: Объект HTTP-ответа, содержащий session_id для платежной сессии.
        """
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        context['stripe_public_key'] = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        context['order'] = Order.objects.get(id=order_id)
        return context
