//
// Created by Oleg on 30.09.2025.
//

#include "Enemy.h"
#include <ctime>
#include <stdlib.h>
#include <random>

Enemy::Enemy(int level, int difficult) {
    std::mt19937 rng(std::random_device{}());
    double rand;
    if(level <= 4) {
        std::uniform_real_distribution<double> dis(1 , 25*difficult*(1+(double)level/10));
        rand = dis(rng);
        this->number  = std::trunc(rand);
    }
    if(level > 4 && level < 10) {
        std::uniform_real_distribution<double> dis(-25*difficult*(1+(double)level/10) , 25*difficult*(1+(double)level/10));
        rand = dis(rng);
        this->number  = std::trunc(rand);
    }
    if(level >= 10) {
        std::uniform_int_distribution<int> dis1(0 , 2);
        if(dis1(rng) ==2) {
            std::uniform_real_distribution<double> dis(0.01, 1.);
            std::uniform_int_distribution<int>dis2(0 , 1);
            if(dis2(rng) ==1){
                rand = dis(rng);
            }
            else {
                rand = dis(rng)*-1;
            }
            rand = std::round(rand * std::pow(10,2)) / std::pow(10, 2);
        }
        else {
            std::uniform_real_distribution<double> dis(-25*difficult*(1+(double)level/10) , 25*difficult*(1+(double)level/10));
            rand =std::trunc( dis(rng));
        }
    }
    this->number  = rand;
    return;
}

double Enemy::getNumber() {
    return this->number;
}
double Enemy::setNumber(int number) {
    this->number += (double)number;
    return this->number;
}


