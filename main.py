from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.utils.exceptions import TelegramAPIError
from dotenv import load_dotenv
import os
from chatgpt import generate_task_for_ai, analyze_task


load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
LOCATIONS = int(os.getenv("LOCATIONS_NUM"))
CHECK_LISTS = int(os.getenv("CHECK_LISTS_NUM"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UserChecklist(StatesGroup):
    location_selection = State()
    checklist_entry = State()
    comment_input = State()
    photo_upload = State()


@dp.message_handler(commands=["start"], state="*")
async def start_checklist(message: types.Message):
    """
        Handles the '/start' command and starts the checklist process.

        Args:
            message (types.Message): The incoming message object.
        """
    await message.reply("Let's start the checklist. Please select a location:")
    await list_locations(message)


async def list_locations(message: types.Message):
    """
        Lists the available locations for the checklist.

        Args:
            message (types.Message): The incoming message object.
        """
    await UserChecklist.location_selection.set()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    locations = [f"Location {i + 1}" for i in range(0, LOCATIONS)]
    keyboard.add(*locations)
    await message.answer("Choose a location:", reply_markup=keyboard)


@dp.message_handler(state=UserChecklist.location_selection)
async def process_location(message: types.Message, state: FSMContext):
    """
       Processes the selected location and updates the state.

       Args:
           message (types.Message): The incoming message object.
           state (FSMContext): The current state of the conversation.
       """
    await state.update_data(chosen_location=message.text)
    await message.answer(f"You have selected: {message.text}", reply_markup=ReplyKeyboardRemove())
    await UserChecklist.checklist_entry.set()
    await start_checklist_process(message, state)


async def start_checklist_process(message: types.Message, state: FSMContext):
    """
       Starts the checklist process and presents the first entry.

       Args:
           message (types.Message): The incoming message object.
           state (FSMContext): The current state of the conversation.
       """
    await message.answer("Starting the checklist process. Please answer each entry.")
    await process_checklist_entry(message, state, 1)


async def process_checklist_entry(message: types.Message, state: FSMContext, entry_number: int):
    """
        Presents the current checklist entry and updates the state.

        Args:
            message (types.Message): The incoming message object.
            state (FSMContext): The current state of the conversation.
            entry_number (int): The number of the current checklist entry.
        """
    await state.update_data(current_entry=entry_number)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("All clear", "Leave a comment")
    await message.answer(f"Checklist entry {entry_number}: Is everything clear?", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text in ["All clear", "Leave a comment"],
                    state=UserChecklist.checklist_entry)
async def check_clearance(message: types.Message, state: FSMContext):
    """
        Handles the user's response to the checklist entry.

        Args:
            message (types.Message): The incoming message object.
            state (FSMContext): The current state of the conversation.
        """
    user_data = await state.get_data()
    entry_number = user_data["current_entry"]
    if message.text == "Leave a comment":
        await UserChecklist.comment_input.set()
        await message.answer(f"Please provide a comment for entry {entry_number}:")
    else:
        if entry_number < CHECK_LISTS:
            await process_checklist_entry(message, state, entry_number + 1)
        else:
            await finalize_checklist(message, state)


@dp.message_handler(state=UserChecklist.comment_input)
async def process_comment(message: types.Message, state: FSMContext):
    """
        Processes the user's comment and updates the state.

        Args:
            message (types.Message): The incoming message object.
            state (FSMContext): The current state of the conversation.
        """
    user_data = await state.get_data()
    entry_number = user_data["current_entry"]
    await state.update_data({f"comment_entry_{entry_number}": message.text})
    await UserChecklist.photo_upload.set()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("/Skip")
    await message.answer(
        f"Please upload a photo related to your comment for entry {entry_number}, or skip to continue without one.",
        reply_markup=keyboard)


