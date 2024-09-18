import asyncio
import os
import logging
import sys

from dotenv import load_dotenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from api_functions import get_city_id, get_vacancies

load_dotenv()

form_router = Router()

class Form(StatesGroup):
    city = State()
    vacancy = State()
    amount = State()


@form_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.city)
    await message.answer(
        "🏙️Введите город, либо выберите из предложенных",
                reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Минск"),
                    KeyboardButton(text="Брест"),
                    KeyboardButton(text="Витебск"),
                ],
                [
                    KeyboardButton(text="Гродно"),
                    KeyboardButton(text="Гомель"),
                    KeyboardButton(text="Могилёв"),
                ]
            ]
        ,resize_keyboard=True),    
    )

@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer(
        "❌Отмена",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.city)
async def process_city(message: Message, state: FSMContext) -> None:
    city = await get_city_id(message.text)
    await state.update_data(city=city)
    await state.set_state(Form.vacancy)

    await message.answer(
        "👨‍🏭Отлично, а теперь напиши вакансию, в которой заинтересован. ",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.vacancy)
async def process_vacancy(message: Message, state: FSMContext) -> None:
    data = await state.update_data(vacancy=message.text)
    await state.set_state(Form.amount)

    await message.answer(
        "Количество вакансий(до 100)",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="1"),
                    KeyboardButton(text="5"),
                    KeyboardButton(text="10"),
                ],

            ],resize_keyboard=True
        )
    )

@form_router.message(Form.amount)
async def process_place(message: Message, state: FSMContext) -> None:
    data = await state.update_data(amount=message.text)
    await state.clear()
    await show_vacancy(message=message, data=data)


async def show_vacancy(message: Message, data: Dict[str, Any]) -> None:

    city = int(data["city"])
    vacancy = data["vacancy"]
    amount = int(data["amount"])

    text = await get_vacancies(city, vacancy, amount)

    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())

async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
