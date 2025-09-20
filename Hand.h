//
// Created by Admin on 20.09.2025.
//

#ifndef HAND_H
#define HAND_H
#include<vector>
#include "Card.h"
using namespace std;

class Hand {
private:
    vector<Numb_card> Numb_hand;
    vector<Operator_card> Operator_hand;
    vector<Special_card> Special_hand;
    const int MAX_CARDS = 15;
    const int MAX_SPECIAL = 5;
    public:
    static Numb_card merge_cards(Numb_card &card1, Operator_card &card2 , Numb_card &card3);
};


#endif //HAND_H
