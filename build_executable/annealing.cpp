#include "annealing.h"
#include "fast_hash_map.h"

namespace annealing {

    std::mt19937_64 rnd(0);

    using namespace geometry;

    typedef std::array<std::array<uint8_t, IMG_SIZE>, IMG_SIZE> Image;


    std::unordered_map<uint64_t, float> cross_value_map;
    const size_t HASHMAP_SIZE = 100007;
    FastHashMap<float, HASHMAP_SIZE> cross_value_hashmap;

    float cross_value(const Image &img, int left, int right, int up, int down) {
        uint64_t hash_val =
                (uint64_t) left + 1000 * (uint64_t) right + 1000000 * (uint64_t) up + 1000000000 * (uint64_t) down;
        std::pair<uint64_t, float> hashmap_result = cross_value_hashmap.get(hash_val);
        if (hashmap_result.first == hash_val) {
            return hashmap_result.second;
        }
        Line ln1 = Line(Segment(0, left, IMG_SIZE - 1, right));
        Line ln2 = Line(Segment(up, 0, down, IMG_SIZE - 1));
        Vector dot = cross(ln1, ln2);
        Vector d1 = ln1.direction().normalize();
        Vector d2 = ln2.direction().normalize();
        int radius = 5;
        std::vector<float> sm = {0, 0, 0, 0};
        std::vector<float> cnt = {0, 0, 0, 0};
        for (int i = -radius; i <= radius; ++i) {
            for (int j = -radius; j <= radius; ++j) {
                if (i * j == 0) continue;
                int x = round(dot.x + i * d1.x + j * d2.x);
                int y = round(dot.y + i * d1.y + j * d2.y);
                int index = 0;
                if (i > 0 && j > 0) index = 0;
                if (i > 0 && j < 0) index = 1;
                if (i < 0 && j < 0) index = 2;
                if (i < 0 && j > 0) index = 3;
                if (0 <= x && x < IMG_SIZE && 0 <= y && y < IMG_SIZE) {
                    int pixel_color = img[y][x];
                    float weight = (1.0 / (float) std::min(abs(i), abs(j)));
                    sm[index] += (float) pixel_color * weight;
                    cnt[index] += weight;
                }
            }
        }
        for (int i = 0; i < 4; ++i) {
            if (cnt[i] == 0) {
                return -255 * 4;
            }
        }

        std::vector<float> color;
        for (int i = 0; i < 4; ++i) {
            if (cnt[i] == 0) return -255 * 4;
            color.push_back(sm[i] / cnt[i]);
        }
        float result = 0;
        for (int i = 0; i < 4; ++i) {
            result += abs(color[i] - color[(i + 1) % 4]);
        }
        result -= 2 * abs(color[0] - color[2]);
        result -= 2 * abs(color[1] - color[3]);
        cross_value_hashmap.update(hash_val, result);
        return result;
    }

    Board::Board(const Image &img, std::array<int, BOARD_SIZE> l, std::array<int, BOARD_SIZE> r,
                 std::array<int, BOARD_SIZE> u, std::array<int, BOARD_SIZE> d) : left(l),
                                                                                 right(r), up(u),
                                                                                 down(d) {
        int edge_delta = 10;
        for (int i = 0; i < BOARD_SIZE; ++i) {
            if (left[i] < edge_delta) left[i] = edge_delta;
            if (left[i] > IMG_SIZE - 1 - edge_delta) left[i] = IMG_SIZE - 1 - edge_delta;

            if (right[i] < edge_delta) right[i] = edge_delta;
            if (right[i] > IMG_SIZE - 1 - edge_delta) right[i] = IMG_SIZE - 1 - edge_delta;

            if (up[i] < edge_delta) up[i] = edge_delta;
            if (up[i] > IMG_SIZE - 1 - edge_delta) up[i] = IMG_SIZE - 1 - edge_delta;

            if (down[i] < edge_delta) down[i] = edge_delta;
            if (down[i] > IMG_SIZE - 1 - edge_delta) down[i] = IMG_SIZE - 1 - edge_delta;
        }
        std::sort(left.begin(), left.end());
        std::sort(right.begin(), right.end());
        std::sort(up.begin(), up.end());
        std::sort(down.begin(), down.end());
        calc_score(img);
    }

    Vector Board::get_cross(int i, int j) {
        Line h_ln = Line(Segment(0, left[i], IMG_SIZE - 1, right[i]));
        Line v_ln = Line(Segment(up[j], 0, down[j], IMG_SIZE - 1));
        return cross(h_ln, v_ln);
    }

