from aiogram import types
from aiogram.types import FSInputFile
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Router
from datetime import datetime
from config import API_TOKEN
import sql_lite

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
async def cmd_start(message: types.Message):
    user = await sql_lite.get_user(message.chat.id)
    if user == []:
        await sql_lite.create_user(message.chat.id)
    await message.answer("Бот запущен. Вы будете получать изображения каждые 20 секунд.")


async def on_startup():
    await sql_lite.db_connect()
    scheduler.add_job(send_daily_image, 'interval', seconds=20, start_date=datetime.now())
    scheduler.start()
    print('Successful db connect ✅')


async def start():
    await on_startup()
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)
