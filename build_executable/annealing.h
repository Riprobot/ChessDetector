#ifndef BOARD_FINDER_CALC_ANNEALING_H
#define BOARD_FINDER_CALC_ANNEALING_H

#include "geometry.h"

#include <array>
#include <algorithm>
#include <vector>
#include <math.h>
#include <random>
#include <cassert>
#include <iostream>
#include <unordered_map>

const int IMG_SIZE = 416;
const size_t BOARD_SIZE = 7;

namespace annealing {

//    std::mt19937_64 rnd(0);

    using namespace geometry;

    typedef std::array<std::array<uint8_t, IMG_SIZE>, IMG_SIZE> Image;


//    std::unordered_map<uint64_t, float> cross_value_map;

    float cross_value(const Image &img, int left, int right, int up, int down);

    struct Board {
        Board(const Image &img, std::array<int, BOARD_SIZE> l, std::array<int, BOARD_SIZE> r,
              std::array<int, BOARD_SIZE> u, std::array<int, BOARD_SIZE> d);

        Vector get_cross(int i, int j);

        void calc_score(const Image &img);

//        const Image &img;
        std::array<int, BOARD_SIZE> left;
        std::array<int, BOARD_SIZE> right;
        std::array<int, BOARD_SIZE> up;
        std::array<int, BOARD_SIZE> down;
        size_t worst_horizontal = BOARD_SIZE;
        size_t worst_vertical = BOARD_SIZE;
        float score = 0;
    };

    int randint(int l, int r);

    float rndf();

    int triangular(int left, int right, int mid);

    int triangular(int left, int right);

    size_t random_choice(std::vector<int> v);

    Board transform(const Board &board, const Image &img);

    float probability(float old_score, float new_score, float temperature);

    Board simulation(const Image &img, Board board, size_t iter_cnt=20000, size_t start_t=100, size_t final_cnt=1000);
}

#endif //BOARD_FINDER_CALC_ANNEALING_H
