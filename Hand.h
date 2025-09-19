//
// Created by Admin on 20.09.2025.
//

#ifndef HAND_H
#define HAND_H
#include<map>
#include "Card.h"
using namespace std;

class Hand {
private:
    map<Numb_card , int> Numb_hand;
    map<Operator_card , int> Operator_hand;
    map<Special_card , int> Special_hand;
    const int MAX_CARDS = 15;
    const int MAX_SPECIAL = 5;
};


#endif //HAND_H
