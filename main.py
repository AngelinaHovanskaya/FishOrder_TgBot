import time
import datetime
import re
from aiogram import Bot, types, Dispatcher
# from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests

from UserService import UserService
from GoogleSheet import GoogleSheetService
from OrderProduct import OrderProduct

# bot = Dispatcher(Bot(token='6534722740:AAHN3stKJwCZmfGx2TrPrigynrOmHNTJVmk'))
bot = Dispatcher(Bot(token='6946444897:AAHQYgMX0wZYC_bx72Mi5oWcCdJ9cj8PWMc')) #мой бот'
google_sheet_service = GoogleSheetService()
user_service = UserService()




@bot.message_handler(commands=["start"])
async def help_command(message: types.Message):


    user_id = message.from_user.id
    user_session = user_service.get_user_session(user_id)
    user_session.default_parameters()

    catalog_or_make_order = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        *(['Показать ассортимент', 'Выбрать товар']))
    await message.answer('Здравствуйте!\n'
                         'С помощью этого бота Вы можете сделать заказ.\n'
                         'Если появятся вопросы, напишите /help', reply_markup=catalog_or_make_order)
    user_service.set_user_session(user_id, 1)


@bot.message_handler(commands=["info"])
async def help_command(message: types.Message):
    await message.answer('Чтобы сделать заказ напишите /start\nЕсли у Вас возникли вопросы напишите в нашу группу\nhttps://t.me/+V5Yas-uRvlNTiis0')


@bot.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.answer('Для создания заказа напиши /start\nЕсли возникли сложности напишите нам в группу\nhttps://t.me/+V5Yas-uRvlNTiis0')


