//
// Created by Oleg on 30.09.2025.
//

#include "Enemy.h"

#include <stdlib.h>

Enemy::Enemy(int level, int difficult) {
    this->number  = rand() % (25*difficult);
    if(level > 3) {
        rand()%3?this->number+=(rand()%100)/100:this->number+=0;
    }
    if(level > 5) {
        rand()%5?this->number*=-1:this->number+=0;
    }
}
double Enemy::getNumber() {
    return this->number;
}

