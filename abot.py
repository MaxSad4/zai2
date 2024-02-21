import telebot
import openai
import docxtpl
import json
import asyncio
import aiohttp
import io
from telebot import types
from io import BytesIO
from datetime import datetime
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

now = datetime.now()

from telebot.async_telebot import AsyncTeleBot
#bot = AsyncTeleBot('6974771405:AAGGIcN1mcegxhKBZ_iz1aRyJ7iRdCdEc9A') #Z_test_bot
bot = AsyncTeleBot("6414920520:AAGjTEqeTEtCjK0-rxMoiEzZtxKN6BQzfpU") #ZeppelinAIbot

# Создаем пустой словарь для хранения текстовых сообщений и для фото
doc = DocxTemplate("0411-004-GPT.docx")
text_messages = {}
user_photos = {}

@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
        await bot.reply_to(message, "Привет. Это тестовый бот для создания шаблонов ТЗ на основе текстовых сообщений и фото.")

#add new command to TZ
@bot.message_handler(commands=['tz'])
async def send_welcome(message):
        await bot.reply_to(message, "Это раздел для создания технического задания. Используя клавиатуру или голосовой ввод, опишите свободным текстом что и когда нужно, необходимые материалы, укажите объект, место и время производства работ, контактное лицо, иные особенности. В ответ вы получите файл-шаблон технического задания.")

@bot.message_handler(commands=['go'])
async def echo_all(message):
        global doc
        global user_photos
        await bot.reply_to(message, "Обработка запроса...")
        #creating prompt
        preprompt = "Я направлю тебе текст -- это описание простыми работы простыми словами. На основе этого текста ты формально заполнить форму технического задания на инженерный или строительные работы. Используй четкие формальные технически формулировки. Конкретные пункты будут предложены ниже. Ответ выдай в формате одноуровневого словаря python -- в скобках указаны короткие названия для словаря. Если в тексте перечислены работы разного типа перечисли их в разделе job раздельно, опиши их строгим техническим языком без оценочных суждений. Этот раздел должен содержать только список работ. Раздел (name) должен содержать общее наименование работ. Для раздела date определи точную дату или время или период из текста (это могут быть дни или месяцы), если точно не указано напиши Указать даты проведения работы.Для раздела time определи рабочее время/внерабочее время.Для параметра qlevel выбели один из 4 предложенных вариантов: Низкобюджетные/Высококачественные/Бюджетные/Премиум-класс -- ты сам должен определить уровень из контекста.В параметре material перечисляй только материалы. Для раздела usl определи особенности производства работ. Это может быть: стесненность, помещения заставленные мебелью, постоянный поток людей, высота. Сам не придумывай, указывай только если это понятно из текста.Параметр contact указывай в формате Фамилия Имя Отчество, телефон (если в сообщении нет информации -- не указывай ничего).Если требуется что-то согласовать, опиши это в разделе osob.Проанализируй текст и определи что обязательно должно быть указано точно (например, размеры, площадь, кол-во, точные характеристики) для каждого материала, если этого нет в тексте дай рекомендации составителю задания что конкретно нужно указать в разделе dopinfo отдельными пунктами. в случае нескольких строк используй символ переноса строки '\n' Текст: "        
        postprompt = ""
        # Объединяем все значения из словаря в одну строку с пробелами
        text_combined = ' '.join(text_messages[message.chat.id])
        print(text_combined)
        #openAI request
        openai.api_key = "sk-or-vv-43683aa54ef383f42d3d5063b17ccdf00d8108771cd1051f70b1782d324d6c32"
        openai.base_url = "https://api.vsegpt.ru:6070/v1/"
        prompt = preprompt + text_combined + postprompt
        print(text_combined)
        print(prompt)
        gmodel="openai/gpt-3.5-turbo"
        #gmodel="translate-fireworks/mixtral-8x7b-fw-chat"
        messages = []
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "system", "content": "Отвечай в формате JSON in double quotes вида {'name': Наименование работ, 'obj': Объект или здание с адресом, 'place': Конкретное место проведения работ, 'level': Этаж указать цифрой , 'contact': Имя и телефон контактного лица,'qlevel': Уровень качества выполнения работ,'date': Желаемая дата начала выполнения работ,'job': Перечень планируемых работ и ожидаемый результат,'osob': Особые пожелания,'material': Требования к материалам,'time': Желаемое время производства работ,'usl': 'Соблюдение правил бизнесцентра, заказ пропуска на въезд','pay': Условия оплаты,'dopinfo': Что ты как прфильный специалист рекомендуешь дополнительно уточнить укажи 6 важных позиций, которые помогут выполнить работы более качественно и профессионально} , а в случае нескольких строк используй символ переноса строки '\n' и используй кирилицу"})
        try:
            response_big = openai.chat.completions.create(
                model=gmodel,
                messages=messages,
                temperature=0.5,
                n=1,
                max_tokens=int(len(prompt) * 10),
            )
            response = response_big.choices[0].message.content
            response = json.loads(response)
            response = json.dumps(response)
            print(response)
            #bot.reply_to(message, response)
        except Exception as e:
            await bot.reply_to(message, "Произошла ошибка при обработке запроса: " + str(e))

        #create date
        datetime = "{}{}{}_{}{}{}".format(now.day, now.month, now.year, now.hour, now.minute, now.second)
        print(datetime)
        s = datetime
        s1 = "".join(c for c in s if c.isalnum())
        print(s1)
        
        #create DOCX -- создали выше
        #doc = DocxTemplate("0411-004-GPT.docx")
        context = json.loads(response)

        #дополняем словарь и объединяем
        adddic = {"today": "{}.{}.{}".format(now.day, now.month, now.year)}
        user_id = message.from_user.id
        print(user_photos)
        context = context | adddic | user_photos[user_id]
        
        print(context)

        #заполняем docx шаблон и сохраняем файл
        try:
            doc.render(context)
            filename = "Z_AI_ТЗ_"+s1+".docx"
            doc.save(filename)

            #send file
            doc = open(filename, 'rb')
            await bot.reply_to(message, "Техническое задание -- вы можете переслать файл себе на почту и продложить с ним работать:")
            await bot.send_document(message.chat.id, doc)                        
        except Exception as e1:
            #bot.reply_to(message, "Произошла ошибка при отправке файла: " + str(e1))
            print("Произошла ошибка при отправке файла: " + str(e1))

