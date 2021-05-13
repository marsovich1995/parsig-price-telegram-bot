import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlighter import SQLighter
from conf import token_
from get import chek_url, get_data_serch, get_similar_value, get_id_by_url, get_exact_book, check_text

db = SQLighter('db.db') # Подключение к Базе

bot = Bot(token = token_)
dp = Dispatcher(bot)

loop = asyncio.get_event_loop()

inline_btn_1 = InlineKeyboardButton('Нет', callback_data='cancel_1')
inline_btn_2 = InlineKeyboardButton('Да', callback_data='subsc_2')
inline_kb1 = InlineKeyboardMarkup(row_width=2).add(inline_btn_1,inline_btn_2)

@dp.callback_query_handler(lambda c: c.data)
async def process_callback_button1(callback_query: types.CallbackQuery):

    code = callback_query.data[-1] # использовать последний символ
    if code.isdigit():
        code = int(code)
    last_message_id = db.get_last_message_id(callback_query.from_user.id) #Сравнить текущий message_id с послденим из бызы 	
    if code == 2 and last_message_id == callback_query.message.reply_to_message.message_id: #Да
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, '\U00002705') #Галка
        db.update_subscription_book_id(callback_query.from_user.id) 
        db.update_subscription(callback_query.from_user.id,True) #Активация подписки

    elif code == 1: #Нет
        
        await bot.answer_callback_query(callback_query.id)

    else:
        await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands=['start'])
async def subscribe(message: types.Message):
    if(not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    await message.answer("Бот отслеживает изменение цены на сайте Читай Город,\nпришлите ссылку активации оповещения `chitai-gorod.ru/catalog/book/***`",parse_mode= 'Markdown')

@dp.message_handler(commands=['stop'])
async def unsubscribe(message: types.Message):
    if(not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")


def answer_search(message, i, data_json ):

    if isinstance(i,int):
        db.update_subscription_last_request(message.from_user.id,data_json['hits']['hits'][i]['_source']['book_id'],message.message_id ) #запоминает в БД последний запрос и id message
        return message.reply('Получать оповещения об изменении цены\n*' + \
                data_json['hits']['hits'][i]['_source']['name'] + '*?', parse_mode= 'Markdown', reply_markup=inline_kb1)    
    else:
        return message.reply('Совпадений не найдено')         
        
@dp.message_handler()
async def echo(message: types.Message):
    text = message.text
    type_text = check_text(text)
    if type_text == 'url':
        if chek_url(text):
            url = chek_url(text,True)
            try:
                id_book = str(get_id_by_url(url)) #get id by url
                data_json = get_data_serch(id_book)
                i = get_exact_book(data_json,id_book)
                await answer_search(message, i,data_json)
            except:
                await message.reply('Что-то пошло не так, поробуйте другой способ') 
                print('get_id_by_url  error ') #ошибка получить idbook
        else:
            await message.reply('Этот URL не подходит') 
    elif type_text == 'id_book':            
        data_json = get_data_serch(text) #id_book = text
        i = get_exact_book(data_json,text)
        await answer_search(message, i,data_json)     
    else:
        if len(text) < 50:
            data_json = get_data_serch(text)
            i = get_similar_value(data_json,text)
            await answer_search(message, i,data_json)
        else:
            await message.reply('Слишком длиное название')




    # if chek_url(text) == 2: # url распозднан но не входит в число допутимых
    #     await message.reply('Неправильный url')
    # elif len(text) < 50:   # если длина меньше 50 символов     
    #     if chek_url(text): # url распозднан и входит в число допутимых
    #         url = chek_url(text,True) # Возвращает общий url вида https://www.chitai-gorod.ru/catalog/book/0000000/'
    #         try:
    #             text = str(get_id_by_url(url)) #get id by url
    #         except: 
    #             print('get_id_by_url  error ')
    #             # await message.reply('Поиск не дал результатов, попробуйте другой способ')
    #     data_json = get_data_serch(text) #Поиск через API по гаванию или id_book
    #     if data_json['_shards']['successful'] == 1 and data_json['hits']['total']['value'] == 1: #Если успешно и только один результат 

    #         await message.reply('Получать оповещения об изменении цены\n*' + data_json['hits']['hits'][0]['_source']['name'] + '*?', parse_mode= 'Markdown', reply_markup=inline_kb1)
    #         db.update_subscription_last_request(message.from_user.id,data_json['hits']['hits'][0]['_source']['book_id'],message.message_id ) #запоминает в БД последний запрос и id message

    #     elif data_json['_shards']['successful'] == 1 and data_json['hits']['total']['value'] > 1: #Если успешно и только несколько результататов

    #         a = get_similar_value(data_json,text) #Находим индекс наиболее подходяшего результата

    #         if isinstance(a,int): #Если индекс целое
    #             await message.reply('Получать оповещения об изменении цены\n*' + data_json['hits']['hits'][a]['_source']['name'] + '*?', parse_mode= 'Markdown', reply_markup=inline_kb1)
    #             db.update_subscription_last_request(message.from_user.id,data_json['hits']['hits'][a]['_source']['book_id'],message.message_id ) 
    #         else:
    #             await message.reply('Поиск не дал результатов, попробуйте другой способ')  
                    
    #     else:
    #         await message.reply('Поиск не дал результатов, попробуйте другой способ')  

    # else:
    #     await message.reply('Слишком длиное название')

async def parsing(wait_for):

    while True:
        await asyncio.sleep(wait_for)  # жать вызова      
        subscriptions = db.get_subscriptions() #получить список активных подписчиков
        for s in subscriptions:                #('332**1826', 0, 1, 2843543, None, 2843543, 568)
            # print(s)
            try:
                new_data = get_data_serch(s[3])  # получить данные по id_book
                i = get_exact_book(new_data,s[3]) # получить индекс с точным совбадением id book
                if isinstance(i,int): #если найден
                    new_price = int(new_data['hits']['hits'][i]['_source']['price'])  # Запомнить новую Цену              
                    if s[4] != new_price: # Если цена изменилась то оповестить пользователя
                        print('Udate price')
                        db.update_subscription_price(s[0],new_price) #обновать цену в БД
                        db.add_message_count(s[0]) #Увеличить счетчик сообщений
                        await bot.send_message(
                            s[0],
                            str(new_data['hits']['hits'][i]['_source']['name'] +'\nНовая цена: *' + str(new_price) + ' руб.*'),
                            parse_mode= 'Markdown'
                        )
                    else:
                        print('next user')     
                else:
                    print("ошибка поиска")
            except:
                print('ошибка запроса')        


if __name__ == '__main__':
    loop.create_task(parsing(20))
    executor.start_polling(dp, skip_updates=True)
