import asyncio
import os
from datetime import datetime
import aiohttp
import pymongo
from aiogram import Bot, Dispatcher, executor, types
from pymongo.errors import DuplicateKeyError, ConnectionFailure

TOKEN = os.environ['TOKEN']
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

url = 'https://coinpay.org.ua/api/v1/exchange_rate'

cluster = pymongo.MongoClient(
    'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' +
    os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']
)
db = cluster.bot_coinpay
coll = db.users


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    create_user(message)

    hello = \
        """
    
Telegram Bot, which allows you to track a certain exchange rate on Coinpay.
For start tracking, you need to enter the pair of currencies and the time interval in seconds with separator @
Example: 

    BTC_USDT @ 60

To view available pairs, send /get_pairs
For stop tracking - send /stop
    
        """
    await message.reply(hello)


@dp.message_handler(commands=['get_pairs'])
async def get_available_pairs(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            pairs = []
            for pair in data['rates']:
                pairs.append(pair['pair'])
            await message.answer(str(pairs))
            return pairs


@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
    # Clean flag variables stored in DB
    coll.update_one({'_id': message.chat.id}, {'$set': {'user_pair': '', 'user_timer': ''}})
    await message.answer('You entered the /stop command. Submit a new request to continue tracking')


@dp.message_handler(regexp='@')
async def send_price(message: types.Message):
    user_pair = ''
    user_timer = ''
    # check if user_pair and user_timer are set and stored in DB
    if check_user_message(message):
        while True:
            # read user_pair and user_timer from DB
            try:
                user_pair = coll.find_one({"_id": message.chat.id})['user_pair']
                user_timer = coll.find_one({"_id": message.chat.id})['user_timer']
            except ConnectionFailure:
                await message.answer("Lost connection with DB!")
                # Use flag variable stored in DB to stop the loop if needed
            if user_pair:
                price = await get_price(user_pair)
                if price:
                    await message.answer(f"{user_pair.upper()}: {price}")
                    await asyncio.sleep(user_timer)
                else:
                    await message.answer("You entered an invalid pair")
                    break
            else:
                break
        print('Operation canceled')
    else:
        await message.answer('You have entered an invalid request. Try again. For help, send /help')


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer('You have entered an invalid request. Try again. For help, send /help')


def create_user(message) -> None:
    try:
        coll.insert_one({"_id": message.chat.id,
                         "name": message.chat.first_name,
                         "user_pair": '',
                         "user_timer": '',
                         "time": datetime.now()})
    except DuplicateKeyError:
        pass


def check_user_message(message) -> bool:
    try:
        user_pair = message.text.split('@')[0].strip()
        user_timer = int(message.text.split('@')[1].strip())
    except ValueError:
        return False
    print(user_pair, user_timer)
    coll.update_one({'_id': message.chat.id}, {'$set': {'user_pair': user_pair, 'user_timer': user_timer}})
    return True


async def get_price(user_pair) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            for pair in data['rates']:
                if pair['pair'].lower() == user_pair.lower():
                    print(pair['price'])
                    return pair['price']


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
