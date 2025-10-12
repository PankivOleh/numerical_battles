cmake_minimum_required(VERSION 3.29)
project(Numerical_battles_cpp)

set(CMAKE_CXX_STANDARD 14)

add_subdirectory(pybind11)
pybind11_add_module(PyAPI_py
    numerical_battles/Game.cpp
    numerical_battles/Player.cpp
    numerical_battles/Hand.cpp
    numerical_battles/Card.cpp
    numerical_battles/PyAPI.cpp
    numerical_battles/Enemy.cpp)