# file: bot.py
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message

API_TOKEN = '7837639025:AAEdU9Vslw7bTa2W8bpEvRv6mq-bGA4W340'

logging.basicConfig(level=logging.INFO)

# Static conversion rates (USD to others)
RATES = {
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 151.24,
    "CAD": 1.36,
    "AUD": 1.52
}

CURRENCY_BUTTONS = [
    KeyboardButton(text=cur) for cur in RATES.keys()
]

CONVERT_BUTTON = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Convert")]])

class ConvertState(StatesGroup):
    waiting_for_currency = State()
    waiting_for_amount = State()

async def start_handler(message: Message, state: FSMContext):
    await message.answer("Welcome to USD Converter Bot!", reply_markup=CONVERT_BUTTON)

async def convert_handler(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[CURRENCY_BUTTONS])
    await message.answer("Choose one of the currencies to which you wan to convert USD:", reply_markup=keyboard)
    await state.set_state(ConvertState.waiting_for_currency)

async def currency_handler(message: Message, state: FSMContext):
    currency = message.text.upper()
    if currency not in RATES:
        await message.reply("Invalid currency. Please choose from the list.")
        return
    await state.update_data(currency=currency)
    await message.answer("Choose the amount:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ConvertState.waiting_for_amount)

async def amount_handler(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.reply("Please enter a valid number.")
        return

    data = await state.get_data()
    currency = data['currency']
    rate = RATES[currency]
    result = amount * rate

    await message.answer(f"{amount} USD = {result:.2f} {currency}", reply_markup=CONVERT_BUTTON)
    await state.clear()

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.register(start_handler, CommandStart())
    dp.message.register(convert_handler, lambda msg: msg.text == "Convert")
    dp.message.register(currency_handler, StateFilter(ConvertState.waiting_for_currency))
    dp.message.register(amount_handler, StateFilter(ConvertState.waiting_for_amount))

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
