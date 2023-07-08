cmake_minimum_required(VERSION 3.23)
project(board_finder_calc)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_EXE_LINKER_FLAGS "-static") #for windows
# set(CMAKE_EXE_LINKER_FLAGS) #for unix
add_executable(board_finder_calc main.cpp)
