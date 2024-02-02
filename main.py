from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils import executor
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
LOCATIONS = 5

class UserChecklist(StatesGroup):
    location_selection = State()
    checklist_entry = State()
    comment_input = State()
    photo_upload = State()


@dp.message_handler(commands=["start"], state="*")
async def start_checklist(message: types.Message):
    await UserChecklist.location_selection.set()
    await message.reply("Let's start the checklist. Please select a location:")
    await list_locations(message)

async def list_locations(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    locations = [f"Location {i + 1}" for i in range(0, LOCATIONS)]
    keyboard.add(*locations)
    await message.answer("Choose a location:", reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
