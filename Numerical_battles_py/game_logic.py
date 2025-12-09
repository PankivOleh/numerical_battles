import PyAPI_py as api
from enum import Enum


class GameState(Enum):
    PLAYING = 1
    MERGE_CHOICE = 2
    CARD_SELECTION = 3
    SPECIAL_SELECTION = 4
    GAME_OVER = 5
    VICTORY = 6


class GameLogic:
    def __init__(self, player_name, difficulty=1):
        self.player_name = player_name
        self.difficulty = difficulty
        self.level = 1
        self.max_level = 10

        # Створення гравця
        self.hand = api.Hand()
        self.player = api.Player(player_name, 100, 100, self.level, self.difficulty, self.hand)
        self.game = api.Game(self.player)
        self.game.set_hand()

        # Створення ворога
        self.enemy = self.game.create_enemy()
        self.target_number = self.enemy.get_number()

        # Стан гри
        self.state = GameState.PLAYING
        self.selected_cards = []  # [(type, index, value)]
        self.selected_indices = {'numb': [], 'op': []}
        self.result_message = ""
        self.round_won = False

        # Вибір карт
        self.available_choices = []
        self.selected_choice_indices = []
        self.max_regular_choices = 3
        self.max_special_choices = 1

    def get_hand_data(self):
        """Повертає дані про карти в руці"""
        hand = self.player.get_hand()

        numb_cards = []
        for i in range(hand.get_numb_count()):
            card = hand.get_numb_card(i)
            numb_cards.append(card.get_numb())

        op_cards = []
        for i in range(hand.get_operator_count()):
            card = hand.get_operator_card(i)
            op_cards.append(card.get_op())

        special_cards = []
        for i in range(hand.get_special_count()):
            card = hand.get_special_card(i)
            special_cards.append(card.get_numb())

        return numb_cards, op_cards, special_cards

    def select_card(self, card_type, index):
        """Вибір карти для обчислення"""
        if self.state != GameState.PLAYING:
            return False

        hand = self.player.get_hand()

        if card_type == 'numb':
            if index < hand.get_numb_count():
                card = hand.get_numb_card(index)
                value = card.get_numb()
                self.selected_cards.append(('numb', index, value))
                self.selected_indices['numb'].append(index)
                return True
        elif card_type == 'op':
            if index < hand.get_operator_count():
                card = hand.get_operator_card(index)
                value = card.get_op()
                self.selected_cards.append(('op', index, value))
                self.selected_indices['op'].append(index)
                return True

        return False

    def use_special_card(self, index):
        """Використання спеціальної карти"""
        if self.state != GameState.PLAYING:
            return False

        hand = self.player.get_hand()
        if index < hand.get_special_count():
            self.game.use_special_card(index)
            self.target_number = self.enemy.get_number()
            return True
        return False

    def clear_selection(self):
        """Очистити вибрані карти"""
        self.selected_cards = []
        self.selected_indices = {'numb': [], 'op': []}

    def build_expression(self):
        """Побудова математичного виразу з вибраних карт"""
        if not self.selected_cards:
            return ""

        expr = ""
        for i, (card_type, index, value) in enumerate(self.selected_cards):
            if card_type == 'numb':
                # Перевірка на нуль перед операцією ділення
                if i > 0 and self.selected_cards[i - 1][0] == 'op' and self.selected_cards[i - 1][2] == '/':
                    if abs(value) < 0.0001:  # Практично нуль
                        return ""  # Повертаємо порожній рядок щоб заблокувати обчислення
                expr += str(value)
            else:
                expr += str(value)

        return expr

    def calculate_result(self):
        """Обчислення результату та перевірка"""
        if not self.selected_cards:
            return False, "Виберіть карти!"

        # Перевірка правильності послідовності
        if len(self.selected_cards) < 1:
            return False, "Потрібна хоча б одна карта!"

        # Перевірка що починається і закінчується числом
        if self.selected_cards[0][0] != 'numb' or self.selected_cards[-1][0] != 'numb':
            return False, "Вираз має починатися та закінчуватися числом!"

        # Перевірка чергування
        for i in range(len(self.selected_cards) - 1):
            if self.selected_cards[i][0] == self.selected_cards[i + 1][0]:
                return False, "Неправильна послідовність! Чергуйте числа та операції!"

        # Детальна перевірка на ділення на нуль
        for i in range(len(self.selected_cards) - 1):
            if self.selected_cards[i][0] == 'op' and self.selected_cards[i][2] == '/':
                # Перевіряємо наступну карту (має бути число)
                if i + 1 < len(self.selected_cards):
                    next_value = self.selected_cards[i + 1][2]
                    if abs(next_value) < 0.0001:  # Практично нуль
                        return False, "Ділення на нуль неможливе!"

        expr = self.build_expression()

        # Якщо вираз порожній (заблоковано через нуль)
        if not expr:
            return False, "Ділення на нуль неможливе!"

        try:
            result = self.game.calculate(expr)

            # Перевірка на NaN або Infinity
            if result != result or abs(result) == float('inf'):
                return False, "Некоректний результат обчислення!"

            check = self.game.check_number(result, self.target_number)

            # Видаляємо використані карти
            self.game.remove_cards(
                self.selected_indices['numb'],
                self.selected_indices['op']
            )

            if check == 0:
                self.result_message = f"Ідеально! {result} = {self.target_number}"
                self.round_won = True
                return True, self.result_message
            elif check == 1:
                self.result_message = f"Близько! {result} ≈ {self.target_number}"
                self.round_won = True
                return True, self.result_message
            else:
                self.result_message = f"Промах! {result} далеко від {self.target_number}"
                self.player.set_hp(self.player.get_hp() - 10)
                self.round_won = False

                if self.player.get_hp() <= 0:
                    self.state = GameState.GAME_OVER
                    return False, "Гра закінчена! HP = 0"

                return False, self.result_message
        except Exception as e:
            return False, f"Помилка обчислення: {str(e)}"

    def start_merge_phase(self):
        """Початок фази об'єднання карт"""
        self.state = GameState.MERGE_CHOICE
        self.clear_selection()

    def merge_cards(self, numb1_idx, op_idx, numb2_idx):
        """Об'єднання трьох карт"""
        if self.state != GameState.MERGE_CHOICE:
            return False, "Не час для об'єднання!"

        try:
            # +1 бо в С++ функція віднімає 1
            self.game.merge_cards(numb1_idx, op_idx , numb2_idx )
            return True, "Карти об'єднано!"
        except Exception as e:
            return False, f"Помилка об'єднання: {str(e)}"

    def skip_merge(self):
        """Пропустити фазу об'єднання"""
        self.start_card_selection()

    def start_card_selection(self):
        """Початок вибору нових карт"""
        self.state = GameState.CARD_SELECTION
        self.available_choices = self.game.generate_choise()
        self.selected_choice_indices = []

    def select_new_card(self, index):
        """Вибір нової карти з пропозиції"""
        if self.state == GameState.CARD_SELECTION:
            if len(self.selected_choice_indices) < self.max_regular_choices:
                if index not in self.selected_choice_indices:
                    self.selected_choice_indices.append(index)
                    return True
        elif self.state == GameState.SPECIAL_SELECTION:
            if len(self.selected_choice_indices) < self.max_special_choices:
                if index not in self.selected_choice_indices:
                    self.selected_choice_indices.append(index)
                    return True
        return False

    def confirm_card_selection(self):
        """Підтвердження вибору карт"""
        if self.state == GameState.CARD_SELECTION:
            for idx in self.selected_choice_indices:
                self.game.after_choise(idx, self.available_choices)

            if self.round_won:
                self.start_special_selection()
            else:
                self.next_round()

        elif self.state == GameState.SPECIAL_SELECTION:
            for idx in self.selected_choice_indices:
                self.game.after_special_choise(idx, self.available_choices)

            self.next_round()

    def start_special_selection(self):
        """Початок вибору спеціальних карт"""
        self.state = GameState.SPECIAL_SELECTION
        self.available_choices = self.game.generate_special_choise()
        self.selected_choice_indices = []

    def next_round(self):
        """Наступний раунд"""
        self.level += 1

        if self.level > self.max_level:
            self.state = GameState.VICTORY
            return

        self.player.set_level(self.level)
        self.enemy = self.game.create_enemy()
        self.target_number = self.enemy.get_number()
        self.state = GameState.PLAYING
        self.clear_selection()
        self.result_message = ""
        self.round_won = False

    def get_choice_data(self):
        """Отримати дані про доступні карти для вибору"""
        choices_data = []
        for i, card in enumerate(self.available_choices):
            if hasattr(card, 'get_numb'):
                choices_data.append(('numb', card.get_numb()))
            elif hasattr(card, 'get_op'):
                choices_data.append(('op', card.get_op()))
        return choices_data

    def restart_game(self):
        """Перезапуск гри"""
        self.game.cleanall()
        self.__init__(self.player_name, self.difficulty)