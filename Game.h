//
// Created by Oleg on 22.09.2025.
//

#ifndef GAME_H
#define GAME_H
#include "Enemy.h"
#include "Player.h"

class Player;
class Game {
    Player* player;
    Enemy* enemy;
public:
    Game();
    Game(Player* player);
    Player* getPlayer();
    int generateN();
    vector<Card*>* generateChoise();
    int afterChoise(int n , vector<Card*>* choices);
    vector<Numb_card*> generateNumbChoise(int n);
    vector<Operator_card*> generateOperatorChoise(int n);
    vector<Special_card*> generateSpecialChoise();
    int afterSpecialChoise(int n , vector<Special_card*> choices);
    int setHand();
    void mergeCard(int n1 , int n2 , int n3);
    int get_numb_count();
    int get_operator_count();
    int get_special_count();
    vector<string> createarr(string numbers);
    double calculate(string numbers);
    Enemy* createEnemy();
    int checkNumber(double numb1 , double numb2);
    void useSpecial(int n);
    void cleanall();
};

#endif //GAME_H