#collect images
@bot.message_handler(content_types=['photo'])
async def save_photo(message):
        global doc
        global user_photos
        user_id = message.from_user.id
        file_id = message.photo[-1].file_id
        
        if user_id not in user_photos:
            user_photos[user_id] = {}
        
        file_info = await bot.get_file(file_id)

        # Генерируем имя параметра в формате "image1", "image2" и так далее
        param_name = f"image{len(user_photos[user_id]) + 1}"

        # Генерируем уникальное имя файла на основе user_id и file_id
        file_name = f"img/{user_id}_{file_info.file_path.rsplit('/', 1)[-1]}"

        # Скачиваем файл на диск
        downloaded_file = await bot.download_file(file_info.file_path)
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
            print(file_name)
        #await bot.reply_to(message, "Картинка сохранена на диск.")

        image = InlineImage(doc, file_name, width=Mm(120))

        try:
            # Сохраняем информацию о фотографии в словаре
            user_photos[user_id][param_name] = image
            await bot.reply_to(message, f"Фотография сохранена с именем параметра {param_name}. Используйте /go для начала генерации ТЗ на основе ранее указанных данных.")
        except Exception as e:
                await bot.reply_to(message, f"Произошла ошибка при сохранении фотографии: {str(e)}")

        #user_photos = {'image1': image, 'att' : "Приложение 1. Фото-материалы."}
        print(user_photos)        
        print(user_photos[user_id])   

#collect messages
@bot.message_handler(func=lambda message: True)
async def handle_text_messages(message):

# Используем chat_id пользователя как ключ в словаре
    chat_id = message.chat.id

    # Проверяем, существует ли уже запись для данного пользователя
    if chat_id not in text_messages:
        text_messages[chat_id] = []

    # Добавляем текстовое сообщение в список для данного пользователя
    text_messages[chat_id].append(message.text)
    await bot.send_message(chat_id, "Сообщение добавлено в список. Используйте /go для начала генерации ТЗ на основе ранее указанных данных.")
    print (text_messages)



# сохранение файлов на будущее
@bot.message_handler(content_types=['document'])
async def handle_docs_photo(message):
        try:
            chat_id = message.chat.id
            file_info = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)

            src = 'files/'+message.document.file_name;
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

            await bot.reply_to(message, "Ваш документ сохранен.")
        except Exception as e:
            await bot.reply_to(message, e)

asyncio.run(bot.polling())



# сделать чтобы много фото в одном сообщении тоже обрабатывалось
# понять как сбразывать статус для конкретного юзера
# проверять вводимые данные (кол-во текста на входе)
# не допускать простого выполнения /go

# Закрываем файл
# doc = None
# Очищаем словари и переменные
# text_messages = {}
# user_photos = {}
