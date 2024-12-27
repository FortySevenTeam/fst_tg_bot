import requests
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

import app.keyboards as kb

router = Router()

# Получает все сделки для пользователя с данным chat_id,
# записывает полученные данные в словарь, где ключами являются имена предметов, а значениями - сделки целиком
def get_orders(chat_id):
    order_check = requests.get(f"http://localhost:8082/api/v1/orders/{chat_id}")
    orders = {}

    for order in order_check.json():
        orders[order["name"]] = order

    return orders

# ================================================= STATES =================================================

# Стейт для регистрации пользователя
class Register(StatesGroup):
    Email = State()
    Temp = State()
    Code = State()

# Стейт для добавления новой сделки в портфель
class AddItem(StatesGroup):
    ItemName = State()
    ItemAmount = State()
    ItemPrice = State()

# Стейт для удаления сделки из портфеля
class RemoveItem(StatesGroup):
    ItemName = State()
    ItemAmount = State()

# Стейт для обновления информации о сделке
class UpdateItem(StatesGroup):
    ItemName = State()
    ItemAmount = State()
    ItemPrice = State()

# ================================================= START COMMAND =================================================

# Выводит приветственное сообщение с вызовом команды старт
# TODO Если пользователь уже есть в базе,
#  вывести соответствующее приветствие (Например, "С возвращением <имя пользователя>")
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в бота FST! \n"
        "Напишите /register, чтобы начать! \n\n\n"
        "(Для входа нажмите 'Авторизоваться')",
        reply_markup=kb.Reg_check
    )

# ================================================= AUTH CHECK =================================================

# TODO Реализовать вывод сообщения об ошибке пользователю, если сервер отвечает неправильно или не отвечает вовсе
@router.callback_query(F.data == "Auth_check")
# TODO Deprecated
async def auth_check(callback: CallbackQuery):
    await callback.answer('')

    chat_id = callback.message.chat.id
    auth_response = requests.get(f"http://localhost:8082/api/v1/orders/{chat_id}")

    if auth_response.status_code == 200:
        await callback.message.edit_text("Успешно!", reply_markup=kb.Reg)
    else : await callback.message.edit_text("Вы не зарегистрированы \nВведите /register для регистрации")

# ================================================= REGISTRATION =================================================

# Устанавливает в стейте поле Email для записи
@router.message(Command('register'))
async def register(message: Message, state: FSMContext):
    await state.set_state(Register.Email)
    await message.answer('Для регистрации введите почту для кода подтверждения')

# Записывает email в стейт
# TODO Реализовать валидацию вводимых данных
@router.message(Register.Email)
async def register_email(message: Message, state: FSMContext):
    await state.update_data(Email=message.text) # Обновление поля Email в стейте
    await state.set_state(Register.Code) # Переключение стейта на запись поля Code

    data = await state.get_data()
    await message.answer(f'Введите код подтверждения с почты \n\n{data["Email"]}')

    if "0" == "0":
        # Формирование словаря для запроса на сервер
        user_details = {
            "email": data["Email"],
            "chat_id": message.chat.id
        }

        # Запрос на сервер для добавления нового пользователя
        response = requests.post("http://localhost:8888/api/v1/registration", json=user_details)
        cookies = response.cookies.get_dict()
        await state.update_data(Temp=cookies)
    else : await message.answer("Введен неверный код подтверждения, повторите регистрацию")


# Записывает код в стейт и выводит пользователю его учётные данные
# TODO Реализовать валидацию вводимых данных, обработку ошибок при разных кодах ответа от сервера;
# TODO Сначала запрос на сервер вместе с обработкой ошибок для разных кодов ответа,
#  а после этого вывод сообщения пользователю
@router.message(Register.Code)
async def register_code(message: Message, state: FSMContext):
    await state.update_data(Code=message.text) # Обновление поля Code в стейте
    data = await state.get_data() # Получение всех полей из стейта
    link = "http://localhost:8888/api/v1/registration/confirm?otp=" + data["Code"]
    response = requests.put(link, cookies=data["Temp"], json=data)

    if response == 200:
        await message.answer("Регистрация пройдена успешно.", reply_markup=kb.main)
    else:
        await message.answer(response.text)
    await state.clear() # Очистка данных стейта

# ================================================= MENU =================================================

