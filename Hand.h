//
// Created by Admin on 20.09.2025.
//

#ifndef HAND_H
#define HAND_H
#include<vector>
#include "Card.h"
#include "Player.h"
using namespace std;

class Player;

class Hand {
private:
    vector<Numb_card*> Numb_hand;
    vector<Operator_card*> Operator_hand;
    vector<Special_card*> Special_hand;
    const int MAX_NUMB = 10;
    const int MAX_OPERATOR = 6;
    const int MAX_SPECIAL = 5;

public:
    static Numb_card merge_cards(Numb_card &card1, Operator_card &card2 , Numb_card &card3);
    Hand();
    void generate_hand();
    vector<Numb_card> get_hand();
    vector<Operator_card> get_operator_hand();
    vector<Special_card> get_special_hand();
    int add_numb_card(Numb_card &card);
    int add_operator_card(Operator_card &card);
    int add_special_card(Special_card &card);
    int add_card(Card& card);
    int check_hand();
    friend ostream& operator<<(ostream& os , const Hand& hand);
};


#endif //HAND_H
