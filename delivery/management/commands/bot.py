"""`Telegram bot`"""

import logging
from uuid import uuid4
import emojis

from geopy.geocoders import Nominatim

from django.core.management.base import BaseCommand
from django.conf import settings

import telebot
from telebot.types import (InlineQueryResultArticle, InputTextMessageContent, InlineQuery, CallbackQuery,
                           Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

from delivery.models import (City, User, Order, OrderProduct, Category, Subcategory,
                             Product, Cart, CartProduct, Status)
from .keyboards import *

bot = telebot.TeleBot(settings.TOKEN)
telebot.logger.setLevel(logging.DEBUG)


@bot.callback_query_handler(func=lambda call: call.data == 'cart_main')
def cart_main_handler(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        text='Ваша корзина:\n\nКоснитесь товара чтобы посмотреть детали',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=cart_keyboard(user))


@bot.callback_query_handler(func=lambda call: call.data == 'clean_cart')
def clean_cart_handler(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    cart = Cart.objects.get(user=user)
    cart.products.all().delete()
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=cart_keyboard(user))


@bot.callback_query_handler(func=lambda call: call.data == 'make_order')
def make_order_handler(call: CallbackQuery):
    keyboard = ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = KeyboardButton(
        text='📞 Отправить номер телефона', request_contact=True)
    button_menu = KeyboardButton(text='⬅️ Назад')
    keyboard.add(button_phone, button_menu)
    bot.answer_callback_query(call.id)
    bot.send_message(
        text='Оставьте контакт или введите свой номер телефона, чтобы мы смогли связаться с вами, в формате: '
             '+79035287986',
        chat_id=call.message.chat.id,
        reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'cart_product')
def cart_product_handler(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        text='Ваша корзина:',
        chat_id=call.message.chat.id,
        reply_markup=cart_keyboard(user))


@bot.callback_query_handler(func=lambda call: 'add_product_' in call.data)
def add_product_query(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    product_id = call.data.split('_')[2]
    product = Product.objects.get(pk=product_id)
    cart = Cart.objects.get(user=user)

    cart_product, cart_product_created = cart.products.get_or_create(
        product=product,
        defaults={'product': product,
                  'quantity': 1,
                  'price': product.price}, )

    if not cart_product_created:
        cart_product.quantity = cart_product.quantity + 1
        cart_product.save()

    bot.answer_callback_query(call.id, text='Добавлено в корзину')
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=product_control(cart_product, user))


@bot.callback_query_handler(func=lambda call: 'detail_minus_' in call.data)
def product_minus(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    cart = Cart.objects.get(user=user)
    cart_product_id = call.data.split('_')[2]

    try:
        cart_product = CartProduct.objects.get(pk=cart_product_id)

        if cart_product.quantity <= 1:
            cart_product.delete()
            bot.answer_callback_query(call.id)
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=product_detail(cart.total_price, cart_product.product.id))
        else:
            cart_product.quantity -= 1
            cart_product.save()
            bot.answer_callback_query(call.id)
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=product_control(cart_product, user))
    except CartProduct.DoesNotExist:
        bot.answer_callback_query(call.id)
        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: 'cart_minus_' in call.data)
def cart_product_minus(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    cart_product_id = call.data.split('_')[2]

    try:
        cart_product = CartProduct.objects.get(pk=cart_product_id)
        if cart_product.quantity <= 1:
            cart_product.delete()
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=cart_keyboard(user))
        else:
            cart_product.quantity = cart_product.quantity - 1
            cart_product.save()
            bot.answer_callback_query(call.id)
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=cart_keyboard(user))
    except CartProduct.DoesNotExist:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=cart_keyboard(user))


@bot.callback_query_handler(func=lambda call: call.data == 'product_quantity')
def product_quantity(call: CallbackQuery):
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: 'detail_plus_' in call.data)
def product_plus(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    cart_product_id = call.data.split('_')[2]

    try:
        cart_product = CartProduct.objects.get(pk=cart_product_id)
        cart_product.quantity = cart_product.quantity + 1
        cart_product.save()

        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=product_control(cart_product, user))
    except CartProduct.DoesNotExist:
        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: 'cart_plus_' in call.data)
def cart_product_plus(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    cart_product_id = call.data.split('_')[2]

    try:
        cart_product = CartProduct.objects.get(pk=cart_product_id)
        cart_product.quantity = cart_product.quantity + 1
        cart_product.save()

        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=cart_keyboard(user))
    except CartProduct.DoesNotExist:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=cart_keyboard(user))


@bot.callback_query_handler(func=lambda call: 'category_' in call.data)
def category_query(call: CallbackQuery):
    category_id = call.data.split('_')[1]
    category = Category.objects.get(pk=category_id)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        text='Подкатегории товаров:',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=select_subcategory(category))


@bot.callback_query_handler(func=lambda call: call.data == 'catalog')
def catalog_query(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        text='Категории товаров:',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=select_category())


@bot.callback_query_handler(func=lambda call: call.data == 'product_back')
def product_back(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def main_menu_query(call: CallbackQuery):
    user = User.objects.get(telegram_id=call.from_user.id)
    cart = Cart.objects.get(user=user)

    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        text='Главное меню:',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=main_menu(cart.total_price))


@bot.callback_query_handler(func=lambda call: call.data == 'config')
def city_change_query(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        text='Ваш город?',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=change_city())


