#include <iostream>
#include <stack>
#include "Game.h"

#include <math.h>
#include <valarray>
using namespace std;

// методи не призначені для пайтону
Player* Game::getPlayer() {
    return player;
}
int Game::generateN() {
    int n ;
    if(rand() & 1) {
        n = 3;
    }else {
        n = 2;
    }
    return n;
}
vector<Numb_card *> Game::generateNumbChoise(int n) {
    vector<Numb_card *> ch;
    for(int i = 0; i < n; i++) {
        Numb_card *c = new Numb_card();
        ch.push_back(c->generate_card());
    }
    return ch;
}
vector<Operator_card *> Game::generateOperatorChoise(int n) {
    vector<Operator_card *> ch;
    for(int i = 0; i < 5-n; i++) {
        Operator_card *c = new Operator_card();
        ch.push_back(c->generate_card());
    }
    return ch;
}

//методи для пайтону
vector<Special_card*>Game::generateSpecialChoise() {
    vector<Special_card *> ch;
    for(int i = 0; i < 3; i++) {
        Special_card *c = new Special_card();
        ch.push_back(c->generate_card());
    }
}
int Game::afterSpecialChoise(int n, vector<Special_card*> choices) {
    getPlayer()->get_hand()->add_special_card(*choices[n]);
    for(auto c : choices) {
        delete c;
    }
    choices.clear();
    return 0;
}
vector<Card*>* Game::generateChoise() {
    int n = generateN();
    vector<Operator_card *> ch = generateOperatorChoise(n);
    vector<Numb_card *> numb = generateNumbChoise(n);
    vector<Card*>* pool = new vector<Card*>;
    for(int i = 0; i < n; i++) {
        pool->push_back(numb[i]);
    }
    for(;n<5;n++) {
        pool->push_back(ch[n]);
    }
    return pool;
}
int Game::afterChoise(int n  , vector<Card*>* ch) {
    Card* c = (*ch)[n];
    if (Numb_card* nc =  dynamic_cast<Numb_card*>(c)) {
        player->get_hand()->add_numb_card(*nc);
    } else if (Operator_card* oc = dynamic_cast<Operator_card*>(c)) {
        player->get_hand()->add_operator_card(*oc);
    }
    for(auto it = ch->begin(); it != ch->end(); it++) {
        delete *it;
    }
    ch->clear();
    return 0;
}
Game::Game(Player *player) {
    this->player = player;
}
Game::Game() {}
int Game::setHand() {
    getPlayer()->get_hand()->generate_hand();
}
void Game::mergeCard(int n1, int n2, int n3) {
    vector<Numb_card*>* v1 = player->get_hand()->get_numb_hand();
    vector<Operator_card*>* v2 = player->get_hand()->get_operator_hand();
    Numb_card* nc1 = (*v1)[n1];
    Numb_card* nc2 = (*v1)[n3];
    Operator_card* oc1 = (*v2)[n2];
    Numb_card newc = (player->get_hand()->merge_cards(nc1 , oc1 , nc2));
    player->get_hand()->check_hand();
    player->get_hand()->add_numb_card(newc);
}
int Game::get_numb_count() {
    return getPlayer()->get_hand()->get_numb_count();
}
int Game::get_operator_count() {
    return getPlayer()->get_hand()->get_operator_count();
}
int Game::get_special_count() {
    return player->get_hand()->get_special_count();
}
int ismorepreor(char op) {
    switch (op) {
        case '+': return 1;
        case '-': return 1;
        case '*': return 2;
        case '/': return 2;
        case '^': return 3;
        default: return 0;
    }
}

vector<string> Game::createarr(string numbers) {
    stack<char> opstack;
    vector<string> arr;
    string num ;
    string op;
    for(auto it  = numbers.begin(); it != numbers.end(); it++) {
        if (std::isdigit(*it)||*it == '.') {
            while (isdigit(*it)||*it == '.') {
                num.push_back(*it);
                if(it!=(numbers.end()-1)) {
                    it++;
                }else{it++;break;}
            }
            it--;
            arr.push_back(num);
            num.clear();
            continue;
        }
        if(opstack.empty()) {
            opstack.push(*it);
        }else {
            if(ismorepreor(opstack.top())>=ismorepreor(*it)) {
                while (!opstack.empty()) {
                    if (ismorepreor(opstack.top())>=ismorepreor(*it)) {
                        op.push_back(opstack.top());
                        arr.push_back(op);
                        op.clear();
                        opstack.pop();
                    } else {break;}
                }
                opstack.push(*it);
            }else {
                opstack.push(*it);
            }

        }
    }
    while(!opstack.empty()) {
        op.push_back(opstack.top());
        arr.push_back(op);
        op.clear();
        opstack.pop();
    }
    return arr;
}


double Game::calculate(string numbers) {\
    stack <double> numbstack;
    vector<string> arr = createarr(numbers);
    double numb1 , numb2 , result;
    for(auto it = arr.begin(); it != arr.end(); it++) {
        if(std::isdigit((*it)[0])) {
            numbstack.push(stod(*it));
        }else {
            numb1 = numbstack.top();
            numbstack.pop();
            numb2 = numbstack.top();
            numbstack.pop();
            if (*it == "+"){result = numb1 + numb2;}
            else if (*it == "-"){result = numb2 - numb1;}
            else if (*it == "*"){result = numb1 * numb2;}
            else if (*it == "/"){result = numb2 / numb1;}
            else if(*it == "^"){result = pow(numb2,numb1);}
            numbstack.push(result);
        }
        }
    result = numbstack.top();
    numbstack.pop();
    return result;
}









