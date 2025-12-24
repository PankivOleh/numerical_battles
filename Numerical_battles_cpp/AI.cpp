#include "AI.h"
#include <iostream>
#include <cmath>
#include <algorithm>

// Зменшуємо глибину до 4 (цього достатньо для 99% задач, але це рятує від крашів)
const int MAX_DEPTH = 4;
const int MAX_CHECKS = 80000; // Зменшуємо ліміт операцій
const double MAX_VAL = 100000.0; // Числа більше цього вважаються помилкою

static int checks_count = 0;

double AI::safe_calc(double a, double b, char op, bool &valid) {
    valid = true;
    double res = 0;

    // 1. Попередній захист від величезних чисел
    if (std::abs(a) > MAX_VAL || std::abs(b) > MAX_VAL) { valid = false; return 0; }

    switch (op) {
        case '+':
            res = a + b;
            break;
        case '-':
            res = a - b;
            break;
        case '*':
            // Перевірка на переповнення при множенні
            if (std::abs(a) > 1 && std::abs(b) > MAX_VAL / std::abs(a)) { valid = false; return 0; }
            res = a * b;
            break;
        case '/':
            // Захист від ділення на нуль і занадто малих чисел (що дають величезний результат)
            if (std::abs(b) < 0.01) { valid = false; return 0; }
            res = a / b;
            break;
        case '^':
            // ЖОРСТКИЙ ЗАХИСТ СТЕПЕНЯ
            // Дозволяємо тільки маленькі степені, бо це найчастіша причина крашу
            if (std::abs(b) > 3.001) { valid = false; return 0; } // Максимум куб
            if (std::abs(a) > 20) { valid = false; return 0; }
            if (b < 0) { valid = false; return 0; } // Жодних дробів у степені для безпеки

            res = std::pow(a, b);
            break;
        default: valid = false; return 0;
    }

    // 2. Фінальна перевірка результату
    if (std::isinf(res) || std::isnan(res) || std::abs(res) > MAX_VAL) {
        valid = false;
        return 0;
    }

    return res;
}

double AI::solveRecursive(vector<Number> nums, vector<Operation> ops, double target, int depth) {
    checks_count++;
    // Аварійний вихід, якщо зациклились
    if (checks_count > MAX_CHECKS) return 999999.0;

    // Базовий випадок: чи є ціль?
    double best_diff = 999999.0;
    for (const auto& n : nums) {
        double diff = std::abs(n.value - target);
        if (diff < best_diff) best_diff = diff;
        if (best_diff < 0.001) return 0.0;
    }

    if (depth >= MAX_DEPTH || nums.size() < 2 || ops.empty()) {
        return best_diff;
    }

    for (size_t i = 0; i < nums.size(); ++i) {
        for (size_t j = 0; j < nums.size(); ++j) {
            if (i == j) continue;

            // ЛІНІЙНЕ ОБМЕЖЕННЯ (Гравець має продовжувати ланцюжок)
            bool has_virtual = false;
            for(const auto& n : nums) if(n.is_virtual) has_virtual = true;
            if (has_virtual) {
                if (!nums[i].is_virtual && !nums[j].is_virtual) continue;
            }

            for (size_t k = 0; k < ops.size(); ++k) {
                bool valid = false;
                double res = safe_calc(nums[i].value, nums[j].value, ops[k].op, valid);

                if (!valid) continue;

                // Створення копій векторів - найважча операція для пам'яті.
                // Ми робимо це тільки якщо валідація пройшла.
                vector<Number> next_nums;
                next_nums.reserve(nums.size() - 1); // Оптимізація пам'яті

                // Розумне копіювання
                for(size_t idx = 0; idx < nums.size(); ++idx) {
                    if(idx != i && idx != j) next_nums.push_back(nums[idx]);
                }
                // Додаємо результат
                next_nums.push_back({res, -1, true});

                vector<Operation> next_ops = ops;
                next_ops.erase(next_ops.begin() + k);

                double path_diff = solveRecursive(next_nums, next_ops, target, depth + 1);

                if (path_diff < best_diff) best_diff = path_diff;
                if (best_diff < 0.001) return 0.0;

                // Додатковий вихід, щоб не продовжувати, якщо час вичерпано
                if (checks_count > MAX_CHECKS) return best_diff;
            }
        }
    }
    return best_diff;
}

vector<int> AI::findBestMove(vector<double> numbers, vector<char> ops, double target) {
    checks_count = 0; // Скидаємо лічильник

    // Захист від порожніх даних
    if (numbers.size() < 2 || ops.empty()) return {-1, -1, -1};

    vector<Number> num_structs;
    num_structs.reserve(numbers.size());
    for(size_t i=0; i<numbers.size(); ++i) num_structs.push_back({numbers[i], (int)i, false});

    vector<Operation> op_structs;
    op_structs.reserve(ops.size());
    for(size_t i=0; i<ops.size(); ++i) op_structs.push_back({ops[i], (int)i});

    int best_n1 = -1, best_op = -1, best_n2 = -1;
    double best_scenario_diff = 999999.0;

    // Глобальний try-catch на випадок збою пам'яті STL
    try {
        for (size_t i = 0; i < num_structs.size(); ++i) {
            for (size_t j = 0; j < num_structs.size(); ++j) {
                if (i == j) continue;

                for (size_t k = 0; k < op_structs.size(); ++k) {

                    if (checks_count > MAX_CHECKS) {
                        // Повертаємо, що встигли знайти
                        if (best_n1 != -1) return {best_n1, best_op, best_n2};
                        return {-1, -1, -1};
                    }

                    bool valid = false;
                    double val = safe_calc(num_structs[i].value, num_structs[j].value, op_structs[k].op, valid);
                    if (!valid) continue;

                    if (std::abs(val - target) < 0.001) {
                        return {num_structs[i].original_index, op_structs[k].original_index, num_structs[j].original_index};
                    }

                    // Підготовка наступного кроку
                    vector<Number> future_nums;
                    future_nums.reserve(num_structs.size() - 1);
                    for(size_t idx = 0; idx < num_structs.size(); ++idx) {
                        if(idx != i && idx != j) future_nums.push_back(num_structs[idx]);
                    }
                    future_nums.push_back({val, -1, true});

                    vector<Operation> future_ops = op_structs;
                    future_ops.erase(future_ops.begin() + k);

                    double potential = solveRecursive(future_nums, future_ops, target, 1);

                    if (potential < best_scenario_diff) {
                        best_scenario_diff = potential;
                        best_n1 = num_structs[i].original_index;
                        best_n2 = num_structs[j].original_index;
                        best_op = op_structs[k].original_index;
                    }
                }
            }
        }
    } catch (...) {
        // Ловимо будь-який краш і просто пропускаємо хід
        return {-1, -1, -1};
    }

    return {best_n1, best_op, best_n2};
}