cmake_minimum_required(VERSION 3.29)
project(Numerical_battles_cpp)

set(CMAKE_CXX_STANDARD 14)

add_subdirectory(pybind11)

# Створюємо модуль
pybind11_add_module(PyAPI_py
        Game.cpp
        Player.cpp
        Hand.cpp
        Card.cpp
        PyAPI.cpp
        Enemy.cpp # Переконався, що додав цей файл
)

# === ДОДАЙ ЦЕЙ БЛОК ===
if(WIN32 AND MINGW)
    # Ця команда каже компілятору: "Запхни код бібліотек gcc та stdc++ всередину файлу"
    target_link_options(PyAPI_py PRIVATE "-static-libgcc" "-static-libstdc++" "-Wl,-Bstatic,--whole-archive" "-lwinpthread" "-Wl,--no-whole-archive")
    # АБО спрощений варіант, якщо верхній видасть помилку:
    # target_link_options(PyAPI_py PRIVATE "-static")
endif()
# ======================