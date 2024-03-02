from typing import List, Dict
import stripe
import os
import logging

from django.http import HttpRequest
from django.urls import reverse
from test_3_project.settings import STRIPE_SECRET_KEY_CURRENCY_1, STRIPE_SECRET_KEY_CURRENCY_2
from .models import Order, OrderItem, Item

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class ItemPaymentDataService:
    """
    Сервис генерации данных для оплаты товара.

    Methods:
        - generate_payment_data(request: HttpRequest, item: Item, currency: str) -> Tuple[Dict, str]:
            Генерирует данные для платежа на основе информации о товаре.

    """
    @classmethod
    def generate_payment_data(cls, request: HttpRequest, item: Item, currency: str) -> Dict:
        """
        Генерирует данные для платежа на основе информации о товаре.

        Parameters:
            - request (HttpRequest): Объект, представляющий входящий HTTP-запрос.
            - item (Item): Объект товара.
            - currency (str): Валюта.

        Returns:
            Tuple[Dict, str]: Словарь с данными для платежа и секретный ключ Stripe.

        """
        try:
            if currency == 'usd':
                stripe_secret_key = STRIPE_SECRET_KEY_CURRENCY_1
            else:
                stripe_secret_key = STRIPE_SECRET_KEY_CURRENCY_2

            payment_data = {
                'payment_method_types': ['card'],
                'line_items': [
                    {
                        'price_data': {
                            'currency': currency,
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
                'success_url': request.build_absolute_uri(reverse('success')),
                'cancel_url': request.build_absolute_uri(reverse('cancel')),
            }

            return payment_data, stripe_secret_key
        except Exception as e:
            logger.error(f"An error occurred in ItemPaymentDataService: {str(e)}")
            raise


class OrderPaymentDataService:
    """
    Сервис генерации данных для оплаты заказа.

    Methods:
        - generate_payment_data(request: HttpRequest, order: Order) -> Dict:
            Генерирует данные для платежа на основе информации о заказе.

    """
    @classmethod
    def generate_payment_data(cls, request, order):
        """
        Генерирует данные для платежа на основе информации о заказе.

        Parameters:
            - request (HttpRequest): Объект, представляющий входящий HTTP-запрос.
            - order (Order): Объект заказа.

        Returns:
            Dict: Словарь с данными для платежа.

        """
        try:
            line_items = []

            for item in order.order_item.all():
                description = f"{item.item.description}."

                if (order.tax and order.tax.rate) or (order.discount and order.discount.amount):
                    description += f" Начальная цена: {item.item.get_formatted_price()}."

                unit_amount = int(item.item.price)

                if order.tax and order.tax.rate:
                    unit_amount -= unit_amount * int(order.tax.rate) / 100
                    description += f" Добавлен налог {order.tax.rate}%."

                if order.discount and order.discount.amount:
                    unit_amount -= unit_amount * int(order.discount.amount) / 100
                    description += f" Добавлена скидка {order.discount.amount}%."

                unit_amount *= 100
                unit_amount = round(unit_amount)

                line_items.append(
                    {
                        'price_data': {
                            'currency': item.item.get_currency_display(),
                            'product_data': {
                                'name': item.item.name,
                                'description': description,
                            },
                            'unit_amount': unit_amount,
                        },
                        'quantity': item.quantity,
                    }
                )

            payment_data = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'success_url': request.build_absolute_uri(reverse('success')),
                'cancel_url': request.build_absolute_uri(reverse('cancel')),
            }

            return payment_data
        except Exception as e:
            logger.error(f"An error occurred in OrderPaymentDataService: {str(e)}")
            raise


class PaymentSessionCreator:
    """
    Сервис создания сессии оплаты через Stripe Checkout.

    Methods:
        - create_session(stripe_secret_key: str, payment_data: dict) -> str:
            Создает сессию оплаты.

    """
    @classmethod
    def create_session(cls, stripe_secret_key: str, payment_data: dict) -> str:
        """
        Создает сессию оплаты через Stripe Checkout.

        Parameters:
            - stripe_secret_key (str): Секретный ключ Stripe.
            - payment_data (dict): Словарь с данными для создания сессии оплаты.

        Returns:
            str: ID созданной сессии оплаты.

        """
        try:
            stripe.api_key = stripe_secret_key
            session = stripe.checkout.Session.create(**payment_data)
            return session.id
        except Exception as e:
            logger.error(f"An error occurred in PaymentSessionCreator: {str(e)}")
            raise


class OrderCreationService:
    """
    Сервис для создания заказов.

    Methods:
        - create_order(order_items_data: List[dict]) -> int:
            Создает заказ на основе предоставленных данных.

    """

    @staticmethod
    def create_order(order_items_data: List[dict]) -> int:
        """
        Создает заказ на основе предоставленных данных.

        Parameters:
            - order_items_data (List[dict]): Список словарей с данными о товарах в заказе.

        Returns:
            - int: Идентификатор созданного заказа.

        """
        try:
            order = Order.objects.create()

            for item_data in order_items_data:
                item = Item.objects.get(id=item_data['item_id'])
                quantity = item_data['quantity']

                order_item = OrderItem.objects.create(order=order, item=item, quantity=quantity)

            return order.id
        except Exception as e:
            logger.error(f"An error occurred in OrderCreationService: {str(e)}")
            raise


