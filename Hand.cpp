
#include "Card.h"
#include "Hand.h"

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