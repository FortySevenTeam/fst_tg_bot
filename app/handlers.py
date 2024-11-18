from webbrowser import Error

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import requests
import app.keyboards as kb

router = Router()

def get_orders(chat_id):
    order_check = requests.get(f"http://localhost:8082/api/v1/orders/{chat_id}")
    orders = {}
    for order in order_check.json():
        orders[order["name"]] = order

    return orders

class Register(StatesGroup):
    Email = State()
    Code = State()

class AddItem(StatesGroup):
    ItemName = State()
    ItemAmount = State()
    ItemPrice = State()

class RemoveItem(StatesGroup):
    ItemName = State()
    ItemAmount = State()

class UpdateItem(StatesGroup):
    ItemName = State()
    ItemAmount = State()
    ItemPrice = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать в FST! \nНапишите /register чтобы начать! \n\n\n(Для входа нажмите 'Авторизоваться')", reply_markup=kb.Reg_check)

#Auth check start
@router.callback_query(F.data == "Auth_check")
async def auth_check(callback: CallbackQuery):
    await callback.answer('')
    chat_id = callback.message.chat.id
    auth_response = requests.get(f"http://localhost:8082/api/v1/orders/{chat_id}")
    if auth_response.status_code == 200:
        await callback.message.edit_text("Успешно!", reply_markup=kb.Reg)
    else : await callback.message.edit_text("Вы не зарегистрированы \nВведите /register для регистрации")
#Auth check stop

#Register start
@router.message(Command('register'))
async def register(message: Message, state: FSMContext):
    await state.set_state(Register.Email)
    await message.answer('Для регистрации введите почту для кода подтверждения')

@router.message(Register.Email)
async def register_email(message: Message, state: FSMContext):
    await state.update_data(Email=message.text)
    await state.set_state(Register.Code)
    data = await state.get_data()
    await message.answer(f'Введите код подтверждения с почты \n\n{data["Email"]}')

@router.message(Register.Code)
async def register_code(message: Message, state: FSMContext):
    await state.update_data(Code=message.text)
    data = await state.get_data()
    if data["Code"] == "0":
        await message.answer(f'Ваши данные: \n{data["Email"]} \n{data["Code"]} \n\nНе забудьте сохранить!', reply_markup=kb.Reg)
        chat_id = message.chat.id
        user_details = {"email": data["Email"], "chat_id": chat_id}
        response = requests.post("http://localhost:8082/api/v1/users", json=user_details)
        await state.clear()
    else : await message.answer("Введен неверный код подтверждения, повторите регистрацию")
#Register stop

