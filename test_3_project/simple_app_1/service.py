import stripe
import os


class PaymentSessionCreator:
    def create_session(self, stripe_secret_key: str, payment_data: dict) -> str:
        """
        Создает сессию оплаты через Stripe Checkout.

        Parameters:
            - payment_data (dict): Словарь с данными для создания сессии оплаты.
            - stripe_secret_key (str): Секретный ключ stripe

        Returns:
            str: ID созданной сессии оплаты.
        """
        stripe.api_key = stripe_secret_key
        # stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        session = stripe.checkout.Session.create(**payment_data)
        return session.id
