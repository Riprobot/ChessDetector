# Chess Detector
* API integrated in [TelegramBot](https://t.me/chess_detector_bot) that convert chess board photos to FEN format
* [YoloV8](https://docs.ultralytics.com/) state-of-art model in detection

This repo was created by _Aidar Asadullin_ as final project of DLS (Deep Learning School) on detection

# Problem

We love playing chess online and offline, but sometimes we need to analyze board position and get best move. If you play online it is easy to do, because we have stockfish in chess sites, but what to do if you play offline. Only way to analyze the situation it is to copy you position piece by piece, sometimes it is boring and slow.

I decided to make telegram bot to solve this problem, you just need to take one photo of board and it will get you direct link to [lichess.org](https://lichess.org), where you position already configured, then you just need check if all pieces are correct and tap button to analyze position and get best move from stockfish.
# Demo
![](demo.gif)

# How it works

Chess board detection splits on 3 main parts:
> 1) Detect corners
> 2) Detect pieces on board
> 3) Merge two detections into FEN

Let's talk about all parts, and I will describe problems and solutions that I had.

### 1. Detect corners
Detecting corners it main part of board recognizing, if corners are incorrect the whole detection will be wrong, so it must have high accuracy.

First, I decided to make detection model on one class, but then I have some problems:
* What if we don't see one or two corners, then model will not detect them.
* What if model detect something that is not corner and detection will be wrong
* We need a big dataset of different boards

After these problems I realized that detecting corners it is not so hard task to use AI, it can be done with algorithm:

Instead of looking for the corners of the board, we will find 14 internal straight lines
7 vertical straight lines and 7 horizontal straight lines
If we find these straight lines, then we can easily find the approximate location of the corners of the board, and then adjust it so that cv2.perspectiveTransforms will be the perfect chessboard

To get the initial list of straight lines, we use cv2.HoughLinesP().
To check which lines fit together, I checked how much their intersections look like a chessboard
Unfortunately cv2.HoughLinesP() sometimes doesn't find the right lines, and also finds a lot of useless lines
Therefore, an algorithm of simulated annealing was implemented to find the final lines
The annealing simulation algorithm requires a lot of iterations so the python code has been running for too long
Therefore, this algorithm has been rewritten in c++, see it on [`build_executable`](build_executable)

### 2. Detect pieces on board

To detect pieces on board we need high accuracy model, I took YoloV8 - now it is state-of-art model in detection task

First, I need dataset of chess pieces, but in Internet I found only one normal [dataset of chess pieces](https://public.roboflow.com/object-detection/chess-full). But these dateset have been created on US CHESS board, but I wanted to detect classic wooden board. So I decided to created my own dataset and train model on it.

### Own dataset

 > I bought [chess board](https://market.yandex.ru/product--desiatoe-korolevstvo-shakhmaty-02845/1780727158?sku=673427455&offerid=kvGiHkxot4KMO1mAj2CKqA&hid=13887809&nid=67217) on Yandex Market, and created and annotated 663 images. Here is [dataset](https://universe.roboflow.com/school-uqbua/chess-dataset-4r7r7)
> 
 > Also, I created some augmentations that roboflow provided

Firstly I trained on big number of raw images containing chess pieces, annotations was bad, but it is only [warm up dataset](https://universe.roboflow.com/school-uqbua/chess-dataset-warm-up/dataset/1)

Second part of training was dataset with good annotations, but on different board. It was [normal dataset](https://public.roboflow.com/object-detection/chess-full) that I found first on US CHESS board.

Third part of training was my own [final dataset](https://universe.roboflow.com/school-uqbua/chess-dataset-4r7r7).

> Training code is provided in [_yolo-v8-train-on-chess.ipynb_](yolo-v8-train-on-chess.ipynb)

>All datasets also provided [here](https://disk.yandex.ru/client/disk/%D0%A8%D0%B0%D1%85%D0%BC%D0%B0%D1%82%D0%BD%D1%8B%D0%B5%20%D0%B4%D0%B0%D1%82%D0%B0%D1%81%D0%B5%D1%82%D1%8B)

### Model results

After training on final dataset YoloV8 have next results on test part:
> Precision:  0.995, Recall: 0.995,MAP50: 0.994, MAP95: 0.925

### 3. Merge detections

Now we have board corners and piece detection, now we can build FEN.

Let do cv2.perspectiveTransforms on our image, that gives us board from bird-eye-view and we can split board on rectangles.

Then lets took piece boxed center and transform these point on new image and in these image we can calculate position on chess board and class we know from detection.


# How to use
* close this repo `https://github.com/Riprobot/ChessDetector.git`
* install requirements.txt `pip install requirements.txt`
* run `python check.py` or `python bot.py` to run telegram bot
* see result in `temp` folder
* or see https://t.me/chess_detector_bot


# Hosting

Now telegram bot hosted on Amvera free servers, and it can be much slower than on your on device. To hosting used [`amvera.yml`](amvera.yml) file

> My device: 6 second
>
> Amvera servers: 45 second 

