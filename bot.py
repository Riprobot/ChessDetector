import telebot
from image2fen import FEN_Converter

bot_token = 'REMOVED'
bot = telebot.TeleBot(bot_token)
model_path = 'model/warmup_normal_final.pt'
start_mes = "Привет это бот для автоматического распознавания шахматной доски, просто пришли мне фото следуя инструкции и получи представление в электронном виде"
detector = FEN_Converter(model_path)
test = True

@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.id)
    bot.send_message(message.chat.id, start_mes)


admin_id = 1893505394
@bot.message_handler(content_types=['photo'])
def photo(message):
    user_id = message.chat.id
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("temp/image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(user_id, "Started to detect")
    url = detector.get_lichess_editor('temp/image.jpg')
    if test:
        img = open('temp/chessboard_transformed_with_grid.jpg', 'rb')
        bot.send_photo(user_id, img, caption="Transformed with grid")
        img = open('temp/detection.jpg', 'rb')
        bot.send_photo(user_id, img, caption="Detection")
    bot.send_message(user_id, url)
bot.polling()