#Menu start
@router.callback_query(F.data == 'Main_menu')
async def main_menu(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Это меню, потом распишу, aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', reply_markup=kb.main)

@router.callback_query(F.data == 'Calc_menu')
async def calc_menu(callback: CallbackQuery):
    await callback.answer('')
    chat_id = callback.message.chat.id
    order_response = requests.get(f"http://localhost:8082/api/v1/orders/{chat_id}")
    orders = ''
    orderslist = []

    if len(order_response.text) > 2:
        for order in order_response.json():
            orderslist.append(order)

    i = 1
    full_price = 0
    for order in orderslist:
        full_price = (float(order["buyPrice"]) * float(order["quantity"])) + full_price
        orders += f'{i}.    {order["name"]}\n       Количество: {order["quantity"]}\n       Средняя цена: {order["buyPrice"]}\n\n'
        i += 1

    await callback.message.edit_text(f'Общая цена портфеля: {full_price}\n\nСодержимое вашего портфеля: \n\n{orders}', reply_markup=kb.Calc)
#Menu stop

#Add Item Start
@router.callback_query(F.data == 'Add_item')
async def calc_add_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Введите название предмета', reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddItem.ItemName)

@router.message(AddItem.ItemName)
async def add_item_name(message: Message, state: FSMContext):
    await state.update_data(ItemName=message.text)
    await state.set_state(AddItem.ItemAmount)
    await message.answer('Введите количество предметов')

@router.message(AddItem.ItemAmount)
async def add_item_amount(message: Message, state: FSMContext):
    await state.update_data(ItemAmount=message.text)
    await state.set_state(AddItem.ItemPrice)
    await message.answer('Введите цену покупки')

@router.message(AddItem.ItemPrice)
async def add_item_price(message: Message, state: FSMContext):
    await state.update_data(ItemPrice=message.text)
    item_data = await state.get_data()
    await message.answer(f'Добавлено в портфель: \nНазвание: {item_data["ItemName"]}'
                         f'\nКоличество: {item_data["ItemAmount"]}'
                         f'\nЦена покупки: {item_data["ItemPrice"]}', reply_markup=kb.Calc_back)
    chat_id = message.chat.id
    order_details = {"name": item_data["ItemName"],"quantity": item_data["ItemAmount"],"buy_price": item_data["ItemPrice"], "chat_id": chat_id}
    response = requests.post("http://localhost:8082/api/v1/orders", json=order_details)
    await state.clear()
#Add Item Stop

#Remove Item Start
@router.callback_query(F.data == 'Remove_item')
async def calc_remove_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Введите название предмета', reply_markup=ReplyKeyboardRemove())
    await state.set_state(RemoveItem.ItemName)

@router.message(RemoveItem.ItemName)
async def remove_item_name(message: Message, state: FSMContext):
    await state.update_data(ItemName=message.text)
    await state.set_state(RemoveItem.ItemAmount)
    await message.answer('Введите количество предметов')

@router.message(RemoveItem.ItemAmount)
async def remove_item_amount(message: Message, state: FSMContext):
    await state.update_data(ItemAmount=message.text)
    item_data = await state.get_data()
    chat_id = message.chat.id
    await message.answer(f'Удалено из портфеля: \nНазвание: {item_data["ItemName"]}'
                         f'\nКоличество: {item_data["ItemAmount"]}', reply_markup=kb.Calc_back)
    order_details = {"name": item_data["ItemName"], "quantity": item_data["ItemAmount"],  "chat_id": chat_id}
    order_delete = requests.delete("http://localhost:8082/api/v1/orders", json=order_details)
    await state.clear()
#Remove item stop

#Update item data start
@router.callback_query(F.data == 'Update_item')
async def calc_update_item(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.answer('Введите название предмета, данные которого хотите изменить', reply_markup=ReplyKeyboardRemove())
    await state.set_state(UpdateItem.ItemName)

@router.message(UpdateItem.ItemName)
async def update_item_name(message: Message, state: FSMContext):
    await state.update_data(ItemName=message.text)
    orders = get_orders(message.chat.id)
    check_data = await state.get_data()

    try:
        print(orders[check_data["ItemName"]])
        await state.set_state(UpdateItem.ItemAmount)
        await message.answer('Введите новое количество предметов')
    except KeyError:
        await state.set_state(UpdateItem.ItemName)
        await message.answer("Введенного предмета не обнаружено, введите заново")

@router.message(UpdateItem.ItemAmount)
async def update_item_amount(message: Message, state: FSMContext):
    await state.update_data(ItemAmount=message.text)
    await state.set_state(UpdateItem.ItemPrice)
    await message.answer('Введите новую цену покупки')

@router.message(UpdateItem.ItemPrice)
async def update_item_price(message: Message, state: FSMContext):
    await state.update_data(ItemPrice=message.text)
    update_data = await state.get_data()
    chat_id = message.chat.id
    await message.answer(f'Данные обновлены в портфеле: \nНазвание: {update_data["ItemName"]}'
                         f'\nКоличество: {update_data["ItemAmount"]}'
                         f'\nЦена покупки: {update_data["ItemPrice"]}', reply_markup=kb.Calc_back)
    order_details = {"name": update_data["ItemName"], "quantity": update_data["ItemAmount"], "buy_price": update_data["ItemPrice"],"chat_id": chat_id}
    order_update = requests.patch("http://localhost:8082/api/v1/orders", json=order_details)
    await state.clear()
#Update item data stop

#Price update start
@router.callback_query(F.data == 'Price_update')
async def price_update(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Цены обновлены', reply_markup=kb.Calc_back)
#Price update stop

#Settings start
@router.callback_query(F.data == 'Settings')
async def settings(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Выберите нужную категорию:', reply_markup=kb.Settings)
#Settings stop

#Currency start
@router.callback_query(F.data == 'Currency')
async def currency(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Курс доллара в стим на сегодня = много рублей', reply_markup=kb.main_back)
#Currency stop

#test
@router.callback_query(F.data == 'Test')
async def test(callback: CallbackQuery):
    await callback.answer('')