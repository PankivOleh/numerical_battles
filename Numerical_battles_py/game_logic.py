import PyAPI_py as api
from enum import Enum
from settings import *


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
        self.max_hand_size = 10  # Максимальний розмір руки
        self.cards_needed = 0

        # Зберігаємо hand у self, щоб Python не видалив його
        self.hand = api.Hand()
        self.player = api.Player(player_name, 100, 100, self.level, self.difficulty, self.hand)
        self.game = api.Game(self.player)
        self.game.set_hand()

        # Генеруємо першого ворога (відразу чесного, бо ми виправили C++)
        self.enemy = self.game.create_enemy()
        self.target_number = self.enemy.get_number()

        self.state = GameState.PLAYING

        # --- ВАЖЛИВО: Прапорець для виходу з глухого кута ---
        self.is_deadlock_recovery = False
        # ----------------------------------------------------

        # Списки для зберігання вибору
        self.selected_cards = []
        self.selected_indices = {'numb': [], 'op': []}

        self.result_message = ""
        self.round_won = False

        self.available_choices = []
        self.selected_choice_indices = []
        self.max_regular_choices = 3
        self.max_special_choices = 1

    def make_ai_turn(self):
        """
        Автоматичний хід бота. Повертає True, якщо хід зроблено.
        """
        # 1. Отримуємо дані для C++
        numb_data, op_data, _ = self.get_hand_data()

        # 2. Питаємо C++, що робити
        # move = [idx_n1, idx_op, idx_n2]
        try:
            move = api.AI.find_best_move(numb_data, op_data, self.target_number)
        except Exception as e:
            print(f"AI Error: {e}")
            return False

        idx_n1, idx_op, idx_n2 = move[0], move[1], move[2]

        # 3. Виконуємо хід, якщо він валідний
        if idx_n1 != -1:
            print(f"[AI] Bot decided: {numb_data[idx_n1]} {op_data[idx_op]} {numb_data[idx_n2]}")
            self.clear_selection()

            # Послідовність важлива!
            self.select_card('numb', idx_n1)
            self.select_card('op', idx_op)
            self.select_card('numb', idx_n2)

            return True
        else:
            print("[AI] I give up! Skipping turn...")
            return False


    def start_card_selection(self):
        self.state = GameState.CARD_SELECTION

        # Отримуємо 10 карток з C++ (ти вже це зробив там)
        self.available_choices = self.game.generate_choise()
        self.selected_choice_indices = []

        # --- РОЗУМНИЙ ЛІМІТ ---
        # Рахуємо поточні карти
        hand = self.player.get_hand()
        current_count = hand.get_numb_count() + hand.get_operator_count()

        # Скільки не вистачає до повної руки?
        self.cards_needed = self.max_hand_size - current_count

        # Захист: якщо карт 0 (на всякий випадок), беремо мінімум 5
        if self.cards_needed < 3: self.cards_needed = 3
        # Захист: не можемо взяти більше, ніж пропонує драфт (10)
        if self.cards_needed > len(self.available_choices):
            self.cards_needed = len(self.available_choices)



    def check_deadlock(self):
        """
        Перевіряє, чи може гравець зробити хід.
        """
        try:
            if self.player is None or self.player.get_hand() is None:
                return False, ""

            numb_count = self.player.get_hand().get_numb_count()

            if numb_count < 2:
                # Штраф
                penalty = 5

                # Перевірка життя
                if self.player.get_hp() <= 0:
                    self.state = GameState.GAME_OVER
                    return True, "HP вичерпано."

                self.player.set_hp(-penalty)

                if self.player.get_hp() <= 0:
                    self.state = GameState.GAME_OVER
                    return True, "Глухий кут! HP вичерпано."

                # Перехід до вибору (ПОРЯТУНОК)
                if self.game:
                    self.choices = self.game.generate_choise()  # Генеруємо для внутрішнього використання
                    self.available_choices = self.choices  # Синхронізуємо з Python
                    self.selected_choice_indices = []

                    self.state = GameState.CARD_SELECTION
                    self.is_deadlock_recovery = True  # <--- Вмикаємо режим порятунку

                    return True, f"Немає ходів! -{penalty} HP. Доберіть карти."

            return False, ""

        except Exception as e:
            print(f"Warning: Deadlock check skipped due to: {e}")
            return False, ""

    def regenerate_target(self):
        enemy = self.game.create_enemy()
        self.target_number = enemy.get_number()

    def get_hand_data(self):
        hand = self.player.get_hand()
        numb_cards = [hand.get_numb_card(i).get_numb() for i in range(hand.get_numb_count())]
        op_cards = [hand.get_operator_card(i).get_op() for i in range(hand.get_operator_count())]
        special_cards = [hand.get_special_card(i).get_numb() for i in range(hand.get_special_count())]
        return numb_cards, op_cards, special_cards

    def select_card(self, card_type, index):
        if self.state != GameState.PLAYING: return False
        if card_type == 'numb' and index in self.selected_indices['numb']: return False
        if card_type == 'op' and index in self.selected_indices['op']: return False

        # Валідація порядку
        if not self.selected_cards:
            if card_type != 'numb': return False
        else:
            last_type = self.selected_cards[-1][0]
            if last_type == 'numb' and card_type == 'numb': return False
            if last_type == 'op' and card_type == 'op': return False

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

    def clear_selection(self):
        self.selected_cards = []
        self.selected_indices = {'numb': [], 'op': []}

    def build_expression(self):
        if not self.selected_cards: return ""
        expr = ""
        for i, (ctype, idx, val) in enumerate(self.selected_cards):
            if i > 0 and self.selected_cards[i - 1][2] == '/' and abs(float(val)) < 0.0001:
                return "Error"
            expr += str(val)
        return expr

    def preview_calculation(self):
        if not self.selected_cards: return False, "Виберіть карти!"
        count = len(self.selected_cards)

        if count == 1:
            if self.selected_cards[0][0] != 'numb':
                self.clear_selection()
                return False, "Оператор сам по собі не працює!"
        elif count == 2:
            self.clear_selection()
            return False, "Неповний вираз!"
        else:
            if self.selected_cards[0][0] != 'numb' or self.selected_cards[-1][0] != 'numb':
                self.clear_selection()
                return False, "Вираз має починатися і закінчуватися числом!"

            for i in range(len(self.selected_cards) - 1):
                if self.selected_cards[i][0] == 'op' and self.selected_cards[i + 1][0] == 'op':
                    self.clear_selection()
                    return False, "Два оператори підряд!"

                ctype, idx, val = self.selected_cards[i]
                if ctype == 'op' and str(val) == '/':
                    next_val = self.selected_cards[i + 1][2]
                    if abs(float(next_val)) < 0.0001:
                        self.clear_selection()
                        return False, "Ділення на нуль!"

        expr = self.build_expression()
        try:
            result = self.game.calculate(str(expr))
            if result == float('inf') or result == float('-inf') or result != result:
                self.clear_selection()
                return False, "Math Error!"
            return True, result
        except Exception as e:
            print(f"Error: {e}")
            self.clear_selection()
            return False, "Помилка обчислення!"

    def apply_turn_result(self, result_value):
        check = self.game.check_number(result_value, self.target_number)

        sorted_numb = sorted(self.selected_indices['numb'], reverse=True)
        sorted_op = sorted(self.selected_indices['op'], reverse=True)
        self.game.remove_cards(sorted_numb, sorted_op)
        self.clear_selection()

        msg = ""
        success_state = False

        if check == 0 or check == 1:
            self.round_won = True
            match_type = "=" if check == 0 else "≈"
            msg = f"Успіх! {result_value:.3f} {match_type} {self.target_number:.3f}"
            self.game.add_log(f"HIT: {self.player_name} ({msg})")
            success_state = True
        else:
            self.player.set_hp(-10)
            self.round_won = False
            if self.player.get_hp() <= 0:
                self.state = GameState.GAME_OVER
                msg = "Гра закінчена! HP вичерпано."
                return False, msg
            msg = f"Промах! -10 HP. {result_value:.3f} != {self.target_number:.3f}"
            self.game.add_log(f"MISS: {self.player_name} (-10HP)")
            success_state = True

        return success_state, msg

    def start_merge_phase(self):
        self.state = GameState.MERGE_CHOICE
        self.clear_selection()

    def merge_cards(self, idx1, op_idx, idx2):
        if self.state != GameState.MERGE_CHOICE: return False, "Помилка стану"
        try:
            self.game.merge_cards(idx1, op_idx, idx2)
            self.clear_selection()
            self.start_card_selection()
            return True, "Злиття успішне!"
        except Exception as e:
            return False, str(e)

    def skip_merge(self):
        self.start_card_selection()

    def start_card_selection(self):
        self.state = GameState.CARD_SELECTION
        # Отримуємо пул з 10 карт (від C++)
        self.available_choices = self.game.generate_choise()
        self.selected_choice_indices = []

        # --- ЖОРСТКИЙ ЛІМІТ ---
        # Гравець може вибрати до 6 карт.
        # Ніякого поповнення до максимуму, просто фіксоване число.
        self.selection_limit = 6

    def select_new_card(self, index):
        # Визначаємо ліміт залежно від режиму
        if self.state == GameState.SPECIAL_SELECTION:
            limit = self.max_special_choices  # Зазвичай 1
        else:
            limit = self.selection_limit  # Тепер це 6

        # Перевірка: чи не досягли ми ліміту?
        if len(self.selected_choice_indices) < limit:
            # Додаємо, якщо ще не вибрано
            if index not in self.selected_choice_indices:
                self.selected_choice_indices.append(index)
                return True
        return False


    def deselect_new_card(self, index):
        if self.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]:
            if index in self.selected_choice_indices:
                self.selected_choice_indices.remove(index)
                return True
        return False

    def clear_new_selection(self):
        if self.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]:
            self.selected_choice_indices.clear()
            return True
        return False

    def confirm_card_selection(self):
        """
        Підтверджує вибір карт і перемикає стан.
        """
        if self.state == GameState.CARD_SELECTION:
            # 1. Додаємо вибрані карти в руку
            for idx in self.selected_choice_indices:
                self.game.after_choise(idx, self.available_choices)

            # 2. Логіка переходів
            if self.is_deadlock_recovery:
                # Якщо рятувалися від глухого кута -> повертаємося в гру
                self.state = GameState.PLAYING
                self.is_deadlock_recovery = False
                self.round_won = False
                # При дедлоку ціль можна не міняти, або змінити - на твій розсуд.
                # Якщо хочеш міняти і тут - розкоментуй рядок нижче:
                # self.regenerate_target()

            elif self.round_won:
                # Перемога -> йдемо за нагородою
                self.start_special_selection()

            else:
                # === ПРОМАХ (Гра продовжується на цьому ж рівні) ===
                self.state = GameState.PLAYING
                self.round_won = False

                # === ГОЛОВНА ЗМІНА ===
                # Генеруємо нову ціль, щоб гравцю не було нудно з тим самим числом
                self.regenerate_target()

        elif self.state == GameState.SPECIAL_SELECTION:
            # Вибір спецкарти (нагорода за перемогу)
            for idx in self.selected_choice_indices:
                self.game.after_special_choise(idx, self.available_choices)

            # Переходимо на наступний рівень
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

        self.game.add_log(f"--- Round {self.level} Started ---")

        self.player.set_level(self.level)

        # Створюємо ворога (він вже розумний завдяки C++)
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

    def use_special_card(self, index):
        if self.state != GameState.PLAYING: return False
        hand = self.player.get_hand()
        if index < hand.get_special_count():
            self.game.use_special_card(index)
            self.target_number = self.enemy.get_number()
            self.clear_selection()
            return True
        return False