# Выводит главное меню с клавиатурой для навигации по разделам
@router.callback_query(F.data == 'Main_menu')
async def main_menu(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(
        'Это меню, потом распишу, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        reply_markup=kb.main
    )

# Запрашивает и выводит список вложений пользователя
# TODO Переделать с использованием функции get_orders()
@router.callback_query(F.data == 'Calc_menu')
async def calc_menu(callback: CallbackQuery):
    await callback.answer('')
    chat_id = callback.message.chat.id
    # Список всех сделок для пользователя с данным chat_id
    order_response = (
        requests.get(f"http://localhost:8082/api/v1/orders/{chat_id}")
    )
    res = ''
    orders = []

    if len(order_response.text) > 2:
        for order in order_response.json():
            orders.append(order)

    i = 1
    full_price = 0
    for order in orders:
        full_price = (float(order["buyPrice"]) * float(order["quantity"])) + full_price
        # Заполнение общей строки с информацией о каждой сделке
        res += (
            f'{i}.    '
            f'{order["name"]}\n       '
            f'Количество: {order["quantity"]}\n       '
            f'Средняя цена: {order["buyPrice"]}\n\n'
        )
        i += 1

    await callback.message.edit_text(
        f'Общая стоимость портфеля: {full_price}\n\n'
        f'Содержимое вашего портфеля: \n\n{res}',
        reply_markup=kb.Calc
    )

# ================================================= ADD ORDER =================================================

# Устанавливает в стейте поле ItemName для записи
@router.callback_query(F.data == 'Add_item')
async def calc_add_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Введите название предмета', reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddItem.ItemName)

# Записывает наименование предмета в стейт
@router.message(AddItem.ItemName)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(ItemName=message.text) # Обновление поля ItemName в стейте
    await state.set_state(AddItem.ItemAmount) # Установка нового поля стейта для ввода
    await message.answer('Введите количество предметов')

# Записывает количество предметов в сделке
@router.message(AddItem.ItemAmount)
async def add_item_amount(message: Message, state: FSMContext):
    await state.update_data(ItemAmount=message.text) # Обновление поля ItemAmount в стейте
    await state.set_state(AddItem.ItemPrice)
    await message.answer('Введите цену покупки')

# Записывает цену закупки предмета,
# выводит пользователю сообщение о добавленном предмете
# TODO Сначала запрос на сервер вместе с обработкой ошибок для разных кодов ответа,
#  а после этого вывод сообщения пользователю
@router.message(AddItem.ItemPrice)
async def add_item_price(message: Message, state: FSMContext):
    await state.update_data(ItemPrice=message.text)
    item_data = await state.get_data()

    await message.answer(
    f'Добавлено в портфель: \nНазвание: {item_data["ItemName"]}'
        f'\nКоличество: {item_data["ItemAmount"]}'
        f'\nЦена покупки: {item_data["ItemPrice"]}',
        reply_markup=kb.Calc_back
    )

    chat_id = message.chat.id
    # Формирование словаря для запроса на сервер
    order_details = {
        "name": item_data["ItemName"],
        "quantity": item_data["ItemAmount"],
        "buy_price": item_data["ItemPrice"],
        "chat_id": chat_id
    }
    # Отправление запроса на сервер для добавления новой сделки
    requests.post("http://localhost:8082/api/v1/orders", json=order_details)

    await state.clear() # Очистка данных в стейте

# ================================================= REMOVE ORDER =================================================

# Устанавливает в стейте поле ItemName для записи
@router.callback_query(F.data == 'Remove_item')
async def calc_remove_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Введите название предмета', reply_markup=ReplyKeyboardRemove())
    await state.set_state(RemoveItem.ItemName) # Установка поля ItemName в качестве поля ввода

# Обновляет значение поля ItemName и устанавливает следующее поле стейта для записи
@router.message(RemoveItem.ItemName)
async def remove_item_name(message: Message, state: FSMContext):
    await state.update_data(ItemName=message.text) # Обновление поля ItemName в стейте
    await state.set_state(RemoveItem.ItemAmount) # Установка нового поля в стейте для ввода
    await message.answer('Введите количество предметов')

# Обновляет количество предметов в сделке или удаляет сделку полностью,
# если введённое количество предметов >= количеству предметов в сделке
# TODO Добавить условие для проверки того,
#  не совпадает ли введённое количество с количеством в имеющейся сделке
#  или не равны ли эти значения
# TODO Сначала запрос на сервер вместе с обработкой ошибок для разных кодов ответа,
#  а после этого вывод сообщения пользователю
@router.message(RemoveItem.ItemAmount)
async def remove_item_amount(message: Message, state: FSMContext):
    await state.update_data(ItemAmount=message.text) # Обновление поля ItemAmount в стейте
    item_data = await state.get_data() # Получение данных из стейта
    chat_id = message.chat.id

    await message.answer(f'Удалено из портфеля: \nНазвание: {item_data["ItemName"]}'
                         f'\nКоличество: {item_data["ItemAmount"]}', reply_markup=kb.Calc_back)

    # Формирование словаря для запроса на сервер
    order_details = {
        "name": item_data["ItemName"],
        "quantity": item_data["ItemAmount"],
        "chat_id": chat_id
    }
    # Запрос на удаление сделки из портфеля пользователя
    requests.delete("http://localhost:8082/api/v1/orders", json=order_details)

    await state.clear() # Очистка данных в стейте

# ================================================= UPDATE ORDER =================================================

# Устанавливает в стейте поле ItemName для записи
@router.callback_query(F.data == 'Update_item')
async def calc_update_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer(
        'Введите название предмета, данные которого хотите изменить',
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UpdateItem.ItemName)

# Обновляет имя предмета или, уведомляя пользователя об ошибке, возвращается на шаг назад
@router.message(UpdateItem.ItemName)
async def update_item_name(message: Message, state: FSMContext):
    await state.update_data(ItemName=message.text) # Обновление поля ItemName в стейте
    orders = get_orders(message.chat.id) # Получение списка всех сделок для пользователя
    check_data = await state.get_data()

    try:
        await state.set_state(UpdateItem.ItemAmount) # Установить поле ItemAmount для записи
        await message.answer(
            f'Название предмета: {orders[check_data["ItemName"]]}\n\nВведите новое количество предметов'
        )
    except KeyError: # Может выброситься, если запрошенный список не содержит сделки с запрошенным предметом или пуст
        await state.set_state(UpdateItem.ItemName) # Вернуть стейт в положение ввода в поле ItemName
        await message.answer("Введенного предмета не обнаружено, введите заново")

# Обновляет количество предметов в сделке
@router.message(UpdateItem.ItemAmount)
async def update_item_amount(message: Message, state: FSMContext):
    await state.update_data(ItemAmount=message.text) # Обновление поля ItemAmount
    await state.set_state(UpdateItem.ItemPrice) # Установка поля ItemPrice для ввода
    await message.answer('Введите новую цену покупки')

# Обновляет цену предмета в сделке
# TODO Сначала запрос на сервер вместе с обработкой ошибок для разных кодов ответа,
#  а после этого вывод сообщения пользователю
@router.message(UpdateItem.ItemPrice)
async def update_item_price(message: Message, state: FSMContext):
    await state.update_data(ItemPrice=message.text)  # Обновление поля ItemPrice
    update_data = await state.get_data() # Получение данных из стейта
    chat_id = message.chat.id
    await message.answer(f'Данные обновлены в портфеле: \nНазвание: {update_data["ItemName"]}'
                         f'\nКоличество: {update_data["ItemAmount"]}'
                         f'\nЦена покупки: {update_data["ItemPrice"]}', reply_markup=kb.Calc_back)

    # Формирование словаря для запроса на сервер
    order_details = {
        "name": update_data["ItemName"],
        "quantity": update_data["ItemAmount"],
        "buy_price": update_data["ItemPrice"],
        "chat_id": chat_id
    }
    # Запрос на сервер для обновления данных о сделке
    requests.patch("http://localhost:8082/api/v1/orders", json=order_details)

    await state.clear() # Очистка стейта

# ================================================= UPDATE PRICE =================================================

# Выводит пользователю сообщение об успешном обновлении цен
@router.callback_query(F.data == 'Price_update')
async def price_update(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Цены обновлены', reply_markup=kb.Calc_back)

# ================================================= SETTINGS =================================================

# Выводит пользователю сообщение с призывом к выбору категории
@router.callback_query(F.data == 'Settings')
async def settings(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите нужную категорию:', reply_markup=kb.Settings)

# ================================================= CURRENCY =================================================

# Выводит пользователю сообщение о нынешнем курсе доллара в стиме
@router.callback_query(F.data == 'Currency')
async def currency(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Курс доллара в стим на сегодня = много рублей', reply_markup=kb.main_back)

# ================================================= TEST =================================================

#test
# TODO Deprecated
@router.callback_query(F.data == 'Test')
async def test(callback: CallbackQuery):
    await callback.answer('')