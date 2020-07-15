""" `Keyboards` """

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from delivery.models import City, User, Category, Subcategory, Cart, CartProduct


def change_city() -> InlineKeyboardMarkup:
    """`Keyboard with list of cities`"""

    cities = City.objects.all().order_by('name')

    markup = InlineKeyboardMarkup()

    for city in cities:
        markup.add(InlineKeyboardButton(
            text=city.name,
            callback_data=f'user_city_{city.id}'))

    return markup


def main_menu(total_cart_price) -> InlineKeyboardMarkup:
    """`Main menu keyboard`"""

    markup = InlineKeyboardMarkup(2)
    markup.add(
        InlineKeyboardButton(text='📁 Каталог', callback_data='catalog'),
        InlineKeyboardButton(text='ℹ️ Информация',
                             callback_data='information')
    )
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(
            text='❓ Как пользоваться',
            callback_data='help'),
        InlineKeyboardButton(
            text='🛒 Корзина ({:,.2f} руб)'.format(total_cart_price),
            callback_data='cart_main'),
        InlineKeyboardButton(text='⚙️ Изменить город',
                             callback_data='config')
    )

    return markup


def select_category() -> InlineKeyboardMarkup:
    """`Category list keyboard`"""

    categories = Category.objects.all()

    markup = InlineKeyboardMarkup()

    for category in categories:
        markup.add(InlineKeyboardButton(
            text=f'{category.emoji} {category.name}',
            callback_data=f'category_{category.id}'))

    markup.add(InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data='main_menu'))

    return markup


def select_subcategory(category: Category) -> InlineKeyboardMarkup:
    """`Subcategory list keyboard`"""

    subcategories = Subcategory.objects.filter(category=category).order_by('name')

    markup = InlineKeyboardMarkup()

    for subcategory in subcategories:
        markup.add(InlineKeyboardButton(
            text=f'{subcategory.emoji} {subcategory.name}',
            switch_inline_query_current_chat=subcategory.emoji))

    markup.add(
        InlineKeyboardButton(
            text='🔍 Поиск',
            switch_inline_query_current_chat=f'{category.emoji} '),
        InlineKeyboardButton(
            text='⬅️ Назад', callback_data='catalog'))

    return markup


def product_detail(total_cart_price, product_id) -> InlineKeyboardMarkup:
    """`Product detail keyboard`"""

    markup = InlineKeyboardMarkup(1)

    markup.add(
        InlineKeyboardButton(
            text='Добавить',
            callback_data=f'add_product_{product_id}'))

    markup.add(
        InlineKeyboardButton(
            text='🛒 Корзина ({:,.2f} руб)'.format(total_cart_price),
            callback_data='cart_product'),
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='product_back'))

    return markup


def product_control(cart_product, user) -> InlineKeyboardMarkup:
    """`Product detail control keyboard`"""

    cart = Cart.objects.get(user=user)

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            text='-',
            callback_data=f'detail_minus_{cart_product.id}'),
        InlineKeyboardButton(
            text=cart_product.quantity,
            callback_data='product_quantity'),
        InlineKeyboardButton(
            text='+',
            callback_data=f'detail_plus_{cart_product.id}'))
    markup.row = 1
    markup.add(
        InlineKeyboardButton(
            text='🛒 Корзина ({:,.2f} руб)'.format(cart.total_price),
            callback_data='cart_product'))
    markup.add(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='product_back'))

    return markup


def cart_keyboard(user: User) -> InlineKeyboardMarkup:
    """`Cart keyboard`"""

    cart = Cart.objects.get(user=user)

    markup = InlineKeyboardMarkup()

    for cart_product in cart.products.all().order_by('product'):
        markup.add(
            InlineKeyboardButton(
                text=f'📦 {cart_product.quantity} x {cart_product}',
                callback_data='cart_product'))
        markup.add(
            InlineKeyboardButton(
                text='-',
                callback_data=f'cart_minus_{cart_product.id}'),
            InlineKeyboardButton(
                text='{:,.2f} руб'.format(
                    cart_product.price*cart_product.quantity),
                callback_data='product_quantity'),
            InlineKeyboardButton(
                text='+',
                callback_data=f'cart_plus_{cart_product.id}'))

    markup.add(
        InlineKeyboardButton(
            text='💰 {:,.2f} руб'.format(cart.total_price),
            callback_data='cart_sum'))

    if cart.total_price > 0:
        markup.add(
            InlineKeyboardButton(
                text='♻️ Очистить корзину',
                callback_data='clean_cart'))
        markup.add(
            InlineKeyboardButton(
                text='Оформить заказ ➡️',
                callback_data='make_order'))
    else:
        markup.add(
            InlineKeyboardButton(
                text='Ваша корзина пока пуста',
                callback_data='cart_empty'))
    markup.add(
        InlineKeyboardButton(
            text='⬅️ В меню',
            callback_data='main_menu'))

    return markup
