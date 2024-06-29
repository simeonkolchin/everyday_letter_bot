from aiogram import types
from aiogram.types import FSInputFile
from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Router
from datetime import datetime
from config import API_TOKEN
import sql_lite
import pytz

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
scheduler = AsyncIOScheduler()


async def send_daily_image():
    users = await sql_lite.get_users()
    for user_id in users:
        user = await sql_lite.get_user(user_id[0])
        if user == []:
            continue

        count = list(map(int, user[0][1].split()))
        if count[-1] < 43:
            with open(f'../data/texts/{count[-1]}.txt', 'r') as text:
                await bot.send_photo(chat_id=user_id[0], photo=FSInputFile(f'../data/images/{count[-1]}.png'), caption=text.read(),
                                     parse_mode='HTML')
                await sql_lite.update_user(user_id[0], user[0][1], count[-1] + 1)


@router.message(CommandStart())
async def cmd_start(message: types.Message, bot: Bot):
    print(message.chat.id)
    user = await sql_lite.get_user(message.chat.id)
    if user == []:
        await sql_lite.create_user(message.chat.id)
    await message.answer(f"Бот запущен")
    await bot.send_message(chat_id=993699116, text=f"@{message.from_user.username} запустил(а) бота!")


@router.message(Command("send_"))
async def cmd_start(message: types.Message, bot: Bot):
    await send_daily_image()

async def on_startup():
    await sql_lite.db_connect()
    scheduler.add_job(send_daily_image, 'interval', days=1, start_date=datetime.now(pytz.timezone('Europe/Moscow')).replace(hour=11, minute=0, second=0))
    scheduler.start()
    print('Successful db connect ✅')


async def start():
    await on_startup()
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)
