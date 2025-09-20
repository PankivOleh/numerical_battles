#include "Player.h"
#include "Hand.h"
#include "Card.h"
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
    Oleh->set_hp(-1);
    Numb_card card1 = Numb_card(7)  , card2 = Numb_card(5);
    Operator_card card3 = Operator_card('+');
    cout<<endl<<card1.get_numb()<<card3.get_op()<<card2.get_numb();
    cout<<card3.is_in_hand();
    Numb_card card4 = Numb_card();
    card4 = Hand::merge_cards(card1,card3,card2);
    cout<<'='<<card4.get_numb();
    cout<<card3.is_in_hand();
    cout<<endl;
    Numb_card* card5 = new Numb_card , *card6 = new Numb_card;
    card5 = card5->generate_card();
    card6 = card6->generate_card();
    Operator_card* card7 = new Operator_card();
    card7 = card7->generate_card();
    cout<<card5->get_numb()<<card7->get_op()<<card6->get_numb()<<'=';
    card1 = Hand::merge_cards(*card5 , *card7 ,*card6);
    cout<<card1.get_numb();


    return 0;
}