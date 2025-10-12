cmake_minimum_required(VERSION 3.29)
project(Numerical_battles_cpp)

set(CMAKE_CXX_STANDARD 14)

add_subdirectory(pybind11)
pybind11_add_module(PyAPI_py
    Game.cpp
    Player.cpp
    Hand.cpp
    Card.cpp
    PyAPI.cpp
    Enemy.cpp)