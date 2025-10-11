#include <pybind11/pybind11.h>
#include "Game.h"

namespace py = pybind11;

PYBIND11_MODULE(numerical_battles_api, m) {
    py::class_<Game>(m, "Game")
        .def(py::init<>())
        .def("cleanall", &Game::cleanall)
        // інші методи
        ;
}