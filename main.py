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


@dp.message_handler(commands=["Skip"], state=UserChecklist.photo_upload)
async def skip_photo(message: types.Message, state: FSMContext):
    """
       Skips the photo upload and continues with the checklist.

       Args:
           message (types.Message): The incoming message object.
           state (FSMContext): The current state of the conversation.
       """
    await UserChecklist.checklist_entry.set()
    await message.answer("Skipping photo upload. Continuing with the checklist.")
    await process_checklist_entry(message, state, (await state.get_data()).get("current_entry", 1) + 1)


@dp.message_handler(content_types=["photo"], state=UserChecklist.photo_upload)
async def process_photo(message: types.Message, state: FSMContext):
    """
        Processes the uploaded photo and updates the state.

        Args:
            message (types.Message): The incoming message object.
            state (FSMContext): The current state of the conversation.
        """
    try:
        photo_file = await bot.get_file(message.photo[-1].file_id)
        photo_url = f"https://api.telegram.org/file/bot{os.getenv('BOT_TOKEN')}/{photo_file.file_path}"
        user_data = await state.get_data()
        entry_number = user_data["current_entry"]
        await state.update_data({f"photo_entry_{entry_number}": photo_url})
        await UserChecklist.checklist_entry.set()
        await message.answer("Photo uploaded successfully. Continuing with the checklist.")
        await process_checklist_entry(message, state, entry_number + 1)
    except TelegramAPIError:
        await message.reply("There was an issue with the Telegram API. Please try again.")
    except FileNotFoundError:
        await message.reply("The photo file was not found. Please try again.")


async def finalize_checklist(message: types.Message, state: FSMContext):
    """
        Finalizes the checklist process and performs any necessary cleanup.

        Args:
            message (types.Message): The incoming message object.
            state (FSMContext): The current state of the conversation.
        """
    await message.answer("Checklist completed. Thank you for your input.")
    user_data = await state.get_data()
    report = generate_task_for_ai(user_data)
    photos = {f"check list {i + 1}": user_data.get(f"photo_entry_{i + 1}")
              for i in range(CHECK_LISTS)
              if f"photo_entry_{i + 1}" in user_data}
    finish_report = await analyze_task(report, photos=photos)
    if finish_report:
        await message.answer("Answer: " + finish_report)
    else:
        await message.answer("The report could not be parsed.")
    await state.finish()
    await list_locations(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
