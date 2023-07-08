# Building executable
This part of project helps to build executable c++ file for annealing, to do calculations faster.

I have already built executable for Mac OS (Darwin), Linux and Windows, they are stored in [`corners/annealing_executables`](corners/annealing_executables). But if you want to build your own executable, just follow the instructions below
# How to build
* Run `g++ -o board_finder_calc -static main.cpp`. There can be error on Mac OS, just run `g++ -o board_finder_calc main.cpp`. On Windows run `g++ -o board_finder_calc.exe -static main.cpp`
* You will get compiled file, replace file in `corners/annealing_executables/{your_OS}` by your compiled file.
* Run `python check.py`
