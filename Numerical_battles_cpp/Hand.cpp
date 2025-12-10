#include "Card.h"
#include "Hand.h"
#include <iostream>
#include <ostream>
#include <math.h>

Numb_card Hand:: merge_cards(Numb_card *card1, Operator_card *card2 , Numb_card *card3) {
    double numb1 = card1->get_numb() , numb2 = card3->get_numb();
    switch(card2->get_op()) {
        case '+': numb1 = numb1 + numb2;break;
        case '/':
    if(numb2 == 0 || fabs(numb2) < 0.0001) {
        numb1 = 0;
    } else {
        numb1 /= numb2;
    }
        break;
        case '*': numb1 *= numb2;break;
        case '-': numb1 -= numb2;break;
        case '^': numb1 = pow(numb1,numb2);break;
    }
    card1->use_card();
    card2->use_card();
    card3->use_card();

    return Numb_card(numb1);
}
ostream& operator<<(ostream& os , const Hand& hand) {
    cout<<"Numb_cards:"<<endl;
    for(auto it = hand.Numb_hand.begin(); it != hand.Numb_hand.end(); it++) {
        cout <<"---"<<endl;
        cout<<"|    |"<<endl;
        cout<<"| "<<(*it)->get_numb()<<" |"<<endl;
        cout<<"|    |"<<endl;
        cout<<" ---"<<endl;
        cout<<(*it)->is_in_hand()<<endl;
    }
    cout<<"operator cards:"<<endl;
    for(auto it = hand.Operator_hand.begin(); it != hand.Operator_hand.end(); it++) {
        cout <<"---"<<endl;
        cout<<"|    |"<<endl;
        cout<<"| "<<(*it)->get_op()<<" |"<<endl;
        cout<<"|    |"<<endl;
        cout<<" ---"<<endl;
        cout<<(*it)->is_in_hand()<<endl;
    }
    cout<<"Special cards:"<<endl;
    for(auto it = hand.Special_hand.begin(); it != hand.Special_hand.end(); it++) {
        cout <<"---"<<endl;
        cout<<"|    |"<<endl;
        cout<<"| "<<(*it)->get_numb()<<" |"<<endl;
        cout<<"|    |"<<endl;
        cout<<" ---"<<endl;
        cout<<(*it)->is_in_hand()<<endl;
    }
    return os;
}
void Hand::generate_hand() {
    for(int i  =0; i<MAX_NUMB; i++) {
      Numb_hand.push_back(Numb_card().generate_card());
        Numb_hand[i]->set_in_hand();
    }
    for(int i =0 ; i<MAX_OPERATOR; i++) {
        Operator_hand.push_back(Operator_card().generate_card());
        Operator_hand[i]->set_in_hand();
    }
    for(int i =0 ; i<MAX_SPECIAL-3; i++) {
        Special_hand.push_back(Special_card().generate_card());
        Special_hand[i]->set_in_hand();
    }
}
vector<Numb_card*>* Hand::get_numb_hand() {
    return &Numb_hand;
}
vector<Operator_card*>* Hand::get_operator_hand() {
    return &Operator_hand;
}
vector<Special_card*>* Hand::get_special_hand() {
    return &Special_hand;
}
Numb_card* Hand::get_numb_card(int n) {
    return Numb_hand[n];
}
Operator_card* Hand::get_operator_card(int n) {
    return Operator_hand[n];
}
Special_card* Hand::get_special_card(int n) {
    return Special_hand[n];
}
int Hand::check_hand() {
    for(auto it = Numb_hand.begin(); it != Numb_hand.end();) {
        if(!(*it)->is_in_hand()) {
            delete (*it);
            it = Numb_hand.erase(it);
        }
        else
            it++;
    }
    for(auto it = Operator_hand.begin(); it != Operator_hand.end(); ) {
        if(!(*it)->is_in_hand()) {
            delete (*it);
            it = Operator_hand.erase(it);
        }
        else
            it++;
    }
    for(auto it = Special_hand.begin(); it != Special_hand.end();) {
        if(!(*it)->is_in_hand()) {
            delete (*it);
            it = Special_hand.erase(it);
        }
        else
            it++;
    }
    return 0;
}
int Hand::get_numb_count() {
    return Numb_hand.size();
}
int Hand::get_operator_count() {
    return Operator_hand.size();
}
int Hand::get_special_count() {
    return Special_hand.size();
}
int Hand::add_numb_card(Numb_card &card) {
    if(Numb_hand.size() >= MAX_NUMB) {
        return -1;
    }
    Numb_card* temp = new Numb_card(card);
    temp->set_in_hand();
    Numb_hand.push_back(temp);
    return Numb_hand.size();
}
int Hand::add_operator_card(Operator_card &card) {
    if(Operator_hand.size() >= MAX_OPERATOR) {
        return -1;
    }
    Operator_card* temp = new Operator_card(card);
    temp->set_in_hand();
    Operator_hand.push_back(temp);
    return Operator_hand.size();
}
int Hand::add_special_card(Special_card &card) {
    if(Special_hand.size() >= MAX_SPECIAL) {
        return -1;
    }
        Special_card* temp = new Special_card(card);
        temp->set_in_hand();
    Special_hand.push_back(temp);
    return Special_hand.size();
}
Hand::Hand() {}


