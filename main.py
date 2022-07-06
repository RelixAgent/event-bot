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
from random import randint


db = sqlite3.connect("baza.db")
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS events (
id INTEGER PRIMARY KEY AUTOINCREMENT,
open INT,
name TEXT,
time TEXT,
comment TEXT,
place TEXT
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS users (
user INT,
events TEXT
)""")
db.commit()

bot = Bot(token='5428307171:AAEDLW3LbtefPwNezErwG_bxtodXGxuxoPM')

dp = Dispatcher(bot, storage=MemoryStorage())

cb = CallbackData("id", "text")


class CreateEvent(StatesGroup):
    event = State()
    time = State()
    place = State()
    comment = State()




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


@dp.message_handler(state=CreateEvent.event)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        global e_name
        e_name = message.text
        await state.finish()
        await message.answer("Напиши время, когда начнётся ивент")
        await CreateEvent.time.set()

@dp.message_handler(state=CreateEvent.time)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        global e_time
        e_time = message.text
        await state.finish()
        await message.answer("Где будет проиходить ивент?")
        await CreateEvent.place.set()

@dp.message_handler(state=CreateEvent.place)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        global e_place
        e_place = message.text
        await state.finish()
        await message.answer("Напиши комментарий к ивенту")
        await CreateEvent.comment.set()

@dp.message_handler(state=CreateEvent.comment)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        global e_place
        global e_name
        global e_time
        e_id = randint(0, 9999)
        e_comment = message.text
        await state.finish()
        message.answer("Ивент создан")
        sql.execute(f"INSERT INTO events VALUES ({e_id}, {1}, ?,?,?,?)", (e_name, e_time, e_comment, e_place))
        db.commit()


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

    if message.text == "Создать ивент":
        await message.answer("Хорошо, напиши название ивента")
        await CreateEvent.event.set()


if __name__ == '__main__':
    executor.start_polling(dp)