    void Board::calc_score(const Image &img) {
        std::array<std::array<float, BOARD_SIZE>, 2> confidence{};
        float result = 0;
        for (int i = 0; i < BOARD_SIZE - 1; ++i) {
            result -= 100 / std::max(0.001f, (float) (up[i + 1] - up[i]));
            result -= 100 / std::max(0.001f, (float) (down[i + 1] - down[i]));
            result -= 100 / std::max(0.001f, (float) (left[i + 1] - left[i]));
            result -= 100 / std::max(0.001f, (float) (right[i + 1] - right[i]));
        }
        float cross_result = 0;
        for (int i = 0; i < BOARD_SIZE; ++i) {
            for (int j = 0; j < BOARD_SIZE; ++j) {
                float value = cross_value(img, left[i], right[i], up[j], down[j]);
                confidence[0][i] += value;
                confidence[0][j] += value;
                cross_result += value;
            }
        }
        float form_result = 0;
        for (int i = 0; i < BOARD_SIZE - 1; ++i) {
            for (int j = 0; j < BOARD_SIZE - 1; ++j) {
                float h = (dist(get_cross(i, j), get_cross(i, j + 1)) +
                           dist(get_cross(i + 1, j), get_cross(i + 1, j + 1))) / 2;
                float w = (dist(get_cross(i, j), get_cross(i + 1, j)) +
                           dist(get_cross(i, j + 1), get_cross(i + 1, j + 1))) / 2;
                float ratio = abs(h - w) / std::max(1.0f, std::max(h, w));
                form_result -= std::max(0.0f, ratio - 0.2f) * 1000;
            }
        }
        result += cross_result;
        result += form_result;
        score = result;
        worst_horizontal = 0;
        worst_vertical = 0;
        for (int i = 0; i < BOARD_SIZE; ++i) {
            if (confidence[0][i] < confidence[0][worst_horizontal]) {
                worst_horizontal = i;
            }
            if (confidence[1][i] < confidence[1][worst_vertical]) {
                worst_vertical = i;
            }
        }
    }

    int randint(int l, int r) {
        if (l == r) return l;
        uint64_t x = rnd();
        return (l + (x % (r - l + 1)));
    }

    float rndf() {
        return ((float) rnd() / (float) 0xFFFFFFFFFFFFFFFF);
    }

    int triangular(int left, int right, int mid) {
        if (left > right) std::swap(left, right);
        if (left == right) return left;
        float x = (rndf() + rndf()) / 2;
        float center = (float) (mid - left) / (float) (right - left);
        if (x < 0.5) {
            x = 2 * x * center;
        } else {
            x = 1 - 2 * (1 - x) * (1 - center);
        }
        return left + (int) (x * (right - left + 1));
    }

    int triangular(int left, int right) {
        if (left > right) std::swap(left, right);
        return triangular(left, right, (left + right) / 2);
    }

    size_t random_choice(std::vector<int> v) {
        int sm = 0;
        for (auto to: v) {
            sm += to;
        }
        int r = randint(0, sm - 1);
        size_t index = 0;
        while (r >= v[index]) {
            r -= v[index];
            ++index;
        }
        return index;
    }

