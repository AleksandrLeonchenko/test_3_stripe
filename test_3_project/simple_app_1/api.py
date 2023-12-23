import os
import stripe
from django.views.generic import TemplateView
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from typing import Any, Dict

from .models import Item


class SessionIdView(APIView):
    """
    Класс SessionIdView представляет API-представление для получения идентификатора сессии оплаты.

    Атрибуты:
        - request: HttpRequest, объект запроса
        - pk: int, идентификатор товара

    Методы:
        - get(self, request, pk): Метод для обработки запроса типа GET.
                                 Получает идентификатор товара, создает сессию оплаты через Stripe Checkout,
                                 и возвращает идентификатор сессии в формате JSON.
    """

    def get(self, request, pk: int) -> Response:
        """
        Обрабатывает GET-запрос для получения идентификатора сессии оплаты.

        Аргументы:
            - request: HttpRequest, объект запроса
            - pk: int, идентификатор товара

        Возвращает:
            - Response: Объект ответа с идентификатором сессии в формате JSON
        """
        item = get_object_or_404(Item, pk=pk)
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        session = stripe.checkout.Session.create(
            # Создание объекта Session для оформления платежа через Stripe Checkout
            payment_method_types=['card'],  # Указание типа платежного метода (в данном случае, карта)
            line_items=[{  # Описание товара или услуги, которую покупатель собирается оплатить
                'price_data': {  # Описание цены и продукта
                    'currency': 'usd',  # Установка валюты (USD)
                    'product_data': {  # Описание товара
                        'name': item.name,
                        'description': item.description,
                    },
                    'unit_amount': int(item.price * 100),  # Установка суммы в центах, умноженной на цену товара
                },
                'quantity': 1,  # Установка количества товара (в данном случае, 1 шт.)
            }],
            mode='payment',  # Установка режима (в данном случае, оплата)
            success_url='https://xxx.com/success',  # URL, куда покупатель попадет после успешной оплаты
            cancel_url='https://yyy.com/cancel',  # URL, куда покупатель попадет после отмены оплаты
        )

        return Response({'session_id': session.id})


class ItemView(TemplateView):
    """
    Класс ItemView представляет представление для отображения информации о товаре.

    Атрибуты:
        - template_name: str, имя шаблона для отображения

    Методы:
        - get_context_data(self, **kwargs: Any) -> Dict[str, Any]: Метод для получения контекста данных
    """
    template_name = "simple_app_1/item.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Получение контекста данных для отображения информации о товаре.

        Аргументы:
            - kwargs: Any, дополнительные аргументы

        Возвращает:
            - Dict[str, Any]: Словарь с контекстом данных для использования в шаблоне
        """
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['stripe_public_key'] = os.environ.get('STRIPE_PUBLISHABLE_KEY')
        context['item'] = Item.objects.get(id=pk)
        return context
