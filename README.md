# Chess Detector
* API integrated in TelegramBot that convert chess board photos to FEN format
* YoloV8 state-of-art model in detection

This repo was created by _Aidar Asadullin_ as final project of DLS (Deep Learning School) on detection

# Demo
![](demo.gif)
# How to use
* clone this repo
* include ```HashMap.h``` (see example below)

# Code example: 
```C++

#include <iostream>
#include "HashMap.h"

HashMap <string, string> hash_map;
hash_map["Hello"] = "world!";
hash_map["name"] = "Aydar";
if (hash_map.count("Hello")) {
  std::cout << "Hello " << hash_map["Hello"] << '\n';
}
for (auto element: hash_map) {
   std::cout << element.first << " " << element.second << '\n';
}
```
# Fine tuning
You can change HashMap hyperparameters in file ```"HashMap.h"```:
* max_load_factor (optimal = 0.70): the percentage at which the HashMap will increase its capacity,  <b>make it smaller to speed up answer time, but increase the HashMap capacity</b>
* capacity_multiplier (optimal = 2.0): coefficient by which the memory size will increase, <b>make it bigger to speed up answer time, but increase the HashMap capacity </b>
# Speed test (HashMap vs unordered_map)
```
small_test (10^5 queries)
hash_map_time 0.0370000000 seconds
unordered_map_time 0.0260000000 seconds



middle_test (10^7 queries)
hash_map_time 1.1480000000 seconds
unordered_map_time 4.6640000000 seconds



large_test (10^8 queries)
hash_map_time 17.9720000000 seconds
unordered_map_time 42.1540000000 seconds
```
