//
// Created by Oleg on 18.09.2025.
//

#ifndef PLAYER_H
#define PLAYER_H
#include <string>

class Player {
private:
    std::string name;
    int hp =1 ;
    int level =1;
    int difficult =1;
    int maxhp =1;
public:
    Player(std::string name, int maxhp, int hp, int level, int difficult);
    int get_hp();
    int get_difficult();
    int get_level();
    int set_hp(int hp);
    int set_dificult(int difficult);
    int set_level(int level);
    ~Player();
};


#endif //PLAYER_H
