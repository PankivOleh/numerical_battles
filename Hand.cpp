
#include "Card.h"
#include "Hand.h"

#include <iostream>
#include <ostream>

Numb_card Hand:: merge_cards(Numb_card &card1, Operator_card &card2 , Numb_card &card3) {
    int numb1 = card1.get_numb() , numb2 = card3.get_numb();
    switch(card2.get_op()) {
        case '+': numb1 = numb1 + numb2;break;
        case '/': numb2==0? numb1 =0: numb1 /=numb2;;break;
        case '*': numb1 *= numb2;break;
        case '-': numb1 -= numb2;break;
    }
    card1.use_card();
    card2.use_card();
    card3.use_card();
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
    }
    cout<<"operator cards:"<<endl;
    for(auto it = hand.Operator_hand.begin(); it != hand.Operator_hand.end(); it++) {
        cout <<"---"<<endl;
        cout<<"|    |"<<endl;
        cout<<"| "<<(*it)->get_op()<<" |"<<endl;
        cout<<"|    |"<<endl;
        cout<<" ---"<<endl;
    }
    cout<<"Special cards:"<<endl;
    for(auto it = hand.Special_hand.begin(); it != hand.Special_hand.end(); it++) {
        cout <<"---"<<endl;
        cout<<"|    |"<<endl;
        cout<<"| "<<(*it)->get_numb()<<" |"<<endl;
        cout<<"|    |"<<endl;
        cout<<" ---"<<endl;
    }
    return os;
}
void Hand::generate_hand() {
    for(int i  =0; i<MAX_NUMB; i++) {
      Numb_hand.push_back(Numb_card().generate_card());
    }
    for(int i =0 ; i<MAX_OPERATOR; i++) {
        Operator_hand.push_back(Operator_card().generate_card());
    }
    for(int i =0 ; i<MAX_SPECIAL-3; i++) {
        Special_hand.push_back(Special_card().generate_card());
    }
}
Hand::Hand() {
}


