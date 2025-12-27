#ifndef AI_H
#define AI_H

#include <vector>
#include <string>
#include "Card.h" // Або твої структури Number/Operation

using namespace std;

// Структури для зручності (можна залишити в .cpp, якщо вони там, але краще в .h)
struct Number {
    double value;
    int original_index; // -1, якщо це проміжний результат
    bool is_virtual;    // true, якщо це число - результат попередньої дії
};

struct Operation {
    char op;
    int original_index;
};

class AI {
public:
    static double safe_calc(double a, double b, char op, bool &valid);

    // Основна функція рекурсії тепер void, бо вона пише результат у змінну класу або передану посилання
    static void solveChain(vector<Number> nums, vector<Operation> ops, double target,
                           vector<int> current_path_indices,
                           vector<double> current_chain_nums, vector<char> current_chain_ops, vector<int> &best_path, double &best_diff);

    // Повертає вектор довільної довжини: [N1, Op1, N2, Op2, N3...]
    static vector<int> findBestMove(vector<double> numbers, vector<char> ops, double target);
};

#endif //AI_H