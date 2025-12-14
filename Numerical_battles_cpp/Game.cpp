#include <iostream>
#include <stack>
#include "Game.h"
#include <cmath>
#include <algorithm>

using namespace std;

// методи не призначені для пайтону



double Game::generateFairTarget() {
    // 1. ПІДГОТОВКА (Отримуємо доступні карти)
    vector<double> base_numbers;
    vector<char> base_ops;

    auto num_hand = player->get_hand()->get_numb_hand();
    for (auto c : *num_hand) {
        if (c->is_in_hand()) base_numbers.push_back(c->get_numb());
    }

    auto op_hand = player->get_hand()->get_operator_hand();
    for (auto c : *op_hand) {
        if (c->is_in_hand()) base_ops.push_back(c->get_op());
    }

    // Захист на випадок порожньої руки
    if (base_numbers.size() < 2 || base_ops.empty()) {
        if (!base_numbers.empty()) return base_numbers[0];
        return 10.0;
    }

    int difficulty = player->get_difficult();

    // =============================================================
    // ЦИКЛ СПРОБ (RETRY LOOP)
    // Ми будемо пробувати генерувати приклад, доки не вийде "чистий"
    // =============================================================
    for (int attempt = 0; attempt < 50; attempt++) {

        // Робимо копії для цієї спроби
        vector<double> pool_nums = base_numbers;
        vector<char> pool_ops = base_ops;

        // Визначаємо кількість операторів
        int max_ops = std::min((int)pool_nums.size() - 1, (int)pool_ops.size());
        int ops_count = 1;

        if (difficulty == 1) ops_count = 1;
        else if (difficulty == 2) ops_count = 1 + (rand() % 2);
        else ops_count = 2 + (rand() % 3); // Hard: 2-4 оператори

        if (ops_count > max_ops) ops_count = max_ops;
        if (ops_count < 1) ops_count = 1;

        // --- БУДУЄМО ЛАНЦЮЖОК (Select) ---
        vector<double> sel_nums;
        vector<char> sel_ops;

        // Перше число
        int idx = rand() % pool_nums.size();
        sel_nums.push_back(pool_nums[idx]);
        pool_nums.erase(pool_nums.begin() + idx);

        for (int i = 0; i < ops_count; i++) {
            // Оператор
            int opIdx = rand() % pool_ops.size();
            sel_ops.push_back(pool_ops[opIdx]);
            pool_ops.erase(pool_ops.begin() + opIdx);

            // Наступне число
            int nIdx = rand() % pool_nums.size();
            sel_nums.push_back(pool_nums[nIdx]);
            pool_nums.erase(pool_nums.begin() + nIdx);
        }

        // --- РАХУЄМО (Calculate with Priority) ---
        // Якщо стається помилка -> valid = false
        bool valid = true;

        // 1. Високий пріоритет (^, *, /)
        for (size_t i = 0; i < sel_ops.size(); ) {
            char op = sel_ops[i];
            if (op == '*' || op == '/' || op == '^') {
                double v1 = sel_nums[i];
                double v2 = sel_nums[i+1];
                double res = 0;

                if (op == '*') {
                    res = v1 * v2;
                } else if (op == '/') {
                    if (std::abs(v2) < 0.001) { valid = false; break; } // Ділення на 0
                    res = v1 / v2;
                } else if (op == '^') {
                    // Жорстка перевірка на адекватність степеня
                    if (std::abs(v1) > 10 || std::abs(v2) > 6) { valid = false; break; }
                    // Перевірка на комплексні числа (корінь з від'ємного)
                    if (v1 < 0 && std::abs(v2) < 1 && v2 != 0) { valid = false; break; }

                    res = pow(v1, v2);
                }

                // Перевірка результату на переповнення
                if (std::isinf(res) || std::isnan(res) || std::abs(res) > 2000000) {
                    valid = false; break;
                }

                sel_nums[i] = res;
                sel_nums.erase(sel_nums.begin() + i + 1);
                sel_ops.erase(sel_ops.begin() + i);
            } else {
                i++;
            }
        }
        if (!valid) continue; // Ця спроба провалилась, пробуємо іншу комбінацію

        // 2. Низький пріоритет (+, -)
        double result = sel_nums[0];
        for (size_t i = 0; i < sel_ops.size(); i++) {
            char op = sel_ops[i];
            double v2 = sel_nums[i+1];
            if (op == '+') result += v2;
            else if (op == '-') result -= v2;
        }

        // Фінальна перевірка адекватності
        if (std::isinf(result) || std::isnan(result)) continue;

        // Округлення
        if (std::abs(result - std::round(result)) < 0.0001) {
            result = std::round(result);
        }

        // --- ANTI-CHEESE (Чи число вже є в руці?) ---
        // Якщо це не Easy, ми не хочемо давати відповідь, яка вже готова
        if (difficulty > 1) {
            bool exists = false;
            // Перевіряємо початковий пул
            for (double num : base_numbers) {
                if (std::abs(num - result) < 0.001) {
                    exists = true;
                    break;
                }
            }
            // Якщо число вже є в руці - це занадто просто, пробуємо інший приклад
            if (exists) continue;
        }

        // Якщо ми дійшли сюди - число ідеальне!
        return result;
    }

    // Якщо за 50 спроб не вдалося (дуже рідко), повертаємо просту суму перших двох
    if (base_numbers.size() >= 2) return base_numbers[0] + base_numbers[1];
    return base_numbers[0];
}

