import telebot
from image2fen import FEN_Converter

bot_token = 'REMOVED'
bot = telebot.TeleBot(bot_token)
model_path = 'model/best_piece_detector.pt'
start_mes = "Привет это бот для автоматического распознавания шахматной доски, просто пришли мне фото следуя инструкции и получи представление в электронном виде"
detector = FEN_Converter(model_path)
test = True

@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.id)
    bot.send_message(message.chat.id, start_mes)


admin_id = 1893505394
# @bot.message_handler(content_types='text')
# def message_reply(message):
#     global last_user_id
#     user_id = message.chat.id
#     if user_id == main_user_id and last_user_id != -1:
#         bot.send_message(last_user_id, message.text)
#         bot.send_message(main_user_id, f"Отправлено {last_user_id}")
#         last_user_id = -1
#         return
#     markup3 = types.InlineKeyboardMarkup()
#     markup3.add(types.InlineKeyboardButton("Ответить", callback_data=f'answer_{user_id}'))
#     bot.send_message(main_user_id, f"Cообщение от {user_id}: \n {message.text}", reply_markup=markup3)
#
# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
#     global last_user_id
#     try:
#         if call.message:
#             user_id = int(call.data[7:])
#             last_user_id = user_id
#             bot.send_message(main_user_id, f"Напишите ответное сообщение")
#     except Exception as e:
#         print(repr(e))
@bot.message_handler(content_types=['photo'])
def photo(message):
    user_id = message.chat.id
    print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("temp/image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    url = detector.get_lichess_editor('temp/image.jpg')
    bot.send_message(user_id, url)
    if test:
        img = open('temp/chessboard_transformed_with_grid.jpg', 'rb')
        bot.send_photo(user_id, img, caption="Transformed with grid")
        img = open('temp/detection.jpg', 'rb')
        bot.send_photo(user_id, img, caption="Detection")
bot.polling()
