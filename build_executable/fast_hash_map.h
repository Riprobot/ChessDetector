#ifndef BOARD_FINDER_CALC_FAST_HASH_MAP_H
#define BOARD_FINDER_CALC_FAST_HASH_MAP_H

#include <array>

template<typename Value, size_t N>
class FastHashMap {
public:
    FastHashMap() {};
    void update(uint64_t key, Value value) {
        size_t i = key % N;
        size_t cnt = 0;
        while (key_[i] != 0) {
            ++i;
            if (i == N) i = 0;
            ++cnt;
            if (cnt >= 3) {
                break;
            }
        }
        key_[i] = key;
        value_[i] = value;
    }
    std::pair<uint64_t, Value> get(uint64_t key) const {
        size_t i = key % N;
        while (key_[i] != 0 && key_[i] != key) {
            ++i;
            if (i == N) i = 0;
        }
        return {key_[i], value_[i]};
    }
private:
    std::array<uint64_t, N> key_{};
    std::array<Value, N> value_{};

};


#endif //BOARD_FINDER_CALC_FAST_HASH_MAP_H