Player* Game::getPlayer() {
    return player;
}

int Game::generateN() {
    int n ;
    if(rand() & 1) {
        n = 6;
    }else {
        n = 4;
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
Enemy* Game::createEnemy() {
    // 1. Спочатку генеруємо "Чесну Ціль" (Fair Target)
    double fairTarget = this->generateFairTarget();

    // 2. Створюємо ворога вже з цим числом
    // (Старий ворог видаляється в cleanall або тут, якщо треба)
    if (this->enemy != nullptr) {
        delete this->enemy;
    }

    this->enemy = new Enemy(fairTarget);

    return this->enemy;
}


vector<Operator_card *> Game::generateOperatorChoise(int n) {
    vector<Operator_card *> ch;
    for(int i = 0; i < 10-n; i++) {
        Operator_card *c = new Operator_card();
        ch.push_back(c->generate_card());
    }
    return ch;
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
    int p;
    for(auto it  = numbers.begin(); it != numbers.end(); it++) {
        if(*it =='-'&&(!std::isdigit(*(it-1))||it==numbers.begin())) {
            num.push_back(*it);
            continue;
        }
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
Game::Game() {}
//методи для пайтону


vector<Special_card*>Game::generateSpecialChoise() {
    vector<Special_card *> ch;
    for(int i = 0; i < 3; i++) {
        Special_card *c = new Special_card();
        ch.push_back(c->generate_card());
    }
    return ch;
}
int Game::afterSpecialChoise(int n, vector<Special_card*> choices) {
    getPlayer()->get_hand()->add_special_card(*choices[n]);
    return 0;
}
vector<Card*> Game::generateChoise() {
    int n = generateN();
    vector<Operator_card *> ch = generateOperatorChoise(n);
    vector<Numb_card *> numb = generateNumbChoise(n);
    vector<Card*> pool;
    for(int i = 0; i < n; i++) {
        pool.push_back(numb[i]);
    }

    for(size_t i = 0; i < ch.size(); i++) {
        pool.push_back(ch[i]);
    }

    return pool;
}

int Game::afterChoise(int n  , vector<Card*> ch) {
    Card* c = (ch)[n];
    if (Numb_card* nc =  dynamic_cast<Numb_card*>(c)) {
        player->get_hand()->add_numb_card(*nc);
    } else if (Operator_card* oc = dynamic_cast<Operator_card*>(c)) {
        player->get_hand()->add_operator_card(*oc);
    }
    return 0;
}


Game::Game(Player *player) {
    srand(time(NULL));
    this->player = player;
    this->enemy = nullptr;
}

void Game::setHand() {
    getPlayer()->get_hand()->generate_hand();
}

void Game::mergeCard(int n1, int n2, int n3) {
    vector<Numb_card*>* v1 = player->get_hand()->get_numb_hand();
    vector<Operator_card*>* v2 = player->get_hand()->get_operator_hand();
    Numb_card* nc1 = (*v1)[n1];
    Numb_card* nc2 = (*v1)[n3];
    Operator_card* oc1 = (*v2)[n2];
    Numb_card newc = (this->getPlayer()->get_hand()->merge_cards(nc1,oc1,nc2));
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


int Game::checkNumber(double numb1, double numb2) {
    double difficult = this->getPlayer()->get_difficult();
    double dif = abs(numb1 - numb2);

    // Визначаємо допустиму похибку залежно від складності
    double tolerance = 0.0;

    if (difficult == 1) {
        tolerance = 2.5; // Easy: можна помилитися на ±2.5
    } else if (difficult == 2) {
        tolerance = 1.0; // Normal: похибка ±1
    } else {
        tolerance = 0.1; // Hard: майже ідеально
    }

    // Перевірка
    if (dif <= 0.001) {
        return 0; // Ідеально (JACKPOT!)
    }

    if (dif <= tolerance) {
        return 1; // Зараховано (Достатньо близько)
    }

    return -1; // Промах
}

void Game::useSpecial(int n) {
    int numb = this->getPlayer()->get_hand()->get_special_card(n)->get_numb();
    this->enemy->setNumber((double)numb);
    this->getPlayer()->get_hand()->get_special_card(n)->use_card();
    this->player->get_hand()->check_hand();
}


double Game::calculate(string numbers) {\
    stack <double> numbstack;
    vector<string> arr = createarr(numbers);
    double numb1 , numb2 , result;
    for(auto it = arr.begin(); it != arr.end(); it++) {
        if(std::isdigit((*it)[0])||std::isdigit((*it)[1])) {
            numbstack.push(stod(*it));
        }else {
            numb1 = numbstack.top();
            numbstack.pop();
            numb2 = numbstack.top();
            numbstack.pop();
            if (*it == "+"){result = numb1 + numb2;}
            else if (*it == "-"){result = numb2 - numb1;}
            else if (*it == "*"){result = numb1 * numb2;}
            else if (*it == "/"){
                if(fabs(numb1) < 0.0001) {
                    result = 0;
                } else {
                    result = numb2 / numb1;
                }
            }
            else if(*it == "^") {
                if(numb2<0&&numb1!=std::floor(numb1)) {
                    result = pow(numb2,floor(numb1));
                }
                else {
                    result = pow(numb2,numb1);
                }
            }
            numbstack.push(result);
        }
    }
    result = numbstack.top();
    numbstack.pop();
    return result;
}





void Game::cleanall() {
    if(enemy) {
        delete enemy;
        enemy = nullptr;
    }
    if(player&&player->get_hand()) {
        for(auto c:*player->get_hand()->get_numb_hand()) {
            delete c;
        }
        player->get_hand()->get_numb_hand()->clear();
        for(auto c:*player->get_hand()->get_operator_hand()) {
            delete c;
        }
        player->get_hand()->get_operator_hand()->clear();
        for(auto c:*player->get_hand()->get_special_hand()) {
            delete c;
        }
        player->get_hand()->get_special_hand()->clear();
    }
    delete player;
    player = nullptr;
}
void Game::removeCards(vector<int> numb_indices, vector<int> op_indices) {
    // 1. Отримуємо доступ до рук
    auto numb_hand = player->get_hand()->get_numb_hand();
    auto op_hand = player->get_hand()->get_operator_hand();

    // 2. Позначаємо карти чисел як використані
    for (int index : numb_indices) {
        // Перевірка меж, щоб не крашнулось
        if (index >= 0 && index < numb_hand->size()) {
            (*numb_hand)[index]->use_card(); // Ставить is_in_hand = false
        }
    }

    // 3. Позначаємо карти операторів як використані
    for (int index : op_indices) {
        if (index >= 0 && index < op_hand->size()) {
            (*op_hand)[index]->use_card(); // Ставить is_in_hand = false
        }
    }

    // 4. Фізично видаляємо "мертві" карти з векторів
    player->get_hand()->check_hand();
}








