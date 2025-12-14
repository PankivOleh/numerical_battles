#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Game.h"
#include "Player.h"
#include "Hand.h"
#include "Card.h"

namespace py = pybind11;

PYBIND11_MODULE(PyAPI_py, m) {
    m.doc() = "Numerical Battles API";

    // --- 1. КАРТИ ---
    // Спочатку реєструємо базовий клас
    py::class_<Card>(m, "Card")
        .def(py::init<>());

    // Реєструємо Numb_card, вказуючи, що він спадкується від Card
    py::class_<Numb_card, Card>(m, "Numb_card")
        .def(py::init<double>())
        .def("get_numb", &Numb_card::get_numb);

    // Реєструємо Operator_card
    py::class_<Operator_card, Card>(m, "Operator_card")
        .def(py::init<char>())
        .def("get_op", &Operator_card::get_op);

    // Реєструємо Special_card (ВАЖЛИВО!)
    py::class_<Special_card, Card>(m, "Special_card")
        .def(py::init<double>())
        .def("get_numb", &Special_card::get_numb);


    // --- 2. РУКА (Hand) ---
    py::class_<Hand>(m, "Hand")
        .def(py::init<>())
        .def("generate_hand", &Hand::generate_hand)
        .def("check_hand", &Hand::check_hand)

        // Кількість карт
        .def("get_numb_count", &Hand::get_numb_count)
        .def("get_operator_count", &Hand::get_operator_count)
        .def("get_special_count", &Hand::get_special_count)

        // Отримання конкретних карт (reference, щоб Python не видаляв їх)
        .def("get_numb_card", &Hand::get_numb_card, py::return_value_policy::reference)
        .def("get_operator_card", &Hand::get_operator_card, py::return_value_policy::reference)
        .def("get_special_card", &Hand::get_special_card, py::return_value_policy::reference);


    // --- 3. ГРАВЕЦЬ (Player) ---
    py::class_<Player>(m, "Player")
        .def(py::init<std::string, int, int, int, int, Hand*>())
        .def("get_hand", &Player::get_hand, py::return_value_policy::reference)
        .def("get_hp", &Player::get_hp)
        .def("get_name", &Player::get_Name)
        .def("set_hp", &Player::set_hp)
        .def("set_level", &Player::set_level);


    // --- 4. ВОРОГ (Enemy) ---
    py::class_<Enemy>(m, "Enemy")
        .def(py::init<double>())
        .def("get_number", &Enemy::getNumber)
        .def("set_number", &Enemy::setNumber);


    // --- 5. ГРА (Game) ---
    py::class_<Game>(m, "Game")
        .def(py::init<Player*>())
        .def("cleanall", &Game::cleanall)
        .def("calculate", &Game::calculate)
        .def("set_hand", &Game::setHand)
        .def("get_player", &Game::getPlayer, py::return_value_policy::reference)
        .def("create_enemy", &Game::createEnemy, py::return_value_policy::reference)
        .def("check_number", &Game::checkNumber)

        // Методи, що передають володіння новими об'єктами Python-у (take_ownership)
        .def("generate_choise", &Game::generateChoise, py::return_value_policy::take_ownership)
        .def("generate_special_choise", &Game::generateSpecialChoise, py::return_value_policy::take_ownership)

        // Дії
        .def("after_choise", &Game::afterChoise)
        .def("after_special_choise", &Game::afterSpecialChoise)
        .def("merge_cards", &Game::mergeCard)
        .def("use_special_card", &Game::useSpecial)
        .def("remove_cards", &Game::removeCards);
}