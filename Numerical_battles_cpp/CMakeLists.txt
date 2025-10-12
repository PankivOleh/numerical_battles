cmake_minimum_required(VERSION 3.29)
project(Numerical_battles_cpp)
add_subdirectory(pybind11)
pybind11_add_module( Numerical_Battles_API
        numerical_battles/PyAPI.cpp
        numerical_battles/Game.cpp
        numerical_battles/Player.cpp
        numerical_battles/Hand.cpp
        numerical_battles/Card.cpp
        numerical_battles/Enemy.cpp
)

set(CMAKE_CXX_STANDARD 20)

