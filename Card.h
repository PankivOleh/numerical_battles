//
// Created by Admin on 20.09.2025.
//

#ifndef CARD_H
#define CARD_H
class Card {
private:
    bool in_hand = false;
public:
    Card();
    virtual Card* generate_card();
    virtual bool is_in_hand();
    virtual int use_card();
    virtual ~Card() = default;
};
class Operator_card: public Card {
    private:
    char op;
    public:
    Operator_card();
    Operator_card(char op);
    virtual Operator_card* generate_card() override;
    bool is_in_hand() override;
    int use_card() override;
    ~Operator_card() override = default;

};
class Numb_card: public Card {
    private:
    int number;
    public:
    Numb_card();
    Numb_card(int number);
    Numb_card* generate_card () override;
    Numb_card* merge_cards(Numb_card& card1 , Operator_card& card2);
    bool is_in_hand() override;
    int use_card() override;
    ~Numb_card() override = default;
};

class Special_card: public Card {
    int number;
public:
    Special_card();
    Special_card(int number);
    Special_card* generate_card() override;
    bool is_in_hand() override;
    int use_card() override;
    ~Special_card() override = default;
};
#endif //CARD_H
