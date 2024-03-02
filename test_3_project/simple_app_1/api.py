from typing import Any, Dict
from django.http import JsonResponse, HttpResponse, Http404
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

import stripe
import logging
from .models import Item, Order, OrderItem
from .serializers import OrderCreateSerializer
from .service import PaymentSessionCreator, OrderCreationService, ItemPaymentDataService, OrderPaymentDataService
from test_3_project.settings import (
    STRIPE_PUBLISHABLE_KEY, STRIPE_PUBLIC_KEY_CURRENCY_1, STRIPE_PUBLIC_KEY_CURRENCY_2, STRIPE_SECRET_KEY
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class ItemPaymentView(APIView):
    """
    Представление для обработки GET-запроса и создания платежной сессии.

    Attributes:
        - None

    Methods:
        - get(request, pk: int) -> Response: Обрабатывает GET-запрос для создания платежной сессии.

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

        try:
            currency = item.get_currency_display()
            payment_data, stripe_secret_key = ItemPaymentDataService.generate_payment_data(request, item, currency)
            session_id = PaymentSessionCreator.create_session(stripe_secret_key, payment_data)
        except Exception as e:
            logger.error(f"ItemPaymentView - An error occurred: {str(e)}")
            return Response({'error': str(e)}, status=500)

        return Response({'session_id': session_id})


class SuccessView(TemplateView):
    """
    Страница успеха.

    Attributes:
        - template_name (str): Имя шаблона, используемого для отображения страницы успеха.

    Methods:
        - get_context_data(**kwargs: Any) -> Dict[str, Any]: Получение контекста данных для отображения страницы успеха.

    """
    template_name = "simple_app_1/success.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Получение контекста данных для отображения страницы успеха.

        Parameters:
            - kwargs: Дополнительные аргументы.

        Returns:
            - Dict[str, Any]: Словарь с контекстом данных для использования в шаблоне.

        """
        context = super().get_context_data(**kwargs)
        return context


class CancelView(TemplateView):
    """
    Страница отмены.

    Attributes:
        - template_name (str): Имя шаблона, используемого для отображения страницы неудачи.

    Methods:
        - get_context_data(**kwargs: Any) -> Dict[str, Any]: Получение контекста данных для отображения страницы неудачи.

    """
    template_name = "simple_app_1/cancel.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Получение контекста данных для отображения страницы отмены.

        Parameters:
            - kwargs: Дополнительные аргументы.

        Returns:
            - Dict[str, Any]: Словарь с контекстом данных для использования в шаблоне.

        """
        context = super().get_context_data(**kwargs)
        return context


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
        item = Item.objects.get(id=pk)
        currency = item.get_currency_display()

        if currency == 'usd':
            stripe_public_key = STRIPE_PUBLIC_KEY_CURRENCY_1
        else:
            stripe_public_key = STRIPE_PUBLIC_KEY_CURRENCY_2

        context['stripe_public_key'] = stripe_public_key
        context['item'] = Item.objects.get(id=pk)
        return context


class OrderCreateView(APIView):
    """
    Класс API-представления для создания заказа.

    Принимает POST-запрос с данными в формате:
    {
      "items": [
        {"item_id": 1, "quantity": 2},
        {"item_id": 3, "quantity": 1},
        {"item_id": 5, "item": 3}
      ]
    }

    Возвращает JSON с информацией о созданном заказе или ошибкой валидации.
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
            order_id = OrderCreationService.create_order(order_items_data)
            return Response({'order_id': order_id}, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"OrderCreateView - Validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderPaymentView(APIView):
    """
    Класс API-представления для обработки GET-запроса оплаты заказа.

    Attributes:
        - None

    Methods:
        - get(request, order_id: int) -> Response: Обрабатывает GET-запрос для создания платежной сессии заказа.

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

        try:
            payment_data = OrderPaymentDataService.generate_payment_data(request, order)
            session_id = PaymentSessionCreator.create_session(STRIPE_SECRET_KEY, payment_data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

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
        context['stripe_public_key'] = STRIPE_PUBLISHABLE_KEY
        context['order'] = Order.objects.get(id=order_id)
        return context
