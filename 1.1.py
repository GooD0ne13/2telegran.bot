import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

conn = sqlite3.connect('items.db')
cursor = conn.cursor()
cursor.execute('''
    DELETE FROM items WHERE name_item='/to_order';            
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name_item TEXT NOT NULL,
        value TEXT,
        description_item TEXT,
        price TEXT,
        photo TEXT
    )
''')

# cursor.execute('''
#     INSERT INTO items VALUES (4, 'Alchemist','1 шт.','Taur Rider, 2023 Collector Cache','250грн','https://static.wikia.nocookie.net/dota2_gamepedia/images/e/eb/Cosmetic_icon_Taur_Rider.png/revision/latest/scale-to-width-down/170?cb=20230831083724')
# ''')
# cursor.execute('''
#     INSERT INTO items VALUES (5, 'Wraith king','3 шт.','Tyrant of the Veil, 2023 Collector Cache','300грн','https://static.wikia.nocookie.net/dota2_gamepedia/images/3/36/Cosmetic_icon_Tyrant_of_the_Veil.png/revision/latest/scale-to-width-down/170?cb=20230831083743')
# ''')


TOKEN = '6092997901:AAGcBk3xANasOYyxUbeRJc-_nTl2CfgaYJs'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
ADMINS = [978676961]
# 872537831
# 828332097
# 978676961
# 816042478
async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустити бота'),
            types.BotCommand('item_shop', 'Магазин придметів'),
            types.BotCommand('to_order', 'Замовити'),
            types.BotCommand('add_item', 'Додати новий придмет.')
        ]
    )

# @dp.message_handler(commands='comands')
# async def comands(message: types.Message):
#     comand_choice = InlineKeyboardMarkup()

#     await message.answer(text='Всі команди:/start(Відкрити магазин)/to_order(Заказати придмет)/add_item(Додати придмет).', reply_markup=comand_choice)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    button1 = types.KeyboardButton("/add_item")
    button2 = types.KeyboardButton("/to_order")
    button3 = types.KeyboardButton("/item_shop")
    keyboard.add(button1, button2, button3)

    await message.answer("Привіт, виберіть дію:", reply_markup=keyboard)


@dp.message_handler(commands='to_order')
async def order(message: types.Message):
    await message.answer(text='Чудово для допомоги в покупці напиши мені в телеграм @Andri4ik, та не забудь додати в стім для обміну; steam:1478803177.')


@dp.message_handler(commands='item_shop')
async def comands(message: types.Message):
    items_choice = InlineKeyboardMarkup()
    cursor.execute('SELECT name_item FROM items')
    items_data = cursor.fetchall()
    
    for item_data in items_data:
        item_name = item_data[0]
        button = InlineKeyboardButton(text=item_name, callback_data=item_name)
        items_choice.add(button)
    
    await message.answer(text='Привіт! Це магазин придметів з гри Dota 2. Вибери придмет який хочеш оглянути.', reply_markup=items_choice)

@dp.callback_query_handler()
async def get_item_info(callback_query: types.CallbackQuery):
    cursor.execute(f"""SELECT value, description_item, price, photo FROM items WHERE name_item = '{callback_query.data}'""")
    item_data = cursor.fetchone()

    if item_data:
        value, item_description, item_price, photo = item_data
        await bot.send_photo(callback_query.message.chat.id, photo)
        
        message = f"<b>Item value:</b> {value}\n\n<b>About:</b> {item_description}\n\n<b>Price:</b> {item_price}"
        
        await bot.send_message(callback_query.message.chat.id, message, parse_mode='html')
    else:
        await bot.send_message(callback_query.message.chat.id, 'Нажаль придмет не знайдено')

@dp.message_handler(commands='add_item')
async def add_new_film(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in ADMINS:
        await message.answer(text='Введи назву героя якого хочеш додати.')
        await state.set_state('item_name')
    else:
        await message.answer(text='Не достатньо прав.')

@dp.message_handler(state='item_name')
async def item_name(message: types.Message, state: FSMContext):
    item_name = message.text
    
    await state.update_data(item_name=item_name)
    await message.answer(text='Тепер введи кількість шт. цього придмета')
    await state.set_state('item_value')

@dp.message_handler(state='item_value')
async def item_value(message: types.Message, state: FSMContext):
    item_value = message.text
    await state.update_data(item_value=item_value)
    await message.answer(text='Тепер напиши назву скрині звідки цей придмет.')
    await state.set_state('item_description')

@dp.message_handler(state='item_description')
async def item_description(message: types.Message, state: FSMContext):
    item_description = message.text
    await state.update_data(item_description=item_description)
    await message.answer(text='Тепер напиши ціну придмета')
    await state.set_state('item_price')

@dp.message_handler(state='item_price')
async def item_price(message: types.Message, state: FSMContext):
    item_price = message.text
    await state.update_data(item_price=item_price) 
    await message.answer(text='Тепер кинь посилання на фото придмета(краще з сайту https://dota2.fandom.com/wiki/August_2023_Collector%27s_Cache).')
    await state.set_state('item_photo')

@dp.message_handler(state='item_photo')
async def item_photo(message: types.Message, state: FSMContext):
    item_photo = message.text
    
    item_name = await state.get_data()
    item_value = await state.get_data()
    item_description = await state.get_data()
    item_price = await state.get_data()
    item_name = item_name['item_name']
    item_value = item_value['item_value']
    item_description = item_description['item_description']
    item_price = item_price['item_price']

    cursor.execute('''
        INSERT INTO items (name_item, value, description_item, price, photo)
        VALUES (?, ?, ?, ?, ?)
    ''', (item_name, item_value, item_description, item_price, item_photo))

    conn.commit()
    
    await state.finish()
    await message.answer(text='Вітаю новий придмет додано до списку.')

async def on_shutdown(dp):
    conn.close()

async def on_startup(dp):
    await set_default_commands(dp)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
