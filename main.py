import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router

# TODO Ввести версионирование программы бота и добавить файл RELEASE_NOTES.md,
#  в котором будут помечаться изменения для каждой версии программы
async def main():
    bot = Bot(token='6378994275:AAE4XgwR1sBdr2r6Q0JxAt6nqv4rcwNl5Ik')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot OFF")
