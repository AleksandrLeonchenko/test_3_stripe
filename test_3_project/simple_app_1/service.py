import stripe
import os


class PaymentSessionCreator:
    def create_session(self, payment_data: dict) -> str:
        """
        Создает сессию оплаты через Stripe Checkout.

        Parameters:
            payment_data (dict): Словарь с данными для создания сессии оплаты.

        Returns:
            str: ID созданной сессии оплаты.
        """
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        session = stripe.checkout.Session.create(**payment_data)
        return session.id
