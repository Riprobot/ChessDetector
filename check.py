import image2fen
model_path = 'model/best_piece_detector.pt'
detector = image2fen.FEN_Converter(model_path)
path = 'D:\Study\PyCharm\PyCharmProjects\ChessDetector\images\\4e3117459d759798537eb52cf5bf534d_jpg.rf.ec961b62d4b0e131fae760ed1f80836b.jpg'
print(detector.get_lichess_analysis(path))