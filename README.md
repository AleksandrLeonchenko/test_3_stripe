# Задача
Реализовать Django + Stripe API бэкенд со следующим функционалом и условиями:


- Django Модель Item с полями (name, description, price)
- API с двумя методами:
- GET /buy/{id}, c помощью которого можно получить Stripe Session Id для оплаты выбранного Item. При выполнении этого метода c бэкенда с помощью python библиотеки stripe должен выполняться запрос stripe.checkout.Session.create(...) и полученный session.id выдаваться в результате запроса
- GET /item/{id}, c помощью которого можно получить простейшую HTML страницу, на которой будет информация о выбранном Item и кнопка Buy. По нажатию на кнопку Buy должен происходить запрос на /buy/{id}, получение session_id и далее с помощью JS библиотеки Stripe происходить редирект на Checkout форму stripe.redirectToCheckout(sessionId=session_id)
- Запуск используя Docker
- Использование environment variables
- Просмотр Django Моделей в Django Admin панели
- Запуск приложения на удаленном сервере, доступном для тестирования
- Модель Order, в которой можно объединить несколько Item и сделать платёж в Stripe на содержимое Order c общей стоимостью всех Items
- Модели Discount, Tax, которые можно прикрепить к модели Order и связать с соответствующими атрибутами при создании платежа в Stripe - в таком случае они корректно отображаются в Stripe Checkout форме.
- Добавить поле Item.currency, создать 2 Stripe Keypair на две разные валюты и в зависимости от валюты выбранного товара предлагать оплату в соответствующей валюте
- Реализовать не Stripe Session, а Stripe Payment Intent.


## Технологии
- Django 5.0
- PostgreSQL 15
- Django Rest Framework 3.14.0
- Stripe

## Установка и настройка

### Предварительные требования
- Python 3.11
- pip
- virtualenv
- Django 5.0
- PostgreSQL 15
- Django Rest Framework 3.14.0


### Для развёртывания и запуска проекта на локальном сервере выполните следующие шаги:

1. Зарегистрируйтесь на stripe.com и получите пару (публичный и секретный) ключи.

2. Создайте вторую пару ключей (для выполнения дополнительного задания)

3. Клонируйте репозиторий:
```bash
git clone [https://github.com/AleksandrLeonchenko/test_3_stripe.git]
```
4. Создайте и активируйте виртуальное окружение:
```bash
virtualenv venv
source venv/bin/activate  # на Linux/macOS
.\venv\Scripts\activate   # на Windows
```
5. Установите зависимости:
```bash
pip install -r requirements.txt
```
6. Заполните файл .env по образцу .env_template.
STRIPE_PUBLISHABLE_KEY (он же STRIPE_PUBLIC_KEY_CURRENCY_1) - первый публичный ключ 
STRIPE_SECRET_KEY (он же STRIPE_SECRET_KEY_CURRENCY_1) - первый секретный ключ
STRIPE_PUBLIC_KEY_CURRENCY_2 - второй публичный ключ 
STRIPE_SECRET_KEY_CURRENCY_2 - второй секретный ключ

7. Настройте базу данных в settings.py и выполните миграции:
```bash
python manage.py migrate
```
8. Загрузите файлы фикстур в базу данных (Admin - пароль - 55660078aA) :
```bash
python manage.py loaddata simple_app_1/fixtures/db_dump.json
```
9. Загрузите файлы фикстур в базу данных (Admin - пароль - 55660078aA) :
```bash
python manage.py runserver
```
10. Откройте ваш веб-браузер и перейдите по адресу http://127.0.0.1:8000/ для проверки, работает ли ваш проект.



### Запуск используя Docker:

1. Запустите приложение Docker Desktop.
2. Выполните команду docker-compose build, чтобы собрать образы Docker:
```bash
docker-compose build
```
4. Затем выполните команду docker-compose up, чтобы запустить контейнеры в фоновом режиме:
```bash
docker-compose up -d
```
5. Запустите команду внутри контейнера для применения миграций:
```bash
docker-compose exec app python manage.py migrate
```
6. Создайте суперпользователя (если нужно):
```bash
docker-compose exec app python manage.py createsuperuser
```
7. Откройте браузер и перейдите по адресу http://127.0.0.1:8000/

8. Для остановки контейнеров используйте команду:
```bash
docker-compose down
```


### Для тестирования проекта:

1. В адресной строке браузера зайдите на http://127.0.0.1:8000/buy/3
2. Вы получите Stripe Session Id=3 для оплаты выбранного Item. 
При выполнении этого метода c бэкенда с помощью python библиотеки stripe выполнится запрос 
stripe.checkout.Session.create(...) и полученный session.id выдаваться в результате запроса. 
Вы получите {"session_id": "cs_test_a1OplEL0EZi0q0cc5ZY6UT61UiuQ3BqVuBCwZHeg3x13PTxiTQYu8jip27"}
3. В адресной строке браузера зайдите на http://127.0.0.1:8000/item/3
4. Нажмите на кнопку "Buy" или "Buy All"
5. Вы будете перенаправлены на форму stripe.redirectToCheckout(sessionId=session_id)
6. Заполните форму. Номер карты введите 4242 4242 4242 4242, период действия 02/26, трёхзначный код 123, 
остальные поля заполните любыми данными. 
7. Нажмите кнопку "оплатить". Вы будете перенаправлены на страницу успешной операции и увидите 
"Thanks for your order! We appreciate your business! If you have any questions, please email orders@example.com. "
8. Если вы введёте номен карты 4000 0000 0000 3220, то вы  увидите: "This is a test 3D Secure 2 authentication for a transaction with Stripe.
In live mode, customers will be asked to verify their identity with a push notification, a text message, or another method chosen 
by their bank."
9. Если вы введёте номен карты 4000 0000 0000 9995, то вы  увидите: "Ваша кредитная карта была отклонена, 
10. так как на ней недостаточно средств. Попробуйте вместо этого заплатить дебетовой картой."
11. Измените в пункте 3 http://127.0.0.1:8000/item/3 на http://127.0.0.1:8000/order/3,  а затем на http://127.0.0.1:8000/order/20.
И реализуйте все пункты проверки ещё раз.
12. Чтобы создать заказ, зайдите на http://127.0.0.1:8000/order/create и отправьте на сервер POST- запросом такой json: 
{
  "items": [
    {"item_id": 1, "quantity": 2},
    {"item_id": 3, "quantity": 1},
    {"item_id": 5, "quantity": 3}
  ]
}
В ответ получите ID заказа.

    
