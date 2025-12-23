import pygame
import sys
import os
import ctypes
from game_logic import GameLogic, GameState
from settings import *
from ui_elements import Button, Card, TextInput

os.environ['SDL_VIDEO_CENTERED'] = '1'
# Ініціалізація pygame
pygame.init()


class Game:
    def __init__(self):
        # Застосовуємо налаштування відео (з settings.py)
        self.apply_video_settings()

        # Стан меню
        self.in_menu = True
        self.settings_menu_active = False

        self.player_name = "Player"
        self.selected_difficulty = 1
        # --- НОВІ ЗМІННІ ДЛЯ РЕЖИМІВ ---
        self.game_mode = "PvE"  # Варіанти: "PvE", "PvP", "EvE"
        self.current_turn = 1  # 1 або 2

        # Таймер для штучного інтелекту (щоб він не ходив миттєво)
        self.ai_timer = 0
        self.ai_delay = 60  # 60 кадрів = 1 секунда затримки

        # Логіка для двох гравців
        self.logic_p1 = None
        self.logic_p2 = None

        self.merge_selection_queue = []

        # --- ЗМІННІ ДЛЯ АНІМАЦІЇ ЛІЧИЛЬНИКА ---
        self.is_animating_calculation = False
        self.anim_start_time = 0
        self.anim_duration = 1500  # Тривалість анімації в мс (1.5 сек)
        self.anim_current_value = 0.0
        self.anim_target_value = 0.0
        self.anim_start_value = 0.0
        self.clock = pygame.time.Clock()
        self.running = True

        self.game_mode = "PvE"  # Або "PvP", "EvE"
        self.logic_p1 = None
        self.logic_p2 = None
        self.current_turn = 1  # 1 або 2

        self.ai_delay_timer = 0
        self.ai_phase = 0



        # Ініціалізація UI елементів
        self.reinit_ui()

        # Логіка гри
        self.logic = None

        # Списки карт (UI об'єкти)
        self.numb_cards = []
        self.op_cards = []
        self.special_cards = []

        # Карти для вибору (Draft)
        self.choice_cards = []

        # Черга для збереження порядку злиття
        self.merge_selection_queue = []

        self.message = ""
        self.message_color = TEXT_COLOR
        self.message_timer = 0

    def apply_video_settings(self):
        """Застосовує налаштування екрану. Виправляє зсув вікна."""
        # 1. Повністю вбиваємо старе вікно, щоб OS забула його координати
        pygame.display.quit()
        pygame.display.init()

        # 2. Центруємо майбутнє вікно (важливо для віконного режиму)
        os.environ['SDL_VIDEO_CENTERED'] = '1'

        # Беремо бажані розміри з налаштувань
        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]

        if CONFIG["FULLSCREEN"]:
            # ВАЖЛИВО: Ми створюємо екран саме розміру w/h (наприклад 1280x720),
            # але додаємо прапорець SCALED. Pygame сам розтягне ці 1280 пікселів
            # на весь ваш монітор (1920x1080), зберігаючи пропорції та чіткість UI.
            try:
                self.screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.SCALED)
            except pygame.error:
                # Якщо SCALED не працює (старе залізо), робимо звичайний фулскрін
                self.screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
        else:
            # Віконний режим - просто вікно заданого розміру по центру
            self.screen = pygame.display.set_mode((w, h))

        pygame.display.set_caption("Numerical Battles")

        # 3. Перераховуємо координати кнопок під нові w/h
        if hasattr(self, 'btn_start'):
            self.reinit_ui()

    def update_calculation_animation(self):
        if not self.is_animating_calculation: return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.anim_start_time

        if elapsed < self.anim_duration:
            t = elapsed / self.anim_duration
            t = 1 - pow(1 - t, 3)
            self.anim_current_value = self.anim_start_value + (self.anim_target_value - self.anim_start_value) * t
        else:
            # === АНІМАЦІЯ ЗАВЕРШЕНА ===
            self.is_animating_calculation = False
            self.anim_current_value = self.anim_target_value

            # 1. Застосовуємо результат (тут може знятися HP)
            success, msg = self.logic.apply_turn_result(self.anim_target_value)

            # === КРИТИЧНА ПЕРЕВІРКА: ЧИ МИ ЖИВІ? ===
            if self.logic.player.get_hp() <= 0:
                self.logic.state = GameState.GAME_OVER
                self.show_message("ГРА ЗАКІНЧЕНА", ERROR_COLOR, duration=200)
                return  # <--- ВАЖЛИВО: Миттєвий вихід, ніяких switch_turn!
            # ========================================

            color = ERROR_COLOR
            if success: color = SUCCESS_COLOR
            if self.logic.round_won: color = SUCCESS_COLOR

            self.show_message(msg, color, duration=120)

            is_bot_turn = (self.game_mode == "EvE") or (self.game_mode == "PvE" and self.current_turn == 2)

            if success:
                # Хід успішний
                if self.logic.round_won:
                    # ПЕРЕМОГА -> Вибір нагороди
                    self.logic.start_special_selection()
                else:
                    # ПРОМІЖНИЙ ХІД
                    if is_bot_turn:
                        self.logic.start_card_selection()
                    else:
                        self.logic.start_merge_phase()

                self.merge_selection_queue.clear()
                self.logic.clear_selection()
                self.choice_cards.clear()
            else:
                # ПОМИЛКА -> Перехід ходу (Тільки якщо ми ще живі, перевірка вище це гарантує)
                self.switch_turn()

            self.sync_cards_with_logic()

    def apply_video_settings(self):
        """Створює вікно згідно з CONFIG"""
        flags = pygame.FULLSCREEN if CONFIG["FULLSCREEN"] else 0
        self.screen = pygame.display.set_mode((CONFIG["WIDTH"], CONFIG["HEIGHT"]), flags)
        pygame.display.set_caption("Numerical Battles")

    def reinit_ui(self):
        """Створює або оновлює всі кнопки під поточний розмір екрану"""
        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        center_x = w // 2

        # --- ГОЛОВНЕ МЕНЮ ---
        self.name_input = TextInput(center_x - 150, 300, 300, 50)
        self.btn_diff_1 = Button(center_x - 200, 420, 120, 50, "EASY")
        self.btn_diff_2 = Button(center_x - 60, 420, 120, 50, "NORMAL")
        self.btn_diff_3 = Button(center_x + 80, 420, 120, 50, "HARD")

        self.btn_mode_pve = Button(center_x - 220, 480, 140, 40, "Людина vs PC")
        self.btn_mode_pvp = Button(center_x - 60, 480, 140, 40, "PvP (Local)")
        self.btn_mode_eve = Button(center_x + 100, 480, 140, 40, "PC vs PC")

        # Виділяємо дефолтний режим
        self.btn_mode_pve.is_selected = True
        # --------------------------------------------------

        # Зсуваємо кнопку START трохи нижче
        self.btn_start = Button(center_x - 100, 580, 200, 60, "START GAME", color=SUCCESS_COLOR)

        # Відновлення стану кнопок
        if self.selected_difficulty == 1:
            self.btn_diff_1.is_selected = True
        elif self.selected_difficulty == 2:
            self.btn_diff_2.is_selected = True
        elif self.selected_difficulty == 3:
            self.btn_diff_3.is_selected = True

        self.btn_start = Button(center_x - 100, 550, 200, 60, "START GAME", color=SUCCESS_COLOR)
        self.btn_settings = Button(w - 140, 20, 120, 40, "Налаштування")
        self.btn_exit_menu = Button(w - 140, 70, 120, 40, "Вихід", color=ERROR_COLOR)

        # --- МЕНЮ НАЛАШТУВАНЬ ---
        self.btn_res_toggle = Button(center_x - 150, 300, 300, 50, f"Resolution: {w}x{h}")
        self.btn_fs_toggle = Button(center_x - 150, 370, 300, 50,
                                    f"Fullscreen: {'ON' if CONFIG['FULLSCREEN'] else 'OFF'}")
        self.btn_settings_back = Button(center_x - 100, 500, 200, 50, "Назад")

        # --- ІГРОВИЙ ПРОЦЕС (PLAYING) ---
        btn_y = h / 2 - 40
        self.calculate_button = Button(center_x - 90, btn_y, 180, 50, "ОБЧИСЛИТИ")
        self.clear_button = Button(center_x - 240, btn_y, 130, 50, "Скинути")
        self.btn_back_to_menu_game = Button(20, 150, 150, 40, "В МЕНЮ", color=(255, 100, 0))

        # --- КНОПКИ ЗЛИТТЯ (MERGE) ---
        r_spec = GET_RECT_SPECIAL()  # Отримуємо актуальну зону спецкарт
        self.confirm_merge_btn = Button(r_spec.centerx - 80, h - 120, 160, 50, "ЗЛИТТЯ", color=SUCCESS_COLOR)
        self.skip_merge_btn = Button(r_spec.centerx - 80, h - 60, 160, 50, "ПРОПУСТИТИ", color=ERROR_COLOR)

        # --- ВИБІР КАРТ (DRAFT) ---
        self.confirm_choice_btn = Button(center_x - 100, h - 100, 200, 50, "ГОТОВО")
        self.btn_clear_choices = Button(center_x + 120, h - 100, 150, 50, "Відмінити", color=ERROR_COLOR)

    def start_game(self):
        p1_name = self.name_input.text.strip() or "Player 1"

        # 1. Створюємо гравців
        if self.game_mode == "PvE":
            self.logic_p1 = GameLogic(p1_name, self.selected_difficulty)
            self.logic_p2 = GameLogic("Robot 🤖", self.selected_difficulty)

        elif self.game_mode == "PvP":
            self.logic_p1 = GameLogic(p1_name, self.selected_difficulty)
            self.logic_p2 = GameLogic("Player 2", self.selected_difficulty)

        elif self.game_mode == "EvE":
            self.logic_p1 = GameLogic("Bot Alpha", self.selected_difficulty)
            self.logic_p2 = GameLogic("Bot Omega", self.selected_difficulty)

        # 2. Налаштовуємо старт
        self.current_turn = 1
        self.logic = self.logic_p1  # Починає перший
        self.in_menu = False

        self.sync_cards_with_logic()

    # ==========================================
    # ЛОГІКА СИНХРОНІЗАЦІЇ UI ТА C++
    # ==========================================
    def sync_cards_with_logic(self):
        if not self.logic: return
        numb_data, op_data, special_data = self.logic.get_hand_data()

        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]

        def create_synced_list(old_ui_list, new_data_list, card_type, selected_indices):
            new_ui_list = []

            for i, val in enumerate(new_data_list):
                # 1. ТОЧКА ПОЯВИ
                if card_type == 'special':
                    # З'являються справа, на фіксованій висоті
                    start_x = w - 100
                    start_y = 150 + (i * 50)  # Каскадом вниз
                else:
                    # Числа/Оп з'являються знизу
                    start_x = w // 2
                    start_y = h + 100

                new_card = Card(start_x, start_y, 80, 110, val, card_type, i)

                # 2. ЗБЕРІГАЄМО ПОЗИЦІЮ, ЯКЩО КАРТА ВЖЕ БУЛА
                if i < len(old_ui_list):
                    prev_card = old_ui_list[i]
                    # Копіюємо позицію
                    new_card.current_pos = pygame.Vector2(prev_card.current_pos)
                    new_card.rect.topleft = prev_card.rect.topleft

                new_card.is_selected = (i in selected_indices)
                new_ui_list.append(new_card)

            return new_ui_list

        # ... (виклик функції для трьох типів без змін) ...
        self.numb_cards = create_synced_list(self.numb_cards, numb_data, 'numb', self.logic.selected_indices['numb'])
        self.op_cards = create_synced_list(self.op_cards, op_data, 'op', self.logic.selected_indices['op'])
        self.special_cards = create_synced_list(self.special_cards, special_data, 'special',
                                                [])  # Тут пустий список індексів

        self.calculate_card_targets()

    def calculate_card_targets(self):
        """Розрахунок позицій з гарантією, що карти не вилетять за екран"""
        card_w, card_h = 80, 110
        gap = 15

        can_fly_to_center = (self.logic.state == GameState.PLAYING)

        r_numb = GET_RECT_NUMB()
        r_op = GET_RECT_OP()
        r_spec = GET_RECT_SPECIAL()
        r_expr = GET_RECT_EXPRESSION()

        # --- 1. ЧИСЛА ---
        count_numb = len(self.numb_cards)
        if count_numb > 0:
            total_w = count_numb * (card_w + gap) - gap
            base_y = r_numb.y + 50
            start_x = r_numb.centerx - (total_w // 2)
            step_x = card_w + gap

            # Стиснення по ширині
            padding = 40
            max_w = r_numb.width - padding
            if count_numb > 1 and total_w > max_w:
                step_x = (max_w - card_w) / (count_numb - 1)
                start_x = r_numb.left + (padding // 2)

            for i, card in enumerate(self.numb_cards):
                if can_fly_to_center and card.is_selected:
                    self.set_expression_target(card, r_expr)
                else:
                    target_x = start_x + i * step_x
                    card.target_pos = pygame.Vector2(target_x, base_y)

        # --- 2. ОПЕРАЦІЇ ---
        count_op = len(self.op_cards)
        if count_op > 0:
            total_w_op = count_op * (card_w + gap) - gap
            base_y_op = r_op.y + 45
            start_x_op = r_op.centerx - (total_w_op // 2)
            step_x_op = card_w + gap

            padding_op = 40
            max_w_op = r_op.width - padding_op
            if count_op > 1 and total_w_op > max_w_op:
                step_x_op = (max_w_op - card_w) / (count_op - 1)
                start_x_op = r_op.left + (padding_op // 2)

            for i, card in enumerate(self.op_cards):
                if can_fly_to_center and card.is_selected:
                    self.set_expression_target(card, r_expr)
                else:
                    target_x = start_x_op + i * step_x_op
                    card.target_pos = pygame.Vector2(target_x, base_y_op)

        # --- 3. СПЕЦКАРТИ (Повністю нова логіка) ---
        count_spec = len(self.special_cards)
        if count_spec > 0:
            # 1. Визначаємо верхню і нижню межі
            start_y = r_spec.y + 40
            # Нижня межа: висота екрану мінус висота карти мінус відступ
            max_y_pos = CONFIG["HEIGHT"] - card_h - 20

            # Доступна висота для розподілу ВЕРХНІХ країв карт
            available_span = max_y_pos - start_y

            # Дефолтний крок
            step_y = card_h + 10

            # Скільки місця треба, якщо не стискати?
            needed_span = (count_spec - 1) * step_y

            # Якщо треба більше місця, ніж є -> зменшуємо крок (Overlap)
            if count_spec > 1 and needed_span > available_span:
                step_y = available_span / (count_spec - 1)

            # Центруємо по горизонталі в зоні
            center_x = r_spec.centerx - (card_w // 2)

            for i, card in enumerate(self.special_cards):
                target_x = center_x
                # Формула гарантує, що остання карта (i = count-1)
                # буде рівно на позиції max_y_pos
                target_y = start_y + (i * step_y)

                card.target_pos = pygame.Vector2(target_x, target_y)

    def set_expression_target(self, card, r_expr):
        """Центрування карт виразу"""
        selected_cards = []

        # Збираємо всі вибрані карти в список у правильному порядку (як в логіці)
        for type_, idx, _ in self.logic.selected_cards:
            if type_ == 'numb':
                # Шукаємо карту за індексом
                found = next((c for c in self.numb_cards if c.index == idx), None)
                if found: selected_cards.append(found)
            elif type_ == 'op':
                found = next((c for c in self.op_cards if c.index == idx), None)
                if found: selected_cards.append(found)

        # Якщо цієї карти немає в списку вибраних (баг розсинхрону), ігноруємо
        if card not in selected_cards:
            return

        pos_index = selected_cards.index(card)

        card_w = 80
        gap = 10
        # Загальна ширина ВСЬОГО виразу
        total_w = len(selected_cards) * (card_w + gap) - gap

        # Початкова точка Х, щоб весь вираз був по центру екрану
        start_x = CONFIG["WIDTH"] // 2 - (total_w // 2)

        target_x = start_x + pos_index * (card_w + gap)
        target_y = r_expr.centery - (card.height // 2)

        card.target_pos = pygame.Vector2(target_x, target_y)

    def update_choice_cards(self):
        """Оновлення карток для драфту (СІТКА 2x5)"""
        if not self.logic: return

        self.choice_cards = []
        choices = self.logic.get_choice_data()  # Тут має бути 10 елементів

        # Налаштування розмірів
        card_w, card_h = 100, 140
        gap_x = 25
        gap_y = 30

        # Скільки карт в одному ряду
        cards_per_row = 5

        # Розрахунок ширини блоку (щоб центрувати)
        # Ширина 5 карт + 4 проміжки
        total_row_w = (cards_per_row * card_w) + ((cards_per_row - 1) * gap_x)

        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]

        # Початкова точка X (центр екрану мінус половина ширини блоку)
        start_x = (w - total_row_w) // 2

        # Початкова точка Y (трохи вище центру, бо у нас 2 ряди)
        start_y = (h // 2) - card_h - (gap_y // 2)

        for i, (card_type, value) in enumerate(choices):
            # Математика сітки:
            row = i // cards_per_row  # 0 для перших 5, 1 для наступних
            col = i % cards_per_row  # 0, 1, 2, 3, 4

            # Координати карти
            x = start_x + (col * (card_w + gap_x))
            y = start_y + (row * (card_h + gap_y))

            # Створення карти
            # Передаємо index=i, щоб логіка знала, яку саме карту ми вибрали
            card = Card(x, y, card_w, card_h, value, card_type, i)

            # Відновлюємо стан вибору (зелена рамка)
            if i in self.logic.selected_choice_indices:
                card.is_selected = True

            self.choice_cards.append(card)

    # ==========================================
    # ВІДОБРАЖЕННЯ (DRAWING)
    # ==========================================\

    def draw_background_grid(self):
        self.screen.fill(BG_COLOR)
        grid_size = 50
        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        for x in range(0, w, grid_size):
            col = (35, 40, 50) if x % 200 != 0 else (45, 50, 60)
            pygame.draw.line(self.screen, col, (x, 0), (x, h), 1)
        for y in range(0, h, grid_size):
            col = (35, 40, 50) if y % 200 != 0 else (45, 50, 60)
            pygame.draw.line(self.screen, col, (0, y), (w, y), 1)

    def draw_zones_and_counters(self):
        def draw_zone(rect, title, count, max_count):
            pygame.draw.rect(self.screen, ZONE_BG_COLOR, rect, border_radius=16)
            pygame.draw.rect(self.screen, ZONE_BORDER_COLOR, rect, 2, border_radius=16)

            header_rect = pygame.Rect(rect.x, rect.y, rect.width, 30)
            pygame.draw.rect(self.screen, ZONE_HEADER_COLOR, header_rect, border_top_left_radius=14,
                             border_top_right_radius=14)
            pygame.draw.line(self.screen, ZONE_BORDER_COLOR, (rect.x, rect.y + 30), (rect.right, rect.y + 30))

            title_surf = FONT_TINY().render(title, True, (170, 170, 190))
            self.screen.blit(title_surf, (rect.x + 15, rect.y + 8))

            cnt_color = SUCCESS_COLOR if count < max_count else ERROR_COLOR
            cnt_surf = FONT_SMALL().render(f"{count} / {max_count}", True, cnt_color)
            self.screen.blit(cnt_surf, (rect.right - 70, rect.y + 5))

        if self.logic:
            h = self.logic.player.get_hand()
            draw_zone(GET_RECT_NUMB(), "ЧИСЛА", h.get_numb_count(), 10)
            draw_zone(GET_RECT_OP(), "ОПЕРАЦІЇ", h.get_operator_count(), 6)
            draw_zone(GET_RECT_SPECIAL(), "СПЕЦІАЛЬНІ", h.get_special_count(), 4)

    def draw_target(self):
        if not self.logic: return
        w = CONFIG["WIDTH"]
        target_panel = pygame.Rect(w // 2 - 180, 20, 360, 90)

        shadow = target_panel.copy();
        shadow.y += 5
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow, border_radius=25)
        pygame.draw.rect(self.screen, ZONE_BG_COLOR, target_panel, border_radius=25)
        pygame.draw.rect(self.screen, ACCENT_COLOR, target_panel, 2, border_radius=25)

        target_text = f"{self.logic.target_number:.3f}".rstrip('0').rstrip('.')
        lbl = FONT_TINY().render("ЦІЛЬОВЕ ЧИСЛО", True, (150, 150, 150))
        self.screen.blit(lbl, lbl.get_rect(center=(w // 2, 45)))
        text_surf = FONT_LARGE().render(target_text, True, ACCENT_COLOR)
        self.screen.blit(text_surf, text_surf.get_rect(center=(w // 2, 80)))

    def draw_info(self):
        if not self.logic: return
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
            w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
            bg_rect = text_surf.get_rect(center=(w // 2, h // 2 - 20))
            bg_rect.inflate_ip(60, 30)

            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 230))
            self.screen.blit(s, bg_rect)
            pygame.draw.rect(self.screen, self.message_color, bg_rect, 2, border_radius=10)
            self.screen.blit(text_surf, text_surf.get_rect(center=bg_rect.center))
            self.message_timer -= 1

    # ==========================================
    # ОБРОБНИКИ ПОДІЙ (HANDLERS)
    # ==========================================
    def handle_menu_event(self, event):
        # Налаштування
        if self.btn_settings.handle_event(event):
            self.settings_menu_active = True
            self.in_menu = False
            return

        if self.btn_exit_menu.handle_event(event):
            self.running = False
            return

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
            # --- ОБРОБКА ВИБОРУ РЕЖИМУ ---
        if self.btn_mode_pve.handle_event(event):
            self.game_mode = "PvE"
            self.btn_mode_pve.is_selected = True
            self.btn_mode_pvp.is_selected = False
            self.btn_mode_eve.is_selected = False

        if self.btn_mode_pvp.handle_event(event):
            self.game_mode = "PvP"
            self.btn_mode_pve.is_selected = False
            self.btn_mode_pvp.is_selected = True
            self.btn_mode_eve.is_selected = False

        if self.btn_mode_eve.handle_event(event):
            self.game_mode = "EvE"
            self.btn_mode_pve.is_selected = False
            self.btn_mode_pvp.is_selected = False
            self.btn_mode_eve.is_selected = True
            # ------------------------------

            if self.btn_start.handle_event(event):
                self.start_game()


        if self.btn_start.handle_event(event):
            self.start_game()

    def handle_settings_event(self, event):
        if self.btn_settings_back.handle_event(event):
            self.settings_menu_active = False
            self.in_menu = True
            return

        if self.btn_res_toggle.handle_event(event):
            current_res = (CONFIG["WIDTH"], CONFIG["HEIGHT"])
            try:
                idx = RESOLUTIONS.index(current_res)
            except ValueError:
                idx = 0

            next_idx = (idx + 1) % len(RESOLUTIONS)
            new_w, new_h = RESOLUTIONS[next_idx]

            CONFIG["WIDTH"], CONFIG["HEIGHT"] = new_w, new_h
            self.apply_video_settings()
            self.reinit_ui()

        if self.btn_fs_toggle.handle_event(event):
            CONFIG["FULLSCREEN"] = not CONFIG["FULLSCREEN"]
            self.apply_video_settings()
            self.reinit_ui()

    def handle_playing_state(self, event):

        if self.logic.state != GameState.PLAYING:
            return

        if not self.is_animating_calculation:
            is_deadlock, msg = self.logic.check_deadlock()
            if is_deadlock:
                # Якщо глухий кут виявлено:
                color = ERROR_COLOR
                if self.logic.state == GameState.GAME_OVER:
                    # Якщо вмерли від штрафу
                    pass
                else:
                    # Якщо просто перейшли до вибору карт
                    self.update_choice_cards()  # Оновити UI вибору

                self.show_message(msg, color, duration=180)
                return  # Виходимо, бо стан змінився

        # 1. БЛОКУВАННЯ ВВОДУ
        # Якщо йде анімація підрахунку (лічильник біжить), ігноруємо всі кліки
        if self.is_animating_calculation:
            return

        # 2. КНОПКА ВИХОДУ В МЕНЮ
        if self.btn_back_to_menu_game.handle_event(event):
            self.in_menu = True
            self.logic = None  # Скидаємо поточну сесію гри
            return

        # 3. ВИБІР КАРТ (Числа та Операції)
        all_cards = self.numb_cards + self.op_cards
        for card in all_cards:
            if card.handle_event(event):
                # select_card тепер повертає True/False (чи пройшла валідація порядку)
                if self.logic.select_card(card.card_type, card.index):
                    self.sync_cards_with_logic()  # Оновлюємо UI (карта летить в центр)

        # 4. ВИКОРИСТАННЯ СПЕЦКАРТ
        spec_used = False
        for card in self.special_cards:
            if card.handle_event(event):
                if self.logic.use_special_card(card.index):
                    self.show_message("Спец. ефект застосовано!", SUCCESS_COLOR)
                    self.sync_cards_with_logic()
                    spec_used = True
                    break
        if spec_used: return

        # 5. КНОПКА "ОБЧИСЛИТИ"
        if self.calculate_button.handle_event(event):
            # ЕТАП А: Прев'ю (Валідація та отримання числа без наслідків)
            is_valid, data = self.logic.preview_calculation()

            if is_valid:
                # ЕТАП Б: Запуск анімації
                # Ми ще НЕ видаляємо карти і НЕ знімаємо HP. Це зробить update_calculation_animation.
                self.is_animating_calculation = True
                self.anim_start_time = pygame.time.get_ticks()

                self.anim_target_value = data  # 'data' тут - це float (результат виразу)
                self.anim_start_value = 0.0  # Можна починати з 0 або з попереднього числа
                self.anim_current_value = 0.0

            else:
                # ЕТАП В: Помилка валідації (наприклад, "Ділення на нуль")
                # 'data' тут - це текст помилки
                self.show_message(data, ERROR_COLOR)
                self.logic.clear_selection()
                self.sync_cards_with_logic()  # Повертаємо карти в руку

        # 6. КНОПКА "СКИНУТИ"
        if self.clear_button.handle_event(event):
            self.logic.clear_selection()
            self.sync_cards_with_logic()

    def handle_merge_state(self, event):
        if self.btn_back_to_menu_game.handle_event(event):
            self.in_menu = True
            self.logic = None
            return

        for card in self.numb_cards + self.op_cards:
            if card.handle_event(event):
                if card.is_merge_selected:
                    card.is_merge_selected = False
                    if card in self.merge_selection_queue:
                        self.merge_selection_queue.remove(card)
                else:
                    if len(self.merge_selection_queue) < 3:
                        card.is_merge_selected = True
                        self.merge_selection_queue.append(card)

        if self.confirm_merge_btn.handle_event(event):
            sel_numb = [c for c in self.merge_selection_queue if c.card_type == 'numb']
            sel_op = [c for c in self.merge_selection_queue if c.card_type == 'op']

            if len(sel_numb) == 2 and len(sel_op) == 1:
                success, msg = self.logic.merge_cards(sel_numb[0].index, sel_op[0].index, sel_numb[1].index)
                self.show_message(msg, SUCCESS_COLOR if success else ERROR_COLOR)
                if success:
                    self.merge_selection_queue.clear()
                    self.sync_cards_with_logic()
                    self.update_choice_cards()
            else:
                self.show_message("Оберіть: [ЧИСЛО] [ОП] [ЧИСЛО]", ERROR_COLOR)

        if self.skip_merge_btn.handle_event(event):
            self.merge_selection_queue.clear()
            self.logic.skip_merge()
            self.update_choice_cards()

    def handle_selection_state(self, event):
        # 1. Визначаємо, чий зараз хід
        is_bot_turn = (self.game_mode == "EvE") or (self.game_mode == "PvE" and self.current_turn == 2)

        # 2. Якщо хід БОТА — блокуємо всі натискання людини (окрім виходу)
        if is_bot_turn:
            if self.btn_back_to_menu_game.handle_event(event):
                self.in_menu = True
                self.logic = None
            return  # <--- Виходимо, щоб людина нічого не зламала

        # 3. Далі йде логіка ТІЛЬКИ для людини
        if self.btn_back_to_menu_game.handle_event(event):
            self.in_menu = True;
            self.logic = None;
            return

        # Кліки по картах
        for card in self.choice_cards:
            if card.handle_event(event):
                if card.is_selected:
                    self.logic.deselect_new_card(card.index)
                    card.is_selected = False
                else:
                    if self.logic.select_new_card(card.index):
                        card.is_selected = True

        if self.btn_clear_choices.handle_event(event):
            self.logic.clear_new_selection()
            for c in self.choice_cards: c.is_selected = False

        # --- КНОПКА "ГОТОВО" ---
        if self.confirm_choice_btn.handle_event(event):
            if len(self.logic.selected_choice_indices) > 0:

                was_special_phase = (self.logic.state == GameState.SPECIAL_SELECTION)

                self.choice_cards.clear()  # Очищення UI
                self.logic.confirm_card_selection()

                if was_special_phase:
                    # Ми щойно обрали спецкарту -> Новий рівень
                    self.sync_cards_with_logic()
                    self.update_choice_cards()

                elif self.logic.state == GameState.PLAYING:
                    # Ми завершили звичайний добір карт -> Перевірка на перемогу в раунді
                    if self.logic.round_won:
                        self.logic.start_special_selection()
                        self.update_choice_cards()
                    else:
                        self.sync_cards_with_logic()
                        self.switch_turn()
            else:
                self.show_message("Оберіть хоча б одну!", ERROR_COLOR)
    # РИСУВАННЯ (DRAW LOOPS)
    # ==========================================
    def draw_menu(self):
        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        title = FONT_TITLE().render("NUMERICAL BATTLES", True, ACCENT_COLOR)
        self.screen.blit(title, title.get_rect(center=(w // 2, 150)))

        lbl_name = FONT_SMALL().render("Введіть ім'я:", True, TEXT_COLOR)
        self.screen.blit(lbl_name, (w // 2 - 150, 275))
        self.name_input.draw(self.screen)

        lbl_diff = FONT_SMALL().render("Оберіть складність:", True, TEXT_COLOR)
        self.screen.blit(lbl_diff, (w // 2 - 150, 395))

        self.btn_diff_1.draw(self.screen)
        self.btn_diff_2.draw(self.screen)
        self.btn_diff_3.draw(self.screen)
        self.btn_mode_pve.draw(self.screen)
        self.btn_mode_pvp.draw(self.screen)
        self.btn_mode_eve.draw(self.screen)
        self.btn_start.draw(self.screen)
        self.btn_settings.draw(self.screen)
        self.btn_exit_menu.draw(self.screen)

    def draw_settings_menu(self):
        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        title = FONT_LARGE().render("НАЛАШТУВАННЯ", True, ACCENT_COLOR)
        self.screen.blit(title, title.get_rect(center=(w // 2, 100)))

        self.btn_res_toggle.draw(self.screen)
        self.btn_fs_toggle.draw(self.screen)
        self.btn_settings_back.draw(self.screen)

    def draw_playing_state(self):
        # 1. Оновлення анімації лічильника (вона має бути тут!)
        self.update_calculation_animation()

        # 2. Фізика і малювання столу
        for c in self.numb_cards + self.op_cards + self.special_cards:
            c.update()

        self.draw_target()
        self.draw_info()
        self.draw_zones_and_counters()

        # Малюємо карти
        cards_to_draw = self.numb_cards + self.op_cards + self.special_cards
        cards_to_draw.sort(key=lambda c: (c.is_selected, c.is_hovered))
        for c in cards_to_draw: c.draw(self.screen)

        # 3. Лічильник під час анімації
        if self.is_animating_calculation:
            overlay = pygame.Surface((CONFIG["WIDTH"], CONFIG["HEIGHT"]), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            val_text = f"{self.anim_current_value:.3f}".rstrip('0').rstrip('.')
            font_big = get_font(140)
            text_surf = font_big.render(val_text, True, ACCENT_COLOR)

            cx, cy = CONFIG["WIDTH"] // 2, CONFIG["HEIGHT"] // 2
            self.screen.blit(text_surf, text_surf.get_rect(center=(cx, cy)))

        # 4. ЛОГІКА БОТА
        is_bot_turn = (self.game_mode == "EvE") or (self.game_mode == "PvE" and self.current_turn == 2)

        # Бот думає ТІЛЬКИ якщо не йде анімація і гра в стані PLAYING
        if is_bot_turn and not self.is_animating_calculation and self.logic.state == GameState.PLAYING:
            self.ai_timer += 1

            # ФАЗА 0: ДУМАЄМО (1.5 сек)
            if self.ai_phase == 0:
                if self.ai_timer > 90:
                    self.ai_phase = 1;
                    self.ai_timer = 0

                    # ФАЗА 1: ВИБИРАЄМО КАРТИ
            elif self.ai_phase == 1:
                try:
                    # Пробуємо отримати хід від C++
                    found_move = self.logic.make_ai_turn()
                except Exception as e:
                    print(f"CRITICAL AI ERROR: {e}")
                    found_move = False

                if found_move:
                    # Якщо все ок
                    self.sync_cards_with_logic()
                    self.calculate_card_targets()
                    self.ai_phase = 2
                else:
                    # Якщо помилка або немає ходів
                    self.show_message("AI Error: Skip Turn", ERROR_COLOR)
                    self.logic.player.set_hp(-5)
                    if self.logic.player.get_hp() <= 0:
                        self.logic.state = GameState.GAME_OVER
                    else:
                        self.logic.start_card_selection()
                        self.logic.is_deadlock_recovery = True

                    self.ai_phase = 0
                self.ai_timer = 0

            # ФАЗА 2: ДИВИМОСЬ (1 сек паузи перед ударом)
            elif self.ai_phase == 2:
                if self.ai_timer > 60:
                    self.ai_phase = 3;
                    self.ai_timer = 0

            # ФАЗА 3: ТИСНЕМО "ОБЧИСЛИТИ"
            elif self.ai_phase == 3:
                valid, res = self.logic.preview_calculation()
                if valid:
                    # Запускаємо анімацію лічильника
                    self.is_animating_calculation = True
                    self.anim_start_time = pygame.time.get_ticks()
                    self.anim_target_value = res
                    self.anim_start_value = 0.0
                else:
                    self.switch_turn()  # Страховка від глюків

                self.ai_phase = 0;
                self.ai_timer = 0

        # Кнопки (тільки коли немає анімації)
        if not self.is_animating_calculation:
            self.calculate_button.draw(self.screen)
            self.clear_button.draw(self.screen)
            self.btn_back_to_menu_game.draw(self.screen)

        self.draw_message()

    def draw_merge_state(self):
        # Оновлюємо фізику для ВСІХ карт (включаючи спеціальні)
        for c in self.numb_cards + self.op_cards + self.special_cards:
            c.update()

        self.draw_target()
        self.draw_info()
        self.draw_zones_and_counters()

        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        hint = FONT_SMALL().render("Виберіть: [ЧИСЛО] -> [ОПЕРАЦІЯ] -> [ЧИСЛО]", True, ACCENT_COLOR)
        self.screen.blit(hint, hint.get_rect(center=(w // 2, 240)))

        # --- ВИПРАВЛЕННЯ ТУТ ---
        # Малюємо спеціальні карти теж!
        for c in self.numb_cards + self.op_cards + self.special_cards:
            c.draw(self.screen)

        self.confirm_merge_btn.draw(self.screen)
        self.skip_merge_btn.draw(self.screen)
        self.btn_back_to_menu_game.draw(self.screen)
        self.draw_message()

    def draw_selection_state(self):
        # Малюємо фон
        for c in self.numb_cards + self.op_cards + self.special_cards:
            c.update();
            c.draw(self.screen)
        self.draw_zones_and_counters()

        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220));
        self.screen.blit(overlay, (0, 0))

        if not self.choice_cards:
            self.update_choice_cards()
            if not self.choice_cards: return

        # --- АВТО-ДОБІР БОТА ---
        is_bot_turn = (self.game_mode == "EvE") or (self.game_mode == "PvE" and self.current_turn == 2)

        if is_bot_turn:
            self.ai_timer += 1
            if self.ai_timer > 25:
                self.ai_timer = 0
                import random

                needed = 1 if self.logic.state == GameState.SPECIAL_SELECTION else self.logic.selection_limit
                curr = len(self.logic.selected_choice_indices)

                # 1. Добираємо
                if curr < needed:
                    avail = [i for i in range(len(self.choice_cards)) if i not in self.logic.selected_choice_indices]
                    if avail:
                        pick = random.choice(avail)
                        if self.logic.select_new_card(pick):
                            self.choice_cards[pick].is_selected = True  # Візуал
                    else:
                        curr = needed

                        # 2. ПІДТВЕРДЖУЄМО
                if curr >= needed:
                    was_special_phase = (self.logic.state == GameState.SPECIAL_SELECTION)

                    self.choice_cards.clear()
                    self.logic.confirm_card_selection()

                    if was_special_phase:
                        # Бот обрав нагороду -> Новий раунд
                        self.sync_cards_with_logic()
                        self.update_choice_cards()  # Оновлюємо, якщо раптом треба

                    elif self.logic.state == GameState.PLAYING:
                        # Бот дібрав карти. Перевірка на перемогу.
                        if self.logic.round_won:
                            # Перемога -> Йдемо за спецкартою
                            self.logic.start_special_selection()
                            self.update_choice_cards()
                        else:
                            # Звичайний хід -> Передача ходу
                            self.sync_cards_with_logic()
                            self.switch_turn()

                    return
        # -----------------------

        # Текст
        title_txt = "Оберіть карти"
        if self.logic.state == GameState.SPECIAL_SELECTION: title_txt = "Оберіть СПЕЦКАРТУ! (Нагорода)"

        t_surf = FONT_LARGE().render(title_txt, True, ACCENT_COLOR)
        self.screen.blit(t_surf, t_surf.get_rect(center=(w // 2, 100)))

        for c in self.choice_cards: c.draw(self.screen)

        self.confirm_choice_btn.draw(self.screen)
        if not is_bot_turn:
            self.btn_clear_choices.draw(self.screen)
            self.btn_back_to_menu_game.draw(self.screen)

        self.draw_message()


    def draw_victory(self):
        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        self.screen.fill((0, 40, 0))

        # Показуємо ім'я переможця
        winner_name = self.logic.player_name

        title = FONT_TITLE().render("ПЕРЕМОГА!", True, SUCCESS_COLOR)
        subtitle = FONT_LARGE().render(f"Переміг: {winner_name}", True, TEXT_COLOR)

        self.screen.blit(title, title.get_rect(center=(w // 2, h // 2 - 50)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(w // 2, h // 2 + 20)))

        self.btn_back_to_menu_game.draw(self.screen)

    def draw_game_over(self):
        w, h = CONFIG["WIDTH"], CONFIG["HEIGHT"]
        self.screen.fill((40, 0, 0))

        title = FONT_TITLE().render("ГРА ЗАКІНЧЕНА", True, ERROR_COLOR)
        # Якщо це PvP, можна написати хто програв
        subtitle = FONT_LARGE().render(f"{self.logic.player_name} програв", True, TEXT_COLOR)

        self.screen.blit(title, title.get_rect(center=(w // 2, h // 2 - 50)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(w // 2, h // 2 + 20)))

        self.btn_back_to_menu_game.draw(self.screen)

    def switch_turn(self):
        """Передає хід наступному гравцю"""
        if self.current_turn == 1:
            self.current_turn = 2
            self.logic = self.logic_p2
        else:
            self.current_turn = 1
            self.logic = self.logic_p1

        # Сповіщення на екрані
        self.show_message(f"Хід гравця: {self.logic.player_name}", ACCENT_COLOR, duration=120)

        # Завантажуємо карти нового гравця на стіл
        self.sync_cards_with_logic()

        # Очищаємо чергу злиття
        self.merge_selection_queue.clear()

    # ==========================================
    # ГОЛОВНИЙ ЦИКЛ
    # ==========================================
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Розподіл подій за станами
                if self.settings_menu_active:
                    self.handle_settings_event(event)
                elif self.in_menu:
                    self.handle_menu_event(event)
                elif self.logic:
                    # Події гри
                    if self.logic.state == GameState.PLAYING:
                        self.handle_playing_state(event)
                    elif self.logic.state == GameState.MERGE_CHOICE:
                        self.handle_merge_state(event)
                    elif self.logic.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]:
                        self.handle_selection_state(event)
                    # Game Over/Victory - тільки вихід в меню
                    elif self.logic.state in [GameState.GAME_OVER, GameState.VICTORY]:
                        if self.btn_back_to_menu_game.handle_event(event):
                            self.in_menu = True
                            self.logic = None

            self.draw_background_grid()

            # Розподіл малювання
            if self.settings_menu_active:
                if self.in_menu: self.draw_menu()
                self.draw_settings_menu()
            elif self.in_menu:
                self.draw_menu()
            elif self.logic:
                if self.logic.state == GameState.PLAYING:
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