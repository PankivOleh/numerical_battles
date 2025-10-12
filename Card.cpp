#include <cstdio>
#include <ctime>
#include "Card.h"
#include <cstdlib>
// Функції

char rand_operator() {
    int rand_num = rand() % 5;
    switch (rand_num) {
        case 0: return '+';
        case 1: return '-';
        case 2: return '*';
        case 3: return '/';
        case 4: return '^';
    }
    return '+';
}
// методи Card
Card::Card() {}

Card* Card:: generate_card() {
    return new Card();}
bool Card:: is_in_hand() {
    return this->in_hand;
}
int Card::use_card() {
    if (this->is_in_hand()) {
        this->in_hand = false;
    }
    else {
        return 1;
    }
    return 0;
}
void Card::set_in_hand() {
    this->in_hand = true;
}
// методи Operator_card
Operator_card::Operator_card() {
    this->op = ' ';
}
Operator_card::Operator_card(char op) {
    this->op = op;
}
Operator_card *Operator_card::generate_card() {
    Operator_card *op = new Operator_card( rand_operator());
    return op;
}
char Operator_card::get_op() {
    return this->op;
}
//методи Numb_card
Numb_card::Numb_card() {
    this->number = 0;
}
Numb_card::Numb_card(double number) {
    this->number = number;
}
Numb_card* Numb_card::generate_card(){
    int i = rand()%3;
    if(i==2) {
        Numb_card *nb = new Numb_card( ((rand()%9)+1)*-1);
        return nb;
    }
    Numb_card *nb = new Numb_card( (rand()%9)+1);
    return nb;
}
double Numb_card::get_numb() {
    return this->number;
}
//методи Secial_card
Special_card::Special_card() {
    this->number = 0;
}
Special_card::Special_card(double number) {
    this->number = number;
}
double Special_card::get_numb() {
    return this->number;
}
Special_card* Special_card::generate_card() {
    int i = rand();
    if(i&1) {
        Special_card *spc = new Special_card( ((rand()%9)+1)*-1);
        return spc;
    }
    Special_card *spc = new Special_card( (rand()%9)+1);
    return spc;
}













