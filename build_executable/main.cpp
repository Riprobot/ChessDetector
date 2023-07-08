#include <iostream>
#include <fstream>

#include "annealing.h"

int hex_char(char ch) {
    if ('0' <= ch && ch <= '9') return (ch - '0');
    return (ch - 'a') + 10;
}

int main() {
    std::ofstream output_file;
    output_file.open("temp/corners.txt");
    if(!output_file) { // file couldn't be opened
        std::cout << "output_file couldn't be opened" << std::endl;
        return 1;
    }
    std::ifstream file;
    file.open("temp/board_find_data.txt");
    if(!file) { // file couldn't be opened
        std::cout << "file couldn't be opened" << std::endl;
        return 1;
    }
    int n, m;
    file >> n >> m;
    if (n != IMG_SIZE || m != IMG_SIZE) {
        std::cout << "wrong img size" << std::endl;
        std::cout << "get " << n << " " << m << std::endl;
        std::cout << "need " << IMG_SIZE << " " << IMG_SIZE << std::endl;
        return 1;
    }
    annealing::Image img;
    std::string s;
    for (int i = 0; i < IMG_SIZE; ++i) {
        for (int j = 0; j < IMG_SIZE; ++j) {
            file >> s;
            img[i][j] = hex_char(s[0]) * 16 + hex_char(s[1]);
        }
    }
    std::array<int, BOARD_SIZE> left;
    std::array<int, BOARD_SIZE> right;
    std::array<int, BOARD_SIZE> up;
    std::array<int, BOARD_SIZE> down;
    for (int i = 0; i < BOARD_SIZE; ++i) { //asdasdasdasdasasdasdasdasdasdasddfsdsdasdasd
        file >> left[i];
    }
    for (int i = 0; i < BOARD_SIZE; ++i) {
        file >> right[i];
    }
    for (int i = 0; i < BOARD_SIZE; ++i) {
        file >> up[i];
    }
    for (int i = 0; i < BOARD_SIZE; ++i) {
        file >> down[i];
    }
//    std::cout << "read_time=" << clock() << "ms" << std::endl;ss
    annealing::Board board(img, left, right, up, down);
    annealing::Board result = annealing::simulation(img, board, 9000, 100, 1000);
//    std::cout << "ok3" << std::endl;
//    std::cout << result.score << std::endl;
//    std::cout << "left = [";
//    for (int i = 0; i < BOARD_SIZE; ++i) {
//        std::cout << result.left[i];
//        if (i != BOARD_SIZE - 1) {
//            std::cout << ", ";
//        }
//    } std::cout << "]\n";
//    std::cout << "right = [";
//    for (int i = 0; i < BOARD_SIZE; ++i) {
//        std::cout << result.right[i];
//        if (i != BOARD_SIZE - 1) {
//            std::cout << ", ";
//        }
//    } std::cout << "]\n";
//    std::cout << "up = [";
//    for (int i = 0; i < BOARD_SIZE; ++i) {
//        std::cout << result.up[i];
//        if (i != BOARD_SIZE - 1) {
//            std::cout << ", ";
//        }
//    } std::cout << "]\n";
//    std::cout << "down = [";
//    for (int i = 0; i < BOARD_SIZE; ++i) {
//        std::cout << result.down[i];
//        if (i != BOARD_SIZE - 1) {
//            std::cout << ", ";
//        }
//    } std::cout << "]\n";

    for (int i = 0; i < BOARD_SIZE; ++i) {
        output_file << result.left[i] << " ";
    } output_file << "\n";
    for (int i = 0; i < BOARD_SIZE; ++i) {
        output_file << result.right[i] << " ";
    } output_file << "\n";
    for (int i = 0; i < BOARD_SIZE; ++i) {
        output_file << result.up[i] << " ";
    } output_file << "\n";
    for (int i = 0; i < BOARD_SIZE; ++i) {
        output_file << result.down[i] << " ";
    } output_file << "\n";


//    std::cout << (int)img[0][0] << std::endl;
//    std::cout << n << " " <<  m << std::endl;
//    std::cout << "Hello, World!" << std::endl;
    std::cout << "c++ time=" << clock() << "ms" << std::endl;
    return 0;
}