@bot.callback_query_handler(func=lambda call: 'user_city' in call.data)
def user_city_query(call: CallbackQuery):
    city_id = call.data.split('_')[2]

    user, created = User.objects.update_or_create(
        telegram_id=call.from_user.id,
        defaults={
            'first_name': call.from_user.first_name,
            'username': str(call.from_user.username or ''),
            'telegram_id': call.from_user.id,
            'chat_id': call.message.chat.id,
            'city': City.objects.get(pk=city_id)
        },
    )

    if created:
        bot.answer_callback_query(call.id, f'User created ID = {user.id}')
        cart = Cart(user=user)
        cart.save()
    else:
        bot.answer_callback_query(call.id, f'User updated ID = {user.id}')

    cart = Cart.objects.get(user=user)

    bot.edit_message_text(
        text='Главное меню:',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=main_menu(cart.total_price))


# Inline handlers

@bot.inline_handler(lambda query: bool(len(query.query.strip())))
def product_search_query(inline_query: InlineQuery):
    text = inline_query.query.strip()
    search_field = text[1:].strip()
    offset = int(inline_query.offset) if inline_query.offset else 0
    next_offset = offset + 30
    results = list()
    products = list()

    emoji = text[0]
    contains_emoji = emojis.get(emoji)

    if contains_emoji:
        try:
            category = Category.objects.get(emoji=emoji)
            subcategories = Subcategory.objects.filter(category=category)
            products = Product.objects.filter(
                subcategory__in=subcategories,
                name__icontains=search_field).order_by('name')[offset:next_offset]

        except Category.DoesNotExist:
            try:
                subcategory = Subcategory.objects.get(emoji=emoji)
                products = Product.objects.filter(
                    subcategory=subcategory,
                    name__icontains=search_field).order_by('name')[offset:next_offset]
            except Subcategory.DoesNotExist:
                pass

        for product in products:
            results.append(InlineQueryResultArticle(
                id=str(uuid4()),
                title=product.name,
                input_message_content=InputTextMessageContent(
                    f'product_{product.id}'),
                description='{:,.2f} руб'.format(product.price),
                thumb_url=product.image))

    bot.answer_inline_query(
        inline_query.id, results, next_offset=str(next_offset))


# Message handlers

@bot.message_handler(content_types=['contact'])
def contact_handler(message: Message):
    user = User.objects.get(telegram_id=message.from_user.id)
    user.last_phone_number = message.contact.phone_number

    user.save()

    keyboard = ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_geo = KeyboardButton(
        text='📍 Отправить местоположение', request_location=True)
    button_menu = KeyboardButton(text='⬅️ Назад')
    keyboard.add(button_geo, button_menu)
    bot.send_message(
        text='Пожалуйста, введите  адрес доставки или нажмите на скрепку (значек скрепки).',
        chat_id=message.chat.id,
        reply_markup=keyboard)


@bot.message_handler(content_types=['location'])
def location_handler(message: Message):
    user = User.objects.get(telegram_id=message.from_user.id)
    cart = Cart.objects.get(user=user)
    geolocation = Nominatim(user_agent="delivery")

    user.last_address = geolocation.reverse(
        f'{message.location.latitude}, {message.location.longitude}')

    user.save()

    order = Order(
        user=user,
        status=Status.objects.get(pk=1),
        phone_number=user.last_phone_number,
        address=user.last_address
    )

    order.save()

    for product in cart.products.all().order_by('product'):
        order_product = OrderProduct(
            product=product.product,
            quantity=product.quantity,
            price=product.price
        )
        order_product.save()
        order.products.add(order_product)
    total_price = cart.total_price
    cart.products.all().delete()
    text = '❕ Ваш заказ передан на обработку, ожидайте подтверждения в боте.\n\n'
    text += f'1️⃣ Номер Вашего заказа № {order.id}\n\n'
    text += '📦 Товары:\n\n'

    for product in order.products.all().order_by('product'):
        text += '{} x {} - {:,.2f} руб\n'.format(
            product.quantity, product.product.name, product.sum)
    text += '\n💰 Общая сумма заказа {:,.2f} руб'.format(total_price)
    text += f'\n\n📍 Адрес доставки - {order.address}\n'
    text += f'\n📞 Номер телефона - {order.phone_number}'

    bot.send_message(
        text=text,
        chat_id=message.chat.id,
        reply_markup=ReplyKeyboardRemove())
    bot.send_message(
        chat_id=message.chat.id,
        text='Главное меню:',
        reply_markup=main_menu(cart.total_price))


@bot.message_handler(func=lambda message: bool(message.text) and 'product_' in message.text)
def product_detail_handler(message: Message):
    user = User.objects.get(telegram_id=message.from_user.id)
    cart = Cart.objects.get(user=user)
    product_id = message.text.split('_')[1]

    try:
        product = Product.objects.get(id=product_id)
        bot.send_photo(
            chat_id=message.chat.id,
            photo=product.image,
            caption='📦 ' + str(product.name) + '\n\n' + '📋 ' + str(product.description) + '\n\n' +
                    '💰 ' + '{:,.2f} руб'.format(product.price),
            reply_markup=product_detail(cart.total_price, product_id))
    except ValueError:
        pass
    finally:
        bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(func=lambda message: message.text == '⬅️ Назад')
def back_menu_message(message: Message):
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['start'])
def start(msg: Message):
    """Start command."""

    try:
        user = User.objects.get(telegram_id=msg.from_user.id)
        cart = Cart.objects.get(user=user)
        bot.send_message(
            chat_id=msg.chat.id,
            text='Главное меню:',
            reply_markup=main_menu(cart.total_price))
    except User.DoesNotExist:
        bot.send_message(
            chat_id=msg.chat.id,
            text='Ваш город?',
            reply_markup=change_city())


class Command(BaseCommand):
    """`Start delivery bot`"""

    help = 'TG Bot'

    def handle(self, *args, **options):
        bot.polling(True)
