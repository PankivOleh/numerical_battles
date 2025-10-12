#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Game.h"

namespace py = pybind11;

using Player_constructor_6args = Player* (Player::*)(
    std::string,
    int,
    int,
    int,
    int,
    Hand*
);

PYBIND11_MODULE(numerical_battles_api, m) {
    m.doc() = "Numerical Battles API";
    py::class_<Card>(m,"Card")
        .def(py::init<>());
    py::class_<Hand>(m,"Hand")
        .def(py::init<>());
    py::class_<Player>(m, "Player")
        .def(py::init<std::string, int, int, int, int,Hand*>())
    ;
    py::class_<Game>(m, "Game")
        .def(py::init<Player*>())
        .def("cleanall", &Game::cleanall)
        .def("calculate", &Game::calculate)
        .def("generate_choise", &Game::generateChoise)
        .def("get_player", &Game::getPlayer)
        .def("after_choise", &Game::afterChoise)
        .def("generate_special_choise", &Game::generateSpecialChoise)
        .def("after_special_choise", &Game::afterSpecialChoise)
        .def("merge_cards",&Game::mergeCard)
        .def("set_hand" , &Game::setHand)
        .def("check_number", &Game::checkNumber)
        .def("create_enemy" , &Game::createEnemy)
        .def("use_special_card" , &Game::useSpecial)
        ;
}