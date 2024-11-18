from aiogram.filters import callback_data
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Калькулятор', callback_data='Calc_menu')],
                                      [InlineKeyboardButton(text='Курс валют', callback_data='Currency'),
                                      InlineKeyboardButton(text='Настройки', callback_data='Settings')]])
main_back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад в меню', callback_data='Main_menu')]])

Reg_check = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Авторизоваться", callback_data='Auth_check')]])
Reg = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Продолжить!', callback_data='Main_menu')]])

Calc = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Добавить предмет', callback_data='Add_item'),
                                      InlineKeyboardButton(text='Удалить предмет', callback_data='Remove_item')],
                                      [InlineKeyboardButton(text='Обновить данные предмета', callback_data='Update_item')],
                                      [InlineKeyboardButton(text='TEST', callback_data='Test')],
                                      [InlineKeyboardButton(text='Назад', callback_data='Main_menu')]])

Calc_back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад в портфель', callback_data='Calc_menu')]])

Settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='1', callback_data='1'),
                                                  InlineKeyboardButton(text='2', callback_data='2'),
                                                  InlineKeyboardButton(text='3', callback_data='3')],
                                                 [InlineKeyboardButton(text='Назад', callback_data='Main_menu')]])

#Skip = InlineKeyboardMarkup(InlineKeyboardButton=[[InlineKeyboardButton(text='Пропустить', callback_data='Main_menu')]])

