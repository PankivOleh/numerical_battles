#include "Player.h"
#include <iostream>
using namespace std;

int main() {
    Player* Oleh = new Player("oleh" , 18 , 18 ,1 , 2);
    Oleh->set_hp(-3);
    cout<<(*Oleh).get_hp();
    Oleh->set_hp(6);
    Oleh->set_dificult(3);
    Oleh->set_hp(5);
    Oleh->set_hp(-5);
    cout<<(*Oleh).get_hp();
    return 0;
}