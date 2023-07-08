import image2fen
model_path = 'model/warmup_normal_final.pt'
detector = image2fen.FEN_Converter(model_path)
path = 'D:\Study\PyCharm\PyCharmProjects\ChessDetector\\temp\image.jpg'
print(detector.get_lichess_editor(path))
