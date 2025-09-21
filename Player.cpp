//
// Created by Oleg on 18.09.2025.
//

#include "Player.h"
#include "Hand.h"
#include <iostream>

using namespace std;



    Player::Player(string name, int maxhp, int hp, int level, int difficult ,Hand* hand ) {
        this->name = name ;
        this ->hp = hp ;
        this -> level = level ;
        this -> difficult = difficult ;
        this -> maxhp = maxhp/difficult ;
        if(this->hp >this-> maxhp) {
            this->hp = this-> maxhp ;
        }
        this -> hand = hand ;
    }
    int Player:: get_hp() {
        return hp ;
    }
    int Player:: get_difficult() {
        return difficult ;
    }
    int Player:: get_level() {
        return level ;
    }
    string Player:: get_Name() {
        return name;
    }
    int Player::set_hp(int hp) {
        if (this->hp== maxhp&&hp>0) {
            cout << "Player already has max hp" << endl ;
            return 0 ;
        }
        if (hp+this->hp > maxhp) {
            this->hp = maxhp ;
            return 0 ;
        }
        this -> hp = hp+this->hp;
        if(this->hp <= 0 ) {
            cout << "You lose :(" << endl ;
            return -1 ;
        }
        return 0 ;
    }
    int Player::set_dificult(int difficult) {\
        if(difficult>3 || difficult<1) {
            return 1 ;
        }
        maxhp = this->difficult*maxhp ;
        maxhp = maxhp/difficult;
        if(maxhp < hp) {
            hp = maxhp ;
        }
        return 0 ;
    }
    int Player::set_level(int level) {
        if(level<1) {
            return 1 ;
        }
        if(level>5*difficult) {
            cout<<"You won!";
            return -1;
        }
        this -> level = level ;
        return 0 ;
    }
    Hand Player::get_hand() {
        return *hand;
    }
    Player:: ~Player(){}
