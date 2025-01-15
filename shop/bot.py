from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Настройки бота
API_TOKEN = '7621395982:AAEBUp892ayfVzC0o0ZZJcwOvUtjJCiRVDo'
ADMIN_CHAT_ID = '6618330710'

# Создание экземпляра бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для уведомлений о заказах.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
