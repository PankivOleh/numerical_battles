#include "Game.h"
#include <iostream>
#include <time.h>


using namespace std;

void test1(void) {
    Hand* hand = new Hand();
    hand->generate_hand();
    Player* Oleh = new Player("oleh" , 18 , 18 ,1 , 2 , hand);
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
    card4 = Hand::merge_cards(&card1,&card3,&card2);
    cout<<'='<<card4.get_numb();
    cout<<card3.is_in_hand();
    cout<<endl;
    Numb_card* card5 = new Numb_card , *card6 = new Numb_card;
    card5 = card5->generate_card();
    card6 = card6->generate_card();
    Operator_card* card7 = new Operator_card();
    card7 = card7->generate_card();
    cout<<card5->get_numb()<<card7->get_op()<<card6->get_numb()<<'=';
    card1 = Hand::merge_cards(card5 , card7 ,card6);
    cout<<card1.get_numb();

    cout<<*(Oleh->get_hand());
    cout<<Oleh->get_hand()->get_special_count()<<endl;
    cout<<Oleh->get_hand()->get_numb_count()<<endl;
    cout<<"enter number of card to use:"<<endl;
    int n;
    cin>>n;
    hand->get_numb_card(n-1)->use_card();
    cout<<*(Oleh->get_hand());
    hand->check_hand();
    cout<<*(Oleh->get_hand());

}

int main(){
    srand(time(NULL));
    Hand* hand = new Hand();
    Player* player = new Player("Oleh" , 18 , 18 ,1 , 2 , hand);
    Game* game = new Game(player);
    hand->generate_hand();
    cout<<endl<<*game->getPlayer()->get_hand()<<endl;
    double n;
    n = game->calculate("4-2+4*2/3*3^3");
    cout<<"select cards to merge:"<<endl;
    int n1 , n2 , n3;
    cin>>n1>>n2>>n3;
    game->mergeCard(n1 , n2 , n3);
    player->get_hand()->check_hand();
    cout<<endl<<*game->getPlayer()->get_hand()<<endl;
    cout<<n<<endl;



    return 0;
}