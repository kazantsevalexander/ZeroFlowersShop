import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# Настройки бота
API_TOKEN = '7621395982:AAEBUp892ayfVzC0o0ZZJcwOvUtjJCiRVDo'
ADMIN_CHAT_ID = '6618330710'

# Создание экземпляра бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: Message):
    await message.reply("Привет! Я бот доставки цветов. Используй /help для просмотра команд.")

@dp.message(Command("help"))
async def send_help(message: Message):
    await message.reply("Вот что я умею:\n/start - начать общение\n/help - показать это сообщение.")

async def main():
    # Запуск диспетчера
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())