#include "AI.h"
#include <iostream>
#include <cmath>
#include <algorithm>
#include <vector>

const int MAX_CHECKS = 200000;
const double MAX_VAL = 100000.0;
static int checks_count = 0;

// Функція для безпечного обчислення двох чисел
double AI::safe_calc(double a, double b, char op, bool &valid) {
    valid = true;
    if (std::abs(a) > MAX_VAL || std::abs(b) > MAX_VAL) { valid = false; return 0; }

    double res = 0;
    switch (op) {
        case '+': res = a + b; break;
        case '-': res = a - b; break;
        case '*':
            if (std::abs(a) > 1 && std::abs(b) > MAX_VAL / std::abs(a)) { valid = false; return 0; }
            res = a * b; break;
        case '/':
            if (std::abs(b) < 0.01) { valid = false; return 0; }
            res = a / b; break;
        // Степінь прибираємо з пріоритетів для простоти, або обробляємо окремо.
        // В ланцюжках usually ^ has highest priority.
        case '^':
             if (std::abs(b) > 3.001) { valid = false; return 0; }
             if (b < 0) { valid = false; return 0; }
             res = std::pow(a, b); break;
        default: valid = false; return 0;
    }

    if (std::isinf(res) || std::isnan(res)) { valid = false; return 0; }
    return res;
}

// === НОВА ФУНКЦІЯ: Рахує вираз з урахуванням пріоритетів (* / перші) ===
double calculate_with_priority(vector<double> nums, vector<char> ops, bool &valid) {
    valid = true;
    if (nums.empty()) return 0;
    if (ops.empty()) return nums[0];

    // КРОК 1: Виконуємо * та / та ^
    // Ми проходимось і "схлопуємо" множення/ділення
    for (size_t i = 0; i < ops.size(); ) {
        char op = ops[i];
        if (op == '*' || op == '/' || op == '^') {
            bool v = false;
            double res = AI::safe_calc(nums[i], nums[i+1], op, v);
            if (!v) { valid = false; return 0; }

            // Записуємо результат на місце лівого числа
            nums[i] = res;
            // Видаляємо праве число і оператор
            nums.erase(nums.begin() + i + 1);
            ops.erase(ops.begin() + i);
            // i не збільшуємо, бо ми маємо перевірити новий оператор, який змістився на це місце
        } else {
            i++;
        }
    }

    // КРОК 2: Виконуємо + та - (зліва направо)
    double result = nums[0];
    for (size_t i = 0; i < ops.size(); ++i) {
        bool v = false;
        result = AI::safe_calc(result, nums[i+1], ops[i], v);
        if (!v) { valid = false; return 0; }
    }

    return result;
}

// Рекурсія тепер не рахує current_val, а накопичує список
void AI::solveChain(vector<Number> nums, vector<Operation> ops, double target,
                    vector<int> current_path_indices,
                    vector<double> current_chain_nums,
                    vector<char> current_chain_ops,
                    vector<int>& best_path, double& best_diff) {

    checks_count++;
    if (checks_count > MAX_CHECKS) return;

    // 1. Оцінюємо поточний ланцюжок (якщо в ньому є хоча б 1 операція)
    if (!current_chain_ops.empty()) {
        bool valid = false;
        double val = calculate_with_priority(current_chain_nums, current_chain_ops, valid);

        if (valid) {
            double diff = std::abs(val - target);
            if (diff < best_diff) {
                best_diff = diff;
                best_path = current_path_indices;
                if (best_diff < 0.0001) return; // Ідеал
            }
        }
    }

    // Якщо карти закінчились
    if (ops.empty() || nums.empty()) return;

    // 2. Пробуємо додати до ланцюжка
    // Ланцюжок виглядає так: Num1 Op1 Num2 Op2 Num3...
    // Нам треба додати Op і Num

    for (size_t k = 0; k < ops.size(); ++k) {
        for (size_t i = 0; i < nums.size(); ++i) {

            // Формуємо нові списки для рекурсії
            vector<double> next_chain_nums = current_chain_nums;
            next_chain_nums.push_back(nums[i].value);

            vector<char> next_chain_ops = current_chain_ops;
            next_chain_ops.push_back(ops[k].op);

            // Швидка перевірка: якщо останній оператор був / або ^, перевіримо валідність зразу,
            // щоб не заглиблюватись у ділення на нуль
            if (ops[k].op == '/' && std::abs(nums[i].value) < 0.01) continue;

            // Оновлюємо шляхи
            vector<int> next_path_indices = current_path_indices;
            next_path_indices.push_back(ops[k].original_index);
            next_path_indices.push_back(nums[i].original_index);

            // Видаляємо використані карти з пулу
            vector<Number> next_pool_nums = nums;
            next_pool_nums.erase(next_pool_nums.begin() + i);

            vector<Operation> next_pool_ops = ops;
            next_pool_ops.erase(next_pool_ops.begin() + k);

            // Йдемо глибше
            solveChain(next_pool_nums, next_pool_ops, target,
                       next_path_indices, next_chain_nums, next_chain_ops,
                       best_path, best_diff);

            if (best_diff < 0.0001 && checks_count > 10000) return;
        }
    }
}

vector<int> AI::findBestMove(vector<double> numbers, vector<char> ops, double target) {
    checks_count = 0;
    if (numbers.size() < 2 || ops.empty()) return {};

    vector<Number> num_structs;
    for(size_t i=0; i<numbers.size(); ++i) num_structs.push_back({numbers[i], (int)i, false});

    vector<Operation> op_structs;
    for(size_t i=0; i<ops.size(); ++i) op_structs.push_back({ops[i], (int)i});

    vector<int> best_path;
    double best_diff = 999999.0;

    // === ЕТАП 1: ГАРАНТОВАНИЙ ХІД (БАЗОВИЙ) ===
    // Швидко перевіряємо прості пари (A op B), щоб мати хоч якийсь варіант про запас
    for (size_t i = 0; i < num_structs.size(); ++i) {
        for (size_t j = 0; j < num_structs.size(); ++j) {
            if (i == j) continue;
            for (size_t k = 0; k < op_structs.size(); ++k) {
                bool valid = false;
                double res = safe_calc(num_structs[i].value, num_structs[j].value, op_structs[k].op, valid);

                if (valid) {
                    double diff = std::abs(res - target);
                    if (diff < best_diff) {
                        best_diff = diff;
                        best_path = { num_structs[i].original_index, op_structs[k].original_index, num_structs[j].original_index };
                    }
                }
            }
        }
    }

    // Якщо ми знайшли ідеальний хід (прямо в ціль) вже тут - повертаємо його
    if (best_diff < 0.0001) return best_path;


    // === ЕТАП 2: ГЛИБОКИЙ ПОШУК (ЛАНЦЮЖКИ) ===
    // Тільки тепер запускаємо важку рекурсію, щоб спробувати покращити результат
    checks_count = 0; // Скидаємо лічильник для чесності

    for (size_t i = 0; i < num_structs.size(); ++i) {
        if (checks_count > MAX_CHECKS) break; // Виходимо, якщо ліміт

        vector<double> start_nums = { num_structs[i].value };
        vector<char> start_ops = {};
        vector<int> start_indices = { num_structs[i].original_index };

        vector<Number> pool_nums = num_structs;
        pool_nums.erase(pool_nums.begin() + i);

        solveChain(pool_nums, op_structs, target,
                   start_indices, start_nums, start_ops,
                   best_path, best_diff); // best_path оновиться тільки якщо знайдемо щось краще

        if (best_diff < 0.0001) break;
    }

    return best_path;
}