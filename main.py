from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import message, reply_keyboard
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.helper import Helper, HelperMode, ListItem
from cgitb import text
import logging, sqlite3, aiogram, datetime, asyncio, random, keyboard

# sosi xui

db = sqlite3.connect("baza.db")
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users (
user INT,
events TEXT
)""")
db.commit()

bot = Bot(token='5428307171:AAEDLW3LbtefPwNezErwG_bxtodXGxuxoPM')

dp = Dispatcher(bot, storage=MemoryStorage())

cb = CallbackData("id", "text")


class N_Start(StatesGroup):
    nik_st = State()


@dp.message_handler(Command("start"), state=None)
async def welcome(message):
    if message.from_user.id == message.chat.id:
        sql.execute(f"SELECT * FROM users WHERE user = {message.from_user.id}")
        if sql.fetchone() is None:
            sql.execute(f"INSERT INTO users VALUES (?,?)", (message.from_user.id, 'None'))
            db.commit()
        else:
            await message.answer(f"привет, {message.from_user.first_name}, это events bot", reply_markup=keyboard.start, parse_mode='Markdown')
    elif message.from_user.id != message.chat.id:
        sql.execute(f"SELECT * FROM users WHERE user = {message.from_user.id}")
        if sql.fetchone() is None:
            await message.reply("похоже что ты не зарегестрирован в events bot\nнапиши /start в личные сообщения боту")
        else:
            await message.answer(f"привет, {message.from_user.first_name}, я events bot",parse_mode='Markdown')

@dp.message_handler(content_types=['text'])
async def main(message : types.Message):
    if message.text == 'ивенты':
        for i in sql.execute(f"SELECT events FROM users WHERE user = {message.from_user.id}"):
            some_events = i
            if sql.fetchone() != None:
                await message.answer(f"привет, {message.from_user.first_name}, твои ивенты {some_events}", reply_markup=keyboard.events_func, parse_mode='Markdown')
            else:
                await message.answer(f"привет, {message.from_user.first_name}, у тебя нету активных ивентов", reply_markup=keyboard.events_func, parse_mode='Markdown')
    if message.text == 'settings':
        await message.answer(f"{message.from_user.first_name}, настройки", reply_markup=keyboard.settings, parse_mode='Markdown')
    if message.text == 'back to menu':
        await message.answer(f"привет, {message.from_user.first_name}, я events bot", reply_markup=keyboard.start, parse_mode='Markdown')
if __name__ == '__main__':
    executor.start_polling(dp)
