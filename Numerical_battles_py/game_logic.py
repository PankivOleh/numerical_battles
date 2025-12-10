import PyAPI_py as api
from enum import Enum


class GameState(Enum):
    PLAYING = 1
    MERGE_CHOICE = 2
    CARD_SELECTION = 3
    SPECIAL_SELECTION = 4
    GAME_OVER = 5
    VICTORY = 6
    SETTINGS = 7


class GameLogic:
    def __init__(self, player_name, difficulty=1):
        self.player_name = player_name
        self.difficulty = difficulty
        self.level = 1
        self.max_level = 10

        # Зберігаємо hand у self, щоб Python не видалив його
        self.hand = api.Hand()
        self.player = api.Player(player_name, 100, 100, self.level, self.difficulty, self.hand)
        self.game = api.Game(self.player)
        self.game.set_hand()

        self.enemy = self.game.create_enemy()
        self.target_number = self.enemy.get_number()

        self.state = GameState.PLAYING

        # Списки для зберігання вибору
        self.selected_cards = []  # [(type, index, value)]
        self.selected_indices = {'numb': [], 'op': []}

        self.result_message = ""
        self.round_won = False

        self.available_choices = []
        self.selected_choice_indices = []
        self.max_regular_choices = 3
        self.max_special_choices = 1

    def get_hand_data(self):
        hand = self.player.get_hand()
        numb_cards = [hand.get_numb_card(i).get_numb() for i in range(hand.get_numb_count())]
        op_cards = [hand.get_operator_card(i).get_op() for i in range(hand.get_operator_count())]
        special_cards = [hand.get_special_card(i).get_numb() for i in range(hand.get_special_count())]
        return numb_cards, op_cards, special_cards

    def select_card(self, card_type, index):
        """Вибір карти з валідацією порядку (Число -> Оп -> Число)"""
        if self.state != GameState.PLAYING: return False

        # 1. Перевірка на повторний вибір тієї ж самої карти
        if card_type == 'numb' and index in self.selected_indices['numb']: return False
        if card_type == 'op' and index in self.selected_indices['op']: return False

        # 2. ВАЛІДАЦІЯ ПОРЯДКУ (Синтаксис)
        if not self.selected_cards:
            # Першою картою має бути ОБОВ'ЯЗКОВО число
            if card_type != 'numb':
                return False
        else:
            last_type = self.selected_cards[-1][0]

            # Не можна ставити число після числа (наприклад "6 7")
            if last_type == 'numb' and card_type == 'numb':
                return False

            # Не можна ставити оператор після оператора (наприклад "+ -")
            if last_type == 'op' and card_type == 'op':
                return False

        # Якщо все ок - додаємо
        hand = self.player.get_hand()

        if card_type == 'numb':
            if index < hand.get_numb_count():
                val = hand.get_numb_card(index).get_numb()
                self.selected_cards.append(('numb', index, val))
                self.selected_indices['numb'].append(index)
                return True
        elif card_type == 'op':
            if index < hand.get_operator_count():
                val = hand.get_operator_card(index).get_op()
                self.selected_cards.append(('op', index, val))
                self.selected_indices['op'].append(index)
                return True

        return False

    def deselect_new_card(self, index):
        """Знімає виділення з карти у вікні вибору"""
        if self.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]:
            if index in self.selected_choice_indices:
                self.selected_choice_indices.remove(index)
                return True
        return False

    def clear_new_selection(self):
        """Повністю очищає вибір нових карт"""
        if self.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]:
            self.selected_choice_indices.clear()
            return True
        return False


    def clear_selection(self):
        self.selected_cards = []
        self.selected_indices = {'numb': [], 'op': []}

    def build_expression(self):
        if not self.selected_cards: return ""
        expr = ""
        for i, (ctype, idx, val) in enumerate(self.selected_cards):
            # Захист від ділення на нуль при візуалізації
            if i > 0 and self.selected_cards[i - 1][2] == '/' and abs(float(val)) < 0.0001:
                return "Error"
            expr += str(val)
        return expr

    def calculate_result(self):
        """
        Тепер повертає True навіть при промаху (якщо це була валідна спроба),
        щоб гра могла рухатися далі.
        """
        # --- ВАЛІДАЦІЯ ---
        if not self.selected_cards: return False, "Виберіть карти!"

        if self.selected_cards[0][0] != 'numb' or self.selected_cards[-1][0] != 'numb':
            self.clear_selection()
            return False, "Вираз має починатися і закінчуватися числом!"

        for i in range(len(self.selected_cards) - 1):
            if self.selected_cards[i][0] == 'op' and self.selected_cards[i + 1][0] == 'op':
                self.clear_selection()
                return False, "Не можна ставити два оператори підряд!"

            # Перевірка ділення на нуль
            ctype, idx, val = self.selected_cards[i]
            if ctype == 'op' and str(val) == '/':
                next_val = self.selected_cards[i + 1][2]
                if abs(float(next_val)) < 0.0001:
                    self.clear_selection()
                    return False, "Ділення на нуль!"

        expr = self.build_expression()

        # --- ОБЧИСЛЕННЯ ---
        try:
            result = self.game.calculate(str(expr))

            if result == float('inf') or result == float('-inf') or result != result:
                self.clear_selection()
                return False, "Math Error!"

            check = self.game.check_number(result, self.target_number)

            # --- ВИПРАВЛЕННЯ ТУТ ---
            # Сортуємо індекси у зворотному порядку (наприклад: [2, 0] замість [0, 2])
            # Це гарантує, що видалення однієї карти не зсуне індекси інших.
            sorted_numb = sorted(self.selected_indices['numb'], reverse=True)
            sorted_op = sorted(self.selected_indices['op'], reverse=True)

            self.game.remove_cards(sorted_numb, sorted_op)

            self.clear_selection()

            if check == 0 or check == 1:
                # --- ПЕРЕМОГА В РАУНДІ ---
                self.round_won = True
                match_type = "=" if check == 0 else "≈"
                return True, f"Успіх! {result:.3f} {match_type} {self.target_number:.3f}"

            else:
                # --- ПРОМАХ (Але хід зараховано) ---
                self.player.set_hp(self.player.get_hp() - 10)
                self.round_won = False  # Це важливо: не дасть вибрати спецкарту

                if self.player.get_hp() <= 0:
                    self.state = GameState.GAME_OVER
                    return False, "Гра закінчена! HP вичерпано."

                # Повертаємо True, бо хід зроблено, але з повідомленням про втрату
                return True, f"Промах! -10 HP. {result:.3f} != {self.target_number:.3f}"

        except Exception as e:
            print(f"Error: {e}")
            self.clear_selection()
            return False, "Помилка обчислення!"

    def merge_cards(self, idx1, op_idx, idx2):
        if self.state != GameState.MERGE_CHOICE: return False, "Помилка стану"
        try:
            self.game.merge_cards(idx1, op_idx, idx2)
            self.clear_selection()

            # --- АВТОМАТИЧНИЙ ПЕРЕХІД ДАЛІ ---
            # Після злиття одразу переходимо до вибору нових карт
            self.start_card_selection()

            return True, "Злиття успішне!"
        except Exception as e:
            return False, str(e)


    def start_merge_phase(self):
        self.state = GameState.MERGE_CHOICE
        self.clear_selection()

    def merge_cards(self, idx1, op_idx, idx2):
        if self.state != GameState.MERGE_CHOICE: return False, "Помилка стану"
        try:
            self.game.merge_cards(idx1, op_idx, idx2)
            self.clear_selection()

            # --- АВТОМАТИЧНИЙ ПЕРЕХІД ДАЛІ ---
            # Після злиття одразу переходимо до вибору нових карт
            self.start_card_selection()

            return True, "Злиття успішне!"
        except Exception as e:
            return False, str(e)

    def use_special_card(self, index):
        if self.state != GameState.PLAYING: return False
        hand = self.player.get_hand()
        if index < hand.get_special_count():
            self.game.use_special_card(index)
            self.target_number = self.enemy.get_number()
            # Очищаємо вибір, щоб уникнути конфліктів індексів
            self.clear_selection()
            return True
        return False

    # ... методи для вибору нових карт залишаються без змін ...
    def skip_merge(self):
        self.start_card_selection()

    def start_card_selection(self):
        self.state = GameState.CARD_SELECTION
        self.available_choices = self.game.generate_choise()
        self.selected_choice_indices = []

    def select_new_card(self, index):
        limit = self.max_special_choices if self.state == GameState.SPECIAL_SELECTION else self.max_regular_choices
        if len(self.selected_choice_indices) < limit:
            if index not in self.selected_choice_indices:
                self.selected_choice_indices.append(index)
                return True
        return False

    def confirm_card_selection(self):
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
        self.state = GameState.SPECIAL_SELECTION
        self.available_choices = self.game.generate_special_choise()
        self.selected_choice_indices = []

    def next_round(self):
        self.level += 1
        if self.level > self.max_level:
            self.state = GameState.VICTORY
            return
        self.player.set_level(self.level)
        self.enemy = self.game.create_enemy()
        self.target_number = self.enemy.get_number()
        self.state = GameState.PLAYING
        self.clear_selection()
        self.round_won = False

    def get_choice_data(self):
        choices_data = []
        for card in self.available_choices:
            if hasattr(card, 'get_numb'):
                choices_data.append(('numb', card.get_numb()))
            elif hasattr(card, 'get_op'):
                choices_data.append(('op', card.get_op()))
        return choices_data