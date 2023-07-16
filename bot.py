def check_ffmpeg():
    import os
    os.system('apt-get update && apt-get install ffmpeg libsm6 libxext6  -y')

check_ffmpeg()

import telebot
from image2fen import FEN_Converter

bot_token = 'REMOVED'
bot = telebot.TeleBot(bot_token)
model_path = 'model/warmup_normal_final.pt'
start_mes = "Привет это бот для автоматического распознавания шахматной доски, просто пришли мне фото следуя инструкции и получи представление в электронном виде на сайте lichess.org"
instruction_mes = "Присылай изображение строго в таком формате:\n" \
                  "1) Изображение шахматной доски строго сбоку, при этом белый фигуры должны быть СЛЕВА, черные фигуры СПРАВА\n" \
                  "2) Доска на фото должна быть расположена ПАРАЛЛЕЛЬНО горизонту \n" \
                  "3) Фото должно быть КВАДРАТНЫМ, но чтобы в него полностью попадала шахматная доска (обрезать можно с помощью встроенного редактора в telegram)\n"
detector = FEN_Converter(model_path)
test = True


@bot.message_handler(commands=['start'])
def start_message(message):
    print(message.chat.id)
    bot.send_message(message.chat.id, start_mes)
    bot.send_photo(message.chat.id, open('images/example.jpg', 'rb'), instruction_mes)


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

if __name__ == '__main__':
    bot.polling()
