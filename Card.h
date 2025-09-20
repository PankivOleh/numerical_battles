
#ifndef CARD_H
#define CARD_H
class Card {
private:
    bool in_hand = false;
public:
    Card();
    virtual Card* generate_card();
    bool is_in_hand();
    int use_card();
    virtual ~Card() = default;
    void set_in_hand();
};
class Operator_card: public Card {
    private:
    char op;
    public:
    Operator_card();
    Operator_card(char op);
    Operator_card* generate_card() override;
    ~Operator_card() override = default;
    char get_op();

};
class Numb_card: public Card {
    private:
    int number;
    public:
    Numb_card();
    Numb_card(int number);
    Numb_card* generate_card () override;
    int get_numb();
    ~Numb_card() override = default;
};

class Special_card: public Card {
    int number;
public:
    Special_card();
    Special_card(int number);
    Special_card* generate_card() override ;
    ~Special_card() override = default;
};
char rand_operator();
#endif //CARD_H