    Board transform(const Board &board, const Image &img) {
        std::array<int, BOARD_SIZE> new_left = board.left;
        std::array<int, BOARD_SIZE> new_right = board.right;
        std::array<int, BOARD_SIZE> new_up = board.up;
        std::array<int, BOARD_SIZE> new_down = board.down;
        std::vector<int> chance_weight = {100, 100, 100, 100, 50, 100, 50};
        /**
        0 - change_to_random
        1 - small parallel move
        2 - big parallel move
        3 - change to average
        4 - swap begin end
        5 - small rotate
        6 - create new_average
        **/
        size_t transform_index = random_choice(chance_weight);
        float worst_chance = 0.3;
        int i = 0;
        if (transform_index == 0) {
            if (rndf() < 0.5) {
                //horizontal
                i = randint(0, BOARD_SIZE - 1);
                if (rndf() < worst_chance) {
                    i = board.worst_horizontal;
                }
                if (i == 0) {
                    new_left[i] = triangular(new_left[i] - (new_left[i + 1] - new_left[i]), new_left[i + 1] - 1,
                                             new_left[i]);
                    new_right[i] = triangular(new_right[i] - (new_right[i + 1] - new_right[i]), new_right[i + 1] - 1,
                                              new_right[i]);
                } else if (i == BOARD_SIZE - 1) {
                    new_left[i] = triangular(new_left[i - 1] + 1, new_left[i] + (new_left[i] - new_left[i - 1]),
                                             new_left[i]);
                    new_right[i] = triangular(new_right[i - 1] + 1, new_right[i] + (new_right[i] - new_right[i - 1]),
                                              new_right[i]);
                } else {
                    new_left[i] = triangular(new_left[i - 1] + 1, new_left[i + 1] - 1, new_left[i]);
                    new_right[i] = triangular(new_right[i - 1] + 1, new_right[i + 1] - 1, new_right[i]);
                }
            } else {
                i = randint(0, BOARD_SIZE - 1);
                if (rndf() < worst_chance) {
                    i = board.worst_vertical;
                }
                if (i == 0) {
                    new_up[i] = triangular(new_up[i] - (new_up[i + 1] - new_up[i]), new_up[i + 1] - 1, new_up[i]);
                    new_down[i] = triangular(new_down[i] - (new_down[i + 1] - new_down[i]), new_down[i + 1] - 1,
                                             new_down[i]);
                } else if (i == BOARD_SIZE - 1) {
                    new_up[i] = triangular(new_up[i - 1] + 1, new_up[i] + (new_up[i] - new_up[i - 1]),
                                           new_up[i]);
                    new_down[i] = triangular(new_down[i - 1] + 1, new_down[i] + (new_down[i] - new_down[i - 1]),
                                             new_down[i]);
                } else {
                    new_up[i] = triangular(new_up[i - 1] + 1, new_up[i + 1] - 1, new_up[i]);
                    new_down[i] = triangular(new_down[i - 1] + 1, new_down[i + 1] - 1, new_down[i]);
                }
            }
        }
        if (transform_index == 1) {
            if (rndf() < 0.5) {
                int min_distance = -80;
                int max_distance = 80;
                i = randint(0, BOARD_SIZE - 1);
                if (rndf() < worst_chance) {
                    i = board.worst_horizontal;
                }
                if (i != 0) {
                    min_distance = std::max(min_distance, new_left[i - 1] - new_left[i]);
                    min_distance = std::max(min_distance, new_right[i - 1] - new_right[i]);
                }
                if (i != BOARD_SIZE - 1) {
                    max_distance = std::min(max_distance, new_left[i + 1] - new_left[i]);
                    max_distance = std::min(max_distance, new_right[i + 1] - new_right[i]);
                }
                int distance = triangular(min_distance, max_distance);
                new_left[i] += distance;
                new_right[i] += distance;
            } else {
                int min_distance = -80;
                int max_distance = 80;
                i = randint(0, BOARD_SIZE - 1);
                if (rndf() < worst_chance) {
                    i = board.worst_vertical;
                }
                if (i != 0) {
                    min_distance = std::max(min_distance, new_up[i - 1] - new_up[i]);
                    min_distance = std::max(min_distance, new_down[i - 1] - new_down[i]);
                }
                if (i != BOARD_SIZE - 1) {
                    max_distance = std::min(max_distance, new_up[i + 1] - new_up[i]);
                    max_distance = std::min(max_distance, new_down[i + 1] - new_down[i]);
                }
                int distance = triangular(min_distance, max_distance);
                new_up[i] += distance;
                new_down[i] += distance;
            }
        }
        if (transform_index == 2) {
            if (rndf() < 0.5) {
                int min_distance = -160;
                int max_distance = 160;
                i = randint(0, BOARD_SIZE - 1);
                if (rndf() < worst_chance) {
                    i = board.worst_horizontal;
                }
                min_distance = std::max(min_distance, 0 - new_left[i]);
                min_distance = std::max(min_distance, 0 - new_right[i]);
                max_distance = std::min(max_distance, (IMG_SIZE - 1) - new_left[i]);
                max_distance = std::min(max_distance, (IMG_SIZE - 1) - new_right[i]);
                int distance = triangular(min_distance, max_distance);
                new_left[i] += distance;
                new_right[i] += distance;
            } else {
                int min_distance = -160;
                int max_distance = 160;
                i = randint(0, BOARD_SIZE - 1);
                if (rndf() < worst_chance) {
                    i = board.worst_vertical;
                }
                min_distance = std::max(min_distance, 0 - new_up[i]);
                min_distance = std::max(min_distance, 0 - new_down[i]);
                max_distance = std::min(max_distance, (IMG_SIZE - 1) - new_up[i]);
                max_distance = std::min(max_distance, (IMG_SIZE - 1) - new_down[i]);
                int distance = triangular(min_distance, max_distance);
                new_up[i] += distance;
                new_down[i] += distance;
            }
        }
        if (transform_index == 3) {
            if (rndf() < 0.5) {
                i = randint(1, BOARD_SIZE - 2);
                new_left[i] = (new_left[i - 1] + new_left[i + 1]) / 2 + triangular(-5, 5);
                new_right[i] = (new_right[i - 1] + new_right[i + 1]) / 2 + triangular(-5, 5);
            } else {
                i = randint(1, BOARD_SIZE - 2);
                new_up[i] = (new_up[i - 1] + new_up[i + 1]) / 2 + triangular(-5, 5);
                new_down[i] = (new_down[i - 1] + new_down[i + 1]) / 2 + triangular(-5, 5);
            }
        }
        if (transform_index == 4) {
            if (rndf() < 0.5) {
                if (rndf() < 0.5) {
                    new_left[BOARD_SIZE - 1] = new_left[0] + (new_left[0] - new_left[1]) + triangular(-5, 5);
                    new_right[BOARD_SIZE - 1] = new_right[0] + (new_right[0] - new_right[1]) + triangular(-5, 5);
                } else {
                    new_left[0] = new_left[BOARD_SIZE - 1] + (new_left[BOARD_SIZE - 1] - new_left[BOARD_SIZE - 2]) +
                                  triangular(-5, 5);
                    new_right[0] = new_right[BOARD_SIZE - 1] + (new_right[BOARD_SIZE - 1] - new_right[BOARD_SIZE - 2]) +
                                   triangular(-5, 5);
                }
            } else {
                if (rndf() < 0.5) {

                    new_up[BOARD_SIZE - 1] = new_up[0] + (new_up[0] - new_up[1]) + triangular(-5, 5);
                    new_down[BOARD_SIZE - 1] = new_down[0] + (new_down[0] - new_down[1]) + triangular(-5, 5);
                } else {
                    new_up[0] = new_up[BOARD_SIZE - 1] + (new_up[BOARD_SIZE - 1] - new_up[BOARD_SIZE - 2]) +
                                triangular(-5, 5);
                    new_down[0] = new_down[BOARD_SIZE - 1] + (new_down[BOARD_SIZE - 1] - new_down[BOARD_SIZE - 2]) +
                                  triangular(-5, 5);
                }
            }
        }
        if (transform_index == 5) {
            if (rndf() < 0.5) {
                i = randint(0, BOARD_SIZE - 1);
                if (rndf() < worst_chance) {
                    i = board.worst_horizontal;
                }
                new_left[i] = new_left[i] + triangular(-5, 5);
                new_right[i] = new_right[i] + triangular(-5, 5);
            } else {
                i = randint(0, BOARD_SIZE - 1);
                if (rndf() < worst_chance) {
                    i = board.worst_vertical;
                }
                new_up[i] = new_up[i] + triangular(-5, 5);
                new_down[i] = new_down[i] + triangular(-5, 5);
            }
        }
        if (transform_index == 6) {
            if (rndf() < 0.5) {
                std::vector<int> a;
                for (int j = 1; j < BOARD_SIZE - 3; ++j) {
                    int val = new_left[j + 1] - new_left[j] + new_right[j + 1] - new_right[j];
                    a.push_back(val * val);
                }
                i = random_choice(a) + 1;
                size_t replace_index = 0;
                if (rndf() < 0.5) {
                    replace_index = BOARD_SIZE - 1;
                }
                if ((board.worst_horizontal == 0 || board.worst_horizontal == BOARD_SIZE - 1) && rndf() < 0.7) {
                    replace_index = board.worst_horizontal;
                }
                new_left[replace_index] = (new_left[i - 1] + new_left[i + 1]) / 2 + triangular(-5, 5);
                new_right[replace_index] = (new_right[i - 1] + new_right[i + 1]) / 2 + triangular(-5, 5);
            } else {
                std::vector<int> a;
                for (int j = 1; j < BOARD_SIZE - 3; ++j) {
                    int val = new_up[j + 1] - new_up[j] + new_down[j + 1] - new_down[j];
                    a.push_back(val * val);
                }
                i = random_choice(a) + 1;
                size_t replace_index = 0;
                if (rndf() < 0.5) {
                    replace_index = BOARD_SIZE - 1;
                }
                if ((board.worst_vertical == 0 || board.worst_vertical == BOARD_SIZE - 1) && rndf() < 0.7) {
                    replace_index = board.worst_vertical;
                }
                new_up[replace_index] = (new_up[i - 1] + new_up[i + 1]) / 2 + triangular(-5, 5);
                new_down[replace_index] = (new_down[i - 1] + new_down[i + 1]) / 2 + triangular(-5, 5);
            }
        }
        return Board(img, new_left, new_right, new_up, new_down);
    }

    float probability(float old_score, float new_score, float temperature) {
        if (new_score > old_score) return 1;
        return exp((new_score - old_score) / temperature);
    }

    Board simulation(const Image &img, Board board, size_t iter_cnt, size_t start_t, size_t final_cnt) {
        for (int i = 0; i < iter_cnt; ++i) {
            float t = start_t - (i * start_t / iter_cnt);
            Board new_board = transform(board, img);
            if (rndf() <= probability(board.score, new_board.score, t)) {
                board = new_board;
            }
            if (i % 5 == 0) {
                cross_value_map.clear();
            }
        }
        return board;
    }
}