#ifndef AI_H
#define AI_H

#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>

using namespace std;

struct Number {
    double value;
    int original_index; // -1, якщо це віртуальне число (результат)
    bool is_virtual;    // true, якщо це проміжний результат
};

struct Operation {
    char op;
    int original_index;
};

class AI {
private:
    // Рекурсивний пошук
    static double solveRecursive(vector<Number> nums, vector<Operation> ops, double target, int depth);

    static double safe_calc(double a, double b, char op, bool &valid);

public:
    static vector<int> findBestMove(vector<double> numbers, vector<char> ops, double target);
};

#endif //AI_H