@bot.message_handler(content_types=["text"])
async def send_message(message: types.Message):
    user_id = message.from_user.id
    user_session = user_service.get_user_session(user_id)

    if user_session.state == 1:

        if message.text == 'Показать ассортимент':

            msg = await message.answer(f"Загрузка данных ⏳")


            catalog = '🐟Наш ассортимент🐟\n\n'

            catalog += '📍Продукция в упаковках по 250 гр\n\n'

            products_packing = google_sheet_service.get_products_list_packing()
            for product in products_packing:
                catalog += product.name + ': ' + product.price + product.unit + '\n'

            catalog += '\n📍Поштучная продукция:\n1 рыбка ~1,5-2 кг\n\n'
            products_apiece = google_sheet_service.get_products_list_apiece()
            for product in products_apiece:
                catalog += product.name + ': ' + product.price + product.unit + '\n'

            make_order = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                KeyboardButton('Выбрать товар'))

            await msg.delete()
            await message.answer(f"{catalog}", reply_markup=make_order)
            return

        elif message.text == 'Выбрать товар':
            msg = await message.answer(f"Загрузка данных ⏳")
            choose_product = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            products_apiece = google_sheet_service.get_products_list_apiece()
            products_packing = google_sheet_service.get_products_list_packing()

            for product in products_packing:
                choose_product.add(product.name)

            for product in products_apiece:
                choose_product.add(product.name)

            await msg.delete()
            await message.answer("Выберите элемент:", reply_markup=choose_product)
            user_service.set_user_session(user_id, 2)

        else:

            catalog_or_make_order = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *(['Показать ассортимент', 'Выбрать товар']))
            await message.answer("Некорректный ответ. Нажмите на кнопку ниже.", reply_markup=catalog_or_make_order)
            return

    elif user_session.state == 2:
        msg = await message.answer(f"Загрузка данных ⏳")
        message_product_name = message.text
        choose_product = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        product_name_apiece = []
        product_name_packing = []

        products_apiece = google_sheet_service.get_products_list_apiece()
        products_packing = google_sheet_service.get_products_list_packing()

        for product in products_packing:
            product_name_packing.append(product.name)
            choose_product.add(product.name)

        for product in products_apiece:
            product_name_apiece.append(product.name)
            choose_product.add(product.name)



        if message_product_name in product_name_apiece or message_product_name in product_name_packing:
            if user_session.change_product:
                user_session.orders[user_session.number_str_for_change].name = message_product_name
                check_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                    *["Проверить заказ"])
                await msg.delete()
                await message.answer("Давайте перепроверим заказ", reply_markup=check_order)
                user_service.set_user_session(user_id, 11)
                return
            if message_product_name in product_name_apiece:
                await msg.delete()
                await message.answer(
                    "Введите количество желаемого продукта\n1 рыбка ~1,5-2 кг")
            else:
                await msg.delete()
                await message.answer(
                    "Введите количество упаковок желаемого продукта\n1 упаковка 250г")

            order_product = OrderProduct()
            order_product.name = message_product_name
            user_service.set_user_session(user_id, 3)
            user_session.current_order = order_product
        else:
            await message.answer('Неверный формат сообщения. Выберите продукт из списка', reply_markup=choose_product)
            return

    elif user_session.state == 3:
        count_product = message.text
        correct_count = count_product
        if ',' in correct_count or '.' in correct_count:
            correct_count = correct_count.replace(',', '')
            correct_count = correct_count.replace('.', '')

        if correct_count.isdigit():
            if user_session.change_weight:
                user_session.orders[user_session.number_str_for_change].count = count_product
                check_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                    *["Проверить заказ"])
                await message.answer("Давайте перепроверим заказ", reply_markup=check_order)
                user_service.set_user_session(user_id, 11)
            else:
                choose = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*["Да", "Нет"])
                await message.answer('Хотите заказать что-то еще?', reply_markup=choose)
                user_service.set_user_session(user_id, 4)
                current_order = user_session.current_order
                current_order.count = count_product
                user_session.orders.append(current_order)

        else:
            await message.answer('Неверный формат сообщения. Введите нужный вес продукта.')
            return

    elif user_session.state == 4:

        if message.text == 'Да':
            msg = await message.answer(f"Загрузка данных ⏳")
            choose_product = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            products_apiece = google_sheet_service.get_products_list_apiece()
            products_packing = google_sheet_service.get_products_list_packing()

            for product in products_packing:
                choose_product.add(product.name)

            for product in products_apiece:
                choose_product.add(product.name)

            await msg.delete()
            await message.answer("Выберите элемент:", reply_markup=choose_product)
            user_service.set_user_session(user_id, 2)

        elif message.text == 'Нет':
            if user_session.change_title:
                check_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                    *["Проверить заказ"])
                await message.answer("Давайте перепроверим заказ", reply_markup=check_order)
                user_service.set_user_session(user_id, 11)
            else:
                await message.answer("Отлично!\nДля дальнейшего оформления заказа нам понадобятся Ваши контакты")
                await message.answer("Введите Ваше имя:")
                user_service.set_user_session(user_id, 5)
        else:
            choose = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*["Да", "Нет"])
            await message.answer('Неверный формат сообщения. Нажмите на кнопку ниже')
            await message.answer('Хотите заказать что-то еще?', reply_markup=choose)
            return

    elif user_session.state == 5:
        user_name = message.text
        user_session.name = user_name
        user_service.set_user_session(user_id, 6)
        await message.answer('Введите номер телефона в формате\n+7-xxx-xxx-xx-xx')

    elif user_session.state == 6:
        phone = message.text

        result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
                          phone)
        if result:
            user_session.phone = phone
            user_service.set_user_session(user_id, 7)
            await message.answer('Введите адрес доставки')
        else:
            await message.answer(
                'Невереный формат сообщения.\nКорректная форма для ввода номер телефона\n+7-xxx-xxx-xx-xx')
            return

    elif user_session.state == 7:
        user_session.address = message.text
        user_service.set_user_session(user_id, 8)
        await message.answer(
            'Напишите желаемую дату доставки, мы постараемся привезти к этому дню.')

    elif user_session.state == 8:
        date_delivery = message.text
        user_session.delivery_date = date_delivery

        user_service.set_user_session(user_id, 9)
        choose = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*["Да", "Нет"])
        await message.answer('Хотите указать комментарий к заказу?', reply_markup=choose)

    elif user_session.state == 9:

        if message.text == 'Да':
            await message.answer("Введите комментарий к заказу")
            user_service.set_user_session(user_id, 10)

        elif message.text == 'Нет':
            check_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *["Проверить заказ"])
            await message.answer("Давайте проверим заказ", reply_markup=check_order)
            user_service.set_user_session(user_id, 11)
            user_session.add_inf = '-'
        else:
            choose = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*["Да", "Нет"])
            await message.answer('Неверный формат сообщения. Нажмите на кнопку')
            await message.answer('Хотите указать комментарий к заказу?', reply_markup=choose)
            return

    elif user_session.state == 10:
        add_inf = message.text
        user_service.set_user_session(user_id, 11)
        user_session.add_inf = add_inf
        check_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*["Проверить заказ"])
        await message.answer("Давайте проверим заказ", reply_markup=check_order)

    elif user_session.state == 11:

        orders = user_session.orders
        send_orders = ''
        for order in orders:
            send_orders += order.name + ': ' + order.count + " шт\n"

        await message.answer(
            f"Имя: {user_session.name}\nНомер телефона: {user_session.phone}\nАдрес: {user_session.address}\nДата доставки заказа: {user_session.delivery_date}\n\nВаш заказ:\n{send_orders}\nКомментарий к заказу: {user_session.add_inf}")
        user_service.set_user_session(user_id, 12)
        choose = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*["Да", "Нет"])
        await message.answer('Все верно?', reply_markup=choose)

    elif user_session.state == 12:
        if message.text == 'Да':
            await message.answer(
                "Ваш заказ принят.\nЕсли возникнут вопросы напишите в нашу группу\nhttps://t.me/+V5Yas-uRvlNTiis0\n\nДля повторного заказа напишите /start")
            user_service.set_user_session(user_id, 1000)
            order_date = datetime.datetime.now().strftime('%d.%m.%y')
            orders = ''
            for order in user_session.orders:
                orders += order.name + ': ' + order.count + '\n'
            google_sheet_service.write_order(message.from_user.username, user_session.name, user_session.phone,
                                             user_session.address, orders,
                                             user_session.delivery_date, order_date, user_session.add_inf)
            user_session.default_parameters()

            params = {
                'chat_id': '1324557750', #мой id
                # 'chat_id': '217744186',
                'text': 'Создан заказ',
            }
            requests.get('https://api.telegram.org/bot6534722740:AAHN3stKJwCZmfGx2TrPrigynrOmHNTJVmk/sendMessage',
                         params=params)

        elif message.text == 'Нет':
            change_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *["Имя", "Номер телефона", "Адрес", "Предположительная дата доставки", "Заказ", "Комментарий"])
            await message.answer("Какое поле хотите исправить?", reply_markup=change_order)
            user_service.set_user_session(user_id, 13)

        else:
            choose = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*["Да", "Нет"])
            await message.answer('Неверный формат сообщения. Нажмите на кнопку')
            await message.answer('Хотите указать комментарий к заказу?', reply_markup=choose)
            return

    elif user_session.state == 13:
        change_title = message.text
        user_session.change_title = change_title
        if change_title == "Заказ":
            change_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *["Добавить", "Изменить", 'Удалить'])
            await message.answer("Вы хотите что-то добавить, изменить или удалить?",
                                 reply_markup=change_order)
            user_service.set_user_session(user_id, 15)
            return
        await message.answer('Введите корректные данные')
        user_service.set_user_session(user_id, 14)

    elif user_session.state == 14:
        change_value = message.text
        change_title = user_session.change_title
        if change_title == 'Имя':
            user_session.name = change_value
        elif change_title == 'Номер телефона':
            # проверка
            result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
                              change_value)

            if result:
                user_session.phone = change_value
            else:
                await message.answer(
                    'Невереный формат сообщения.\nКорректная форма для ввода номер телефона\n+7-xxx-xxx-xx-xx')
                return
        elif change_title == 'Адрес':
            user_session.address = change_value

        elif change_title == "Дата доставки":
            user_session.delivery_date = change_value

        elif change_title == "Комментарий":
            user_session.add_inf = change_value
        else:
            change_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *["Имя", "Номер телефона", "Адрес", "Предположительная дата доставки", "Заказ", "Комментарий"])
            await message.answer("Некорректный формат сообщения. Выберите поле, которое хотите изменить",
                                 reply_markup=change_order)
            return

        check_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*["Проверить заказ"])
        await message.answer("Давайте перепроверим заказ", reply_markup=check_order)
        user_service.set_user_session(user_id, 11)

    elif user_session.state == 15:
        change_value_order = message.text
        if change_value_order == 'Добавить':
            msg = await message.answer(f"Загрузка данных ⏳")
            choose_product = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            products_apiece = google_sheet_service.get_products_list_apiece()
            products_packing = google_sheet_service.get_products_list_packing()

            for product in products_packing:
                choose_product.add(product.name)
            for product in products_apiece:
                choose_product.add(product.name)

            await msg.delete()
            await message.answer("Выберите элемент:", reply_markup=choose_product)
            user_service.set_user_session(user_id, 2)

        elif change_value_order == 'Изменить':
            change_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *["Вес", "Продукт"])
            await message.answer("Что Вы хотите изменить вес или продукт?", reply_markup=change_order)
            user_service.set_user_session(user_id, 17)

        elif change_value_order == 'Удалить':

            orders = user_session.orders
            product_list = []
            for order in orders:
                product_list.append(order.name)
            del_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *product_list)
            await message.answer('Выберите продукт, который нужно удалить из списка', reply_markup=del_order)
            user_service.set_user_session(user_id, 16)

        else:
            change_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *["Добавить", "Изменить"])
            await message.answer("Неверный формат сообщения.\nВы хотите что-то добавить или изменить текущий заказ",
                                 reply_markup=change_order)
            return

    elif user_session.state == 16:
        name_for_delete = message.text
        orders = user_session.orders
        product_list = []
        for order in orders:
            product_list.append(order.name)

        if name_for_delete in product_list:
            index_for_del = product_list.index(name_for_delete)
            user_session.orders.pop(index_for_del)
            check_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *["Проверить заказ"])
            await message.answer("Давайте перепроверим заказ", reply_markup=check_order)
            user_service.set_user_session(user_id, 11)

        else:
            del_order = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *product_list)
            await message.answer('Некорректное сообщение.\nВыберите продукт, который нужно удалить из списка',
                                 reply_markup=del_order)
            return

    elif user_session.state == 17:
        change_order = message.text
        orders = user_session.orders
        product_list = []
        send_orders = ''
        counter = 1
        for order in orders:
            product_list.append(order.name)
            send_orders += str(counter) + ': ' + order.name + ': ' + order.count + " шт\n"
            counter += 1

        if change_order == 'Вес':
            user_session.change_weight = True

        elif change_order == 'Продукт':
            user_session.change_product = True

        else:
            change_orders = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *["Вес", "Продукт"])
            await message.answer("Некорректное сообщение.\nВыберите, что Вы хотите изменить вес или продукт?",
                                 reply_markup=change_orders)
            return

        change_orders = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
            *[str(i) for i in range(1, counter)])
        await message.answer(f"Выберите номер строки, в которой хотите изменить {change_order.lower()}:\n{send_orders}",
                             reply_markup=change_orders)

        user_service.set_user_session(user_id, 18)

    elif user_session.state == 18:
        try:
            number_string = int(message.text) - 1
            if number_string == -1:
                user_session.number_str_for_change = 0
            user_session.number_str_for_change = number_string

            if user_session.change_product:
                choose_product = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

                products_apiece = google_sheet_service.get_products_list_apiece()
                products_packing = google_sheet_service.get_products_list_packing()

                for product in products_packing:
                    choose_product.add(product.name)
                for product in products_apiece:
                    choose_product.add(product.name)

                await message.answer("Выберите новый продукт:", reply_markup=choose_product)
                user_service.set_user_session(user_id, 2)
            elif user_session.change_weight:
                await message.answer(f"Введите нужное значение")
                user_service.set_user_session(user_id, 3)

        except:
            change_orders = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
                *[str(i) for i in range(1, len(user_session.orders) + 1)])
            await message.answer(f"Неверный формат сообщения.\nВыберите номер строки, в которую хотите внести измения",
                                 reply_markup=change_orders)

    else:
        await message.answer('Чтобы узнать о функциях бота напишите /info')


def start_bot():
    if __name__ == '__main__':
        print('The bot is running')
        executor.start_polling(bot)


start_bot()
