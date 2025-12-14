//
// Created by Oleg on 30.09.2025.
//

#include "Enemy.h"
#include <ctime>
#include <stdlib.h>
#include <random>

Enemy::Enemy(double n) {
    this->number = n;
    return;
}

double Enemy::getNumber() {
    return this->number;
}
double Enemy::setNumber(double number) {
    this->number += (double)number;
    return this->number;
}


