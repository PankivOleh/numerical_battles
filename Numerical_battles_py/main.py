import pygame
import sys
from game_logic import GameLogic, GameState
from settings import *
from ui_elements import Button, Card, TextInput

pygame.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Numerical Battles")
        self.clock = pygame.time.Clock()
        self.running = True

        # Меню
        self.in_menu = True
        self.player_name = "Player"
        self.selected_difficulty = 1

        self.name_input = TextInput(WIDTH//2 - 150, 300, 300, 50)
        self.btn_diff_1 = Button(WIDTH//2 - 200, 420, 120, 50, "EASY")
        self.btn_diff_2 = Button(WIDTH//2 - 60, 420, 120, 50, "NORMAL")
        self.btn_diff_3 = Button(WIDTH//2 + 80, 420, 120, 50, "HARD")
        self.btn_diff_1.is_selected = True
        self.btn_start = Button(WIDTH//2 - 100, 550, 200, 60, "START GAME", color=SUCCESS_COLOR)

        self.logic = None

        self.numb_cards = []
        self.op_cards = []
        self.special_cards = []
        self.choice_cards = []

        # Кнопки
        btn_y = 360
        self.calculate_button = Button(WIDTH // 2 - 90, btn_y, 180, 50, "ОБЧИСЛИТИ")
        self.clear_button = Button(WIDTH // 2 - 240, btn_y, 130, 50, "Скинути")

        self.confirm_merge_btn = Button(RECT_SPECIAL.centerx - 80, 680, 160, 50, "ЗЛИТТЯ", color=SUCCESS_COLOR)
        self.skip_merge_btn = Button(RECT_SPECIAL.centerx - 80, 740, 160, 50, "ПРОПУСТИТИ", color=ERROR_COLOR)

        self.confirm_choice_btn = Button(WIDTH // 2 - 100, HEIGHT - 100, 200, 50, "ГОТОВО")

        self.message = ""
        self.message_color = TEXT_COLOR
        self.message_timer = 0

    def start_game(self):
        if self.name_input.text.strip():
            self.player_name = self.name_input.text.strip()
        self.logic = GameLogic(self.player_name, self.selected_difficulty)
        self.in_menu = False
        self.sync_cards_with_logic()

    def sync_cards_with_logic(self):
        """СТАБІЛЬНЕ ОНОВЛЕННЯ: Пріоритет на збереження позиції"""
        if not self.logic: return
        numb_data, op_data, special_data = self.logic.get_hand_data()

        def create_synced_list(old_ui_list, new_data_list, card_type, selected_indices):
            # Створюємо порожній список потрібного розміру
            new_ui_list = [None] * len(new_data_list)
            # Множина індексів старих карт, які ми вже використали
            used_old_indices = set()

            # --- ПРОХІД 1: СТАБІЛЬНІСТЬ ---
            # Спочатку шукаємо карти, які залишилися на тому ж індексі і мають те ж значення.
            # Це запобігає "стрибанню" однакових операторів.
            for i, val in enumerate(new_data_list):
                if i < len(old_ui_list):
                    old_card = old_ui_list[i]

                    # Порівняння значень
                    is_same = False
                    if isinstance(val, float) and isinstance(old_card.value, float):
                        is_same = abs(val - old_card.value) < 0.001
                    else:
                        is_same = (val == old_card.value)

                    if is_same:
                        # Це та сама карта! Залишаємо її.
                        old_card.index = i
                        old_card.update_text(val)  # Про всяк випадок оновлюємо текст
                        old_card.is_selected = (i in selected_indices)

                        new_ui_list[i] = old_card
                        used_old_indices.add(i)

            # --- ПРОХІД 2: ПОШУК ПЕРЕМІЩЕНИХ ---
            # Заповнюємо пробіли картами, які могли зсунутися (наприклад, після видалення сусідів)
            for i, val in enumerate(new_data_list):
                if new_ui_list[i] is None:
                    # Шукаємо підходящу карту серед невикористаних старих
                    found_match = None
                    found_old_index = -1

                    for old_i, old_card in enumerate(old_ui_list):
                        if old_i in used_old_indices: continue  # Ця вже зайнята

                        is_same = False
                        if isinstance(val, float) and isinstance(old_card.value, float):
                            is_same = abs(val - old_card.value) < 0.001
                        else:
                            is_same = (val == old_card.value)

                        if is_same:
                            found_match = old_card
                            found_old_index = old_i
                            break  # Беремо першу ліпшу

                    if found_match:
                        # Знайшли стару карту, яка зсунулася
                        found_match.index = i
                        found_match.is_selected = (i in selected_indices)
                        found_match.update_text(val)

                        new_ui_list[i] = found_match
                        used_old_indices.add(found_old_index)

            # --- ПРОХІД 3: СТВОРЕННЯ НОВИХ ---
            # Якщо досі є None, значить це абсолютно нові карти (наприклад, результат злиття)
            for i, val in enumerate(new_data_list):
                if new_ui_list[i] is None:
                    new_card = Card(WIDTH // 2, HEIGHT + 100, 80, 110, val, card_type, i)
                    new_card.is_selected = (i in selected_indices)
                    new_ui_list[i] = new_card

            return new_ui_list

        # Викликаємо оновлену функцію для всіх типів
        self.numb_cards = create_synced_list(
            self.numb_cards, numb_data, 'numb', self.logic.selected_indices['numb']
        )
        self.op_cards = create_synced_list(
            self.op_cards, op_data, 'op', self.logic.selected_indices['op']
        )
        self.special_cards = create_synced_list(
            self.special_cards, special_data, 'special', []
        )

        self.calculate_card_targets()

    def calculate_card_targets(self):
        """Розраховує цільові координати для анімації польоту карт"""
        card_w, card_h = 80, 110
        gap = 15

        # ВАЖЛИВО:
        # Карти можуть летіти в центр (у вираз) ТІЛЬКИ коли йде гра.
        # Якщо ми перейшли до злиття (MERGE_CHOICE) або вибираємо нові карти,
        # всі карти повинні повернутися в руку, навіть якщо вони технічно "selected".
        can_fly_to_center = (self.logic.state == GameState.PLAYING)

        # --- 1. ЧИСЛА (Zone: RECT_NUMB) ---
        count_numb = len(self.numb_cards)
        if count_numb > 0:
            # Базова ширина: ширина всіх карт + відступи
            total_w = count_numb * (card_w + gap) - gap

            # Налаштування розміщення
            base_y = RECT_NUMB.y + 50
            start_x = RECT_NUMB.centerx - (total_w // 2)
            step_x = card_w + gap

            # Логіка "віяла" (Overlap): якщо карти не влазять в ширину зони
            padding = 40
            max_w = RECT_NUMB.width - padding

            if total_w > max_w:
                # Перераховуємо крок, щоб втиснути всі карти
                # Формула: (доступна_ширина - одна_карта) / (кількість_проміжків)
                step_x = (max_w - card_w) / (count_numb - 1)
                start_x = RECT_NUMB.left + (padding // 2)

            # Призначаємо цілі
            for i, card in enumerate(self.numb_cards):
                # Якщо граємо і карта вибрана -> летить у центр
                if can_fly_to_center and card.is_selected:
                    self.set_expression_target(card)
                else:
                    # Інакше -> летить на своє місце в руці
                    target_x = start_x + i * step_x
                    card.target_pos = pygame.Vector2(target_x, base_y)

        # --- 2. ОПЕРАЦІЇ (Zone: RECT_OP) ---
        count_op = len(self.op_cards)
        if count_op > 0:
            total_w_op = count_op * (card_w + gap) - gap

            base_y_op = RECT_OP.y + 45
            start_x_op = RECT_OP.centerx - (total_w_op // 2)
            step_x_op = card_w + gap

            # Логіка "віяла" для операцій
            padding_op = 40
            max_w_op = RECT_OP.width - padding_op

            if total_w_op > max_w_op:
                step_x_op = (max_w_op - card_w) / (count_op - 1)
                start_x_op = RECT_OP.left + (padding_op // 2)

            for i, card in enumerate(self.op_cards):
                if can_fly_to_center and card.is_selected:
                    self.set_expression_target(card)
                else:
                    target_x = start_x_op + i * step_x_op
                    card.target_pos = pygame.Vector2(target_x, base_y_op)

        # --- 3. СПЕЦКАРТИ (Zone: RECT_SPECIAL) ---
        # Вони завжди стоять вертикально справа і ніколи не летять у вираз
        start_y_spec = RECT_SPECIAL.y + 50
        for i, card in enumerate(self.special_cards):
            target_x = RECT_SPECIAL.centerx - (card_w // 2)
            target_y = start_y_spec + i * (card_h + 10)
            card.target_pos = pygame.Vector2(target_x, target_y)

    def set_expression_target(self, card):
        selected_cards = []
        for type_, idx, _ in self.logic.selected_cards:
            if type_ == 'numb':
                # Знаходимо об'єкт карти, який відповідає цьому індексу
                found = next((c for c in self.numb_cards if c.index == idx), None)
                if found: selected_cards.append(found)
            elif type_ == 'op':
                found = next((c for c in self.op_cards if c.index == idx), None)
                if found: selected_cards.append(found)

        try: pos_index = selected_cards.index(card)
        except ValueError: pos_index = 0

        card_w = 80
        gap = 10
        total_w = len(selected_cards) * (card_w + gap) - gap
        start_x = WIDTH // 2 - (total_w // 2)

        target_x = start_x + pos_index * (card_w + gap)
        target_y = 230 # RECT_EXPRESSION center

        card.target_pos = pygame.Vector2(target_x, target_y)

    def update_choice_cards(self):
        if not self.logic: return
        self.choice_cards = []
        choices = self.logic.get_choice_data()
        card_w, card_h = 100, 140
        total_w = len(choices) * (card_w + 20)
        start_x = (WIDTH - total_w) // 2
        y_pos = HEIGHT // 2 - 50

        for i, (card_type, value) in enumerate(choices):
            x = start_x + i * (card_w + 20)
            card = Card(x, y_pos, card_w, card_h, value, card_type, i)
            if i in self.logic.selected_choice_indices:
                card.is_selected = True
            self.choice_cards.append(card)

    def draw_background_grid(self):
        self.screen.fill(BG_COLOR)
        grid_size = 50
        for x in range(0, WIDTH, grid_size):
            col = (35, 40, 50) if x % 200 != 0 else (45, 50, 60)
            pygame.draw.line(self.screen, col, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, grid_size):
            col = (35, 40, 50) if y % 200 != 0 else (45, 50, 60)
            pygame.draw.line(self.screen, col, (0, y), (WIDTH, y), 1)

    def draw_zones_and_counters(self):
        def draw_zone(rect, title, count, max_count):
            pygame.draw.rect(self.screen, ZONE_BG_COLOR, rect, border_radius=16)
            pygame.draw.rect(self.screen, ZONE_BORDER_COLOR, rect, 2, border_radius=16)

            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 30)
            pygame.draw.rect(self.screen, ZONE_HEADER_COLOR, header_rect, border_top_left_radius=14, border_top_right_radius=14)
            pygame.draw.line(self.screen, ZONE_BORDER_COLOR, (rect.x, rect.y+30), (rect.right, rect.y+30))

            title_surf = FONT_TINY().render(title, True, (170, 170, 190))
            self.screen.blit(title_surf, (rect.x + 15, rect.y + 8))

            cnt_color = SUCCESS_COLOR if count < max_count else ERROR_COLOR
            cnt_surf = FONT_SMALL().render(f"{count} / {max_count}", True, cnt_color)
            self.screen.blit(cnt_surf, (rect.right - 70, rect.y + 5))

        if self.logic:
            h = self.logic.player.get_hand()
            draw_zone(RECT_NUMB, "ЧИСЛА", h.get_numb_count(), 10)
            draw_zone(RECT_OP, "ОПЕРАЦІЇ", h.get_operator_count(), 6)
            draw_zone(RECT_SPECIAL, "СПЕЦІАЛЬНІ", h.get_special_count(), 5)

    def draw_target(self):
        if not self.logic: return
        target_panel = pygame.Rect(WIDTH//2 - 180, 20, 360, 90)
        shadow = target_panel.copy(); shadow.y += 5
        pygame.draw.rect(self.screen, (0,0,0,100), shadow, border_radius=25)
        pygame.draw.rect(self.screen, ZONE_BG_COLOR, target_panel, border_radius=25)
        pygame.draw.rect(self.screen, ACCENT_COLOR, target_panel, 2, border_radius=25)

        target_text = f"{self.logic.target_number:.3f}".rstrip('0').rstrip('.')

        lbl = FONT_TINY().render("ЦІЛЬОВЕ ЧИСЛО", True, (150, 150, 150))
        self.screen.blit(lbl, lbl.get_rect(center=(WIDTH//2, 45)))

        text_surf = FONT_LARGE().render(target_text, True, ACCENT_COLOR)
        self.screen.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, 80)))

    def draw_selected_expression(self):
        pass # Карти самі малюються в центрі

    def draw_info(self):
        if not self.logic: return
        info_x = 30
        info_y = 30
        panel = pygame.Rect(20, 20, 220, 110)
        pygame.draw.rect(self.screen, ZONE_BG_COLOR, panel, border_radius=15)
        pygame.draw.rect(self.screen, ZONE_BORDER_COLOR, panel, 2, border_radius=15)

        name_surf = FONT_MEDIUM().render(self.logic.player_name[:10], True, ACCENT_COLOR)
        self.screen.blit(name_surf, (35, 30))
        hp_surf = FONT_SMALL().render(f"HP: {self.logic.player.get_hp()}", True, SUCCESS_COLOR)
        self.screen.blit(hp_surf, (35, 70))
        lvl_surf = FONT_SMALL().render(f"LVL: {self.logic.level}", True, TEXT_COLOR)
        self.screen.blit(lvl_surf, (140, 70))

    def show_message(self, text, color=TEXT_COLOR, duration=120):
        self.message = text
        self.message_color = color
        self.message_timer = duration

    def draw_message(self):
        if self.message and self.message_timer > 0:
            text_surf = FONT_MEDIUM().render(self.message, True, self.message_color)
            bg_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT//2 - 20))
            bg_rect.inflate_ip(60, 30)
            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 230))
            self.screen.blit(s, bg_rect)
            pygame.draw.rect(self.screen, self.message_color, bg_rect, 2, border_radius=10)
            self.screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))
            self.message_timer -= 1

    # --- HANDLERS ---
    def handle_menu_event(self, event):
        self.name_input.handle_event(event)
        if self.btn_diff_1.handle_event(event):
            self.selected_difficulty = 1
            self.btn_diff_1.is_selected, self.btn_diff_2.is_selected, self.btn_diff_3.is_selected = True, False, False
        if self.btn_diff_2.handle_event(event):
            self.selected_difficulty = 2
            self.btn_diff_1.is_selected, self.btn_diff_2.is_selected, self.btn_diff_3.is_selected = False, True, False
        if self.btn_diff_3.handle_event(event):
            self.selected_difficulty = 3
            self.btn_diff_1.is_selected, self.btn_diff_2.is_selected, self.btn_diff_3.is_selected = False, False, True
        if self.btn_start.handle_event(event):
            self.start_game()

    def handle_playing_state(self, event):
        all_cards = self.numb_cards + self.op_cards

        # Обробка кліків по картах (вибір для виразу)
        for card in all_cards:
            if card.handle_event(event):
                self.logic.select_card(card.card_type, card.index)
                self.sync_cards_with_logic()  # Оновлюємо, щоб карта полетіла в центр

        # Спецкарти
        spec_used = False
        for card in self.special_cards:
            if card.handle_event(event):
                if self.logic.use_special_card(card.index):
                    self.show_message("Спец. ефект застосовано!", SUCCESS_COLOR)
                    self.sync_cards_with_logic()
                    spec_used = True
                    break
        if spec_used: return

        # Кнопка ОБЧИСЛИТИ
        if self.calculate_button.handle_event(event):
            success, msg = self.logic.calculate_result()

            # Спочатку показуємо повідомлення
            color = SUCCESS_COLOR if success else ERROR_COLOR
            self.show_message(msg, color)

            if success:
                # 1. Змінюємо стан на Злиття
                self.logic.start_merge_phase()

                # 2. Скидаємо виділення у всіх карт (щоб вони полетіли вниз)
                for c in self.numb_cards + self.op_cards:
                    c.is_selected = False
                    c.is_merge_selected = False

                # 3. Синхронізуємо (видаляємо старі, створюємо нові карти)
                # Оскільки стан вже MERGE, calculate_card_targets направить їх вниз
                self.sync_cards_with_logic()

            else:
                # Помилка: просто скидаємо вибір
                self.logic.clear_selection()
                self.sync_cards_with_logic()

        # Кнопка Скинути
        if self.clear_button.handle_event(event):
            self.logic.clear_selection()
            self.sync_cards_with_logic()

    def handle_merge_state(self, event):
        # Вибір карт для злиття
        for card in self.numb_cards + self.op_cards:
            if card.handle_event(event):
                card.is_merge_selected = not card.is_merge_selected

        # Підтвердження злиття
        if self.confirm_merge_btn.handle_event(event):
            sel_numb = [c.index for c in self.numb_cards if c.is_merge_selected]
            sel_op = [c.index for c in self.op_cards if c.is_merge_selected]

            if len(sel_numb) == 2 and len(sel_op) == 1:
                # Злиття
                success, msg = self.logic.merge_cards(sel_numb[0], sel_op[0], sel_numb[1])
                self.show_message(msg, SUCCESS_COLOR if success else ERROR_COLOR)

                if success:
                    self.sync_cards_with_logic()
                    self.update_choice_cards()
                    # Увага: перехід стану (self.logic.state) вже відбувся всередині logic.merge_cards()
                    # Тому тут ми просто оновлюємо UI
            else:
                self.show_message("Оберіть: [ЧИСЛО] [ОП] [ЧИСЛО]", ERROR_COLOR)

        # Пропуск злиття
        if self.skip_merge_btn.handle_event(event):
            self.logic.skip_merge()
            self.update_choice_cards()

    def handle_selection_state(self, event):
        for card in self.choice_cards:
            if card.handle_event(event):
                self.logic.select_new_card(card.index)
                self.update_choice_cards()

        if self.confirm_choice_btn.handle_event(event):
            if len(self.logic.selected_choice_indices) > 0:
                self.logic.confirm_card_selection()

                # Якщо ми повернулися в гру
                if self.logic.state == GameState.PLAYING:
                    # Створюємо нові карти (вони з'являться знизу по центру завдяки sync)
                    self.sync_cards_with_logic()

                elif self.logic.state == GameState.SPECIAL_SELECTION:
                    self.update_choice_cards()
            else:
                self.show_message("Оберіть хоча б одну карту!", ERROR_COLOR)


    # --- MAIN DRAW LOOPS ---
    def draw_menu(self):
        title = FONT_TITLE().render("NUMERICAL BATTLES", True, ACCENT_COLOR)
        self.screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))
        lbl_name = FONT_SMALL().render("Введіть ім'я:", True, TEXT_COLOR)
        self.screen.blit(lbl_name, (WIDTH//2 - 150, 275))
        self.name_input.draw(self.screen)
        lbl_diff = FONT_SMALL().render("Оберіть складність:", True, TEXT_COLOR)
        self.screen.blit(lbl_diff, (WIDTH//2 - 150, 395))
        self.btn_diff_1.draw(self.screen)
        self.btn_diff_2.draw(self.screen)
        self.btn_diff_3.draw(self.screen)
        self.btn_start.draw(self.screen)

    def draw_playing_state(self):
        # Physics update
        for c in self.numb_cards + self.op_cards + self.special_cards:
            c.update()

        self.draw_target()
        self.draw_info()
        self.draw_zones_and_counters()

        # СОРТУВАННЯ: Спочатку неактивні, потім вибрані, потім НАВЕДЕНІ (щоб були зверху)
        cards_to_draw = self.numb_cards + self.op_cards + self.special_cards
        cards_to_draw.sort(key=lambda c: (c.is_selected, c.is_hovered))

        for c in cards_to_draw: c.draw(self.screen)

        self.calculate_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.draw_message()

    def draw_merge_state(self):
        for c in self.numb_cards + self.op_cards + self.special_cards:
            c.update()

        self.draw_target()
        self.draw_info()  # Додамо інфо, щоб не зникало
        self.draw_zones_and_counters()

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Трохи прозоріше
        self.screen.blit(overlay, (0, 0))

        hint = FONT_SMALL().render("Виберіть 2 числа та 1 операцію для створення нового числа", True, TEXT_COLOR)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 240)))

        # Малюємо карти
        for c in self.numb_cards + self.op_cards:
            c.draw(self.screen)

        self.confirm_merge_btn.draw(self.screen)
        self.skip_merge_btn.draw(self.screen)
        self.draw_message()


    def draw_selection_state(self):
        for c in self.numb_cards + self.op_cards:
            c.update()

        self.draw_zones_and_counters()
        for c in self.numb_cards + self.op_cards:
            c.draw(self.screen)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        txt = "Оберіть нові карти" if self.logic.state == GameState.CARD_SELECTION else "Оберіть спеціальну карту"
        title = FONT_LARGE().render(txt, True, ACCENT_COLOR)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 100)))

        for card in self.choice_cards:
            card.draw(self.screen)

        self.confirm_choice_btn.draw(self.screen)
        self.draw_message()

    def draw_game_over(self):
        self.screen.fill((40, 0, 0))
        title = FONT_LARGE().render("ГРА ЗАКІНЧЕНА", True, ERROR_COLOR)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    def draw_victory(self):
        self.screen.fill((0, 40, 0))
        title = FONT_LARGE().render("ПЕРЕМОГА!", True, SUCCESS_COLOR)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.in_menu: self.handle_menu_event(event)
                elif self.logic.state == GameState.PLAYING: self.handle_playing_state(event)
                elif self.logic.state == GameState.MERGE_CHOICE: self.handle_merge_state(event)
                elif self.logic.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]: self.handle_selection_state(event)

            self.draw_background_grid()

            if self.in_menu:
                self.draw_menu()
            elif self.logic.state == GameState.PLAYING:
                self.draw_playing_state()
            elif self.logic.state == GameState.MERGE_CHOICE:
                self.draw_merge_state()
            elif self.logic.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]:
                self.draw_selection_state()
            elif self.logic.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.logic.state == GameState.VICTORY:
                self.draw_victory()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()