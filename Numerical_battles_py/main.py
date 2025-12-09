import pygame
import sys
from game_logic import GameLogic, GameState
from settings import *
from ui_elements import Button, Card, TextInput

# Ініціалізація pygame
pygame.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Numerical Battles")
        self.clock = pygame.time.Clock()
        self.running = True

        # --- МЕНЮ ---
        self.in_menu = True
        self.player_name = "Player"
        self.selected_difficulty = 1

        self.name_input = TextInput(WIDTH // 2 - 150, 300, 300, 50)
        self.btn_diff_1 = Button(WIDTH // 2 - 200, 420, 120, 50, "EASY")
        self.btn_diff_2 = Button(WIDTH // 2 - 60, 420, 120, 50, "NORMAL")
        self.btn_diff_3 = Button(WIDTH // 2 + 80, 420, 120, 50, "HARD")
        self.btn_diff_1.is_selected = True
        self.btn_start = Button(WIDTH // 2 - 100, 550, 200, 60, "START GAME", color=SUCCESS_COLOR)

        self.logic = None

        self.numb_cards = []
        self.op_cards = []
        self.special_cards = []
        self.choice_cards = []

        # --- КНОПКИ ГРИ ---
        btn_y = 350
        self.calculate_button = Button(WIDTH // 2 - 90, btn_y, 180, 50, "ОБЧИСЛИТИ")
        self.clear_button = Button(WIDTH // 2 - 240, btn_y, 130, 50, "Очистити")

        self.confirm_merge_btn = Button(RECT_SPECIAL.centerx - 80, 680, 160, 50, "ПІДТВЕРДИТИ", color=SUCCESS_COLOR)
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
        self.update_cards()

    def update_cards(self):
        if not self.logic: return
        numb_data, op_data, special_data = self.logic.get_hand_data()

        self.numb_cards = []
        self.op_cards = []
        self.special_cards = []

        # Центрування Чисел
        card_w, card_h = 70, 90
        gap = 10
        total_w = len(numb_data) * (card_w + gap) - gap
        start_x = RECT_NUMB.centerx - (total_w // 2)
        y_pos = RECT_NUMB.centery - (card_h // 2)

        for i, value in enumerate(numb_data):
            x = start_x + i * (card_w + gap)
            if x < RECT_NUMB.left + 10:
                overlap = (total_w - (RECT_NUMB.width - 20)) / (len(numb_data) - 1) if len(numb_data) > 1 else 0
                x = RECT_NUMB.left + 10 + i * (card_w + gap - overlap)

            card = Card(x, y_pos, card_w, card_h, value, 'numb', i)
            if i in self.logic.selected_indices['numb']: card.is_selected = True
            self.numb_cards.append(card)

        # Центрування Операцій
        total_w_op = len(op_data) * (card_w + gap) - gap
        start_x_op = RECT_OP.centerx - (total_w_op // 2)
        y_pos_op = RECT_OP.centery - (card_h // 2)

        for i, value in enumerate(op_data):
            x = start_x_op + i * (card_w + gap)
            card = Card(x, y_pos_op, card_w, card_h, value, 'op', i)
            if i in self.logic.selected_indices['op']: card.is_selected = True
            self.op_cards.append(card)

        # Спецкарти
        start_y_spec = RECT_SPECIAL.top + 50
        for i, value in enumerate(special_data):
            x = RECT_SPECIAL.centerx - (card_w // 2)
            y = start_y_spec + i * (card_h + 15)
            card = Card(x, y, card_w, card_h, value, 'special', i)
            self.special_cards.append(card)

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

    # --- DRAWING HELPERS ---
    def draw_background_grid(self):
        self.screen.fill(BG_COLOR)
        grid_size = 40
        for x in range(0, WIDTH, grid_size):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, grid_size):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

    def draw_zones_and_counters(self):
        def draw_zone(rect, title, count, max_count):
            pygame.draw.rect(self.screen, ZONE_BG_COLOR, rect, border_radius=15)
            pygame.draw.rect(self.screen, ZONE_BORDER_COLOR, rect, 2, border_radius=15)

            title_surf = FONT_TINY().render(title, True, (150, 150, 170))
            self.screen.blit(title_surf, (rect.x + 20, rect.y + 10))

            cnt_color = SUCCESS_COLOR if count < max_count else ERROR_COLOR
            cnt_surf = FONT_SMALL().render(f"{count}/{max_count}", True, cnt_color)
            self.screen.blit(cnt_surf, (rect.right - 60, rect.y + 10))

        if self.logic:
            h = self.logic.player.get_hand()
            draw_zone(RECT_NUMB, "ЧИСЛА", h.get_numb_count(), 10)
            draw_zone(RECT_OP, "ОПЕРАЦІЇ", h.get_operator_count(), 6)
            draw_zone(RECT_SPECIAL, "СПЕЦІАЛЬНІ", h.get_special_count(), 5)

    def draw_target(self):
        if not self.logic: return
        target_panel = pygame.Rect(WIDTH // 2 - 200, 30, 400, 80)
        pygame.draw.rect(self.screen, ZONE_BG_COLOR, target_panel, border_radius=20)
        pygame.draw.rect(self.screen, ACCENT_COLOR, target_panel, 2, border_radius=20)

        target_text = f"{self.logic.target_number:.3f}".rstrip('0').rstrip('.')

        lbl = FONT_SMALL().render("ЦІЛЬОВЕ ЧИСЛО", True, (150, 150, 150))
        self.screen.blit(lbl, lbl.get_rect(center=(WIDTH // 2, 50)))

        text_surf = FONT_LARGE().render(target_text, True, ACCENT_COLOR)
        self.screen.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, 85)))

    def draw_selected_expression(self):
        if not self.logic: return
        expr = self.logic.build_expression()
        if expr:
            text_surf = FONT_MEDIUM().render(f"{expr} = ?", True, TEXT_COLOR)
            bg_rect = text_surf.get_rect(center=(WIDTH // 2, 170))
            bg_rect.inflate_ip(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 150), bg_rect, border_radius=10)
            self.screen.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, 170)))

    def draw_info(self):
        if not self.logic: return
        info_x = 30
        info_y = 30
        texts = [
            (f"{self.logic.player_name}", ACCENT_COLOR),
            (f"HP: {self.logic.player.get_hp()}", SUCCESS_COLOR),
            (f"LVL: {self.logic.level}", TEXT_COLOR),
        ]
        for txt, col in texts:
            surf = FONT_SMALL().render(txt, True, col)
            self.screen.blit(surf, (info_x, info_y))
            info_y += 30

    def show_message(self, text, color=TEXT_COLOR, duration=120):
        self.message = text
        self.message_color = color
        self.message_timer = duration

    def draw_message(self):
        if self.message and self.message_timer > 0:
            text_surf = FONT_MEDIUM().render(self.message, True, self.message_color)
            bg_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            bg_rect.inflate_ip(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 220), bg_rect, border_radius=10)
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
        for card in self.numb_cards + self.op_cards:
            if card.handle_event(event):
                self.logic.select_card(card.card_type, card.index)
                self.update_cards()

        spec_used = False
        for card in self.special_cards:
            if card.handle_event(event):
                if self.logic.use_special_card(card.index):
                    self.show_message("Спец. ефект застосовано!", SUCCESS_COLOR)
                    self.update_cards()
                    spec_used = True
                    break
        if spec_used: return

        if self.calculate_button.handle_event(event):
            success, msg = self.logic.calculate_result()
            self.show_message(msg, SUCCESS_COLOR if success else ERROR_COLOR)
            if "Виберіть" not in msg and "Потрібна" not in msg:
                self.logic.start_merge_phase()
                for c in self.numb_cards + self.op_cards:
                    c.is_selected = False
                    c.is_merge_selected = False
            self.update_cards()

        if self.clear_button.handle_event(event):
            self.logic.clear_selection()
            self.update_cards()

    def handle_merge_state(self, event):
        for card in self.numb_cards + self.op_cards:
            if card.handle_event(event):
                card.is_merge_selected = not card.is_merge_selected

        if self.confirm_merge_btn.handle_event(event):
            sel_numb = [c.index for c in self.numb_cards if c.is_merge_selected]
            sel_op = [c.index for c in self.op_cards if c.is_merge_selected]

            if len(sel_numb) == 2 and len(sel_op) == 1:
                success, msg = self.logic.merge_cards(sel_numb[0], sel_op[0], sel_numb[1])
                self.show_message(msg, SUCCESS_COLOR if success else ERROR_COLOR)
                if success:
                    self.update_cards()
                    self.logic.start_card_selection()
                    self.update_choice_cards()
            else:
                self.show_message("Оберіть: [ЧИСЛО] [ОП] [ЧИСЛО]", ERROR_COLOR)

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
                if self.logic.state == GameState.PLAYING:
                    self.update_cards()
                elif self.logic.state == GameState.SPECIAL_SELECTION:
                    self.update_choice_cards()
            else:
                self.show_message("Оберіть хоча б одну карту!", ERROR_COLOR)

    # --- MAIN DRAW LOOPS (Тут був пропущений код) ---
    def draw_menu(self):
        title = FONT_TITLE().render("NUMERICAL BATTLES", True, ACCENT_COLOR)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
        lbl_name = FONT_SMALL().render("Введіть ім'я:", True, TEXT_COLOR)
        self.screen.blit(lbl_name, (WIDTH // 2 - 150, 275))
        self.name_input.draw(self.screen)
        lbl_diff = FONT_SMALL().render("Оберіть складність:", True, TEXT_COLOR)
        self.screen.blit(lbl_diff, (WIDTH // 2 - 150, 395))
        self.btn_diff_1.draw(self.screen)
        self.btn_diff_2.draw(self.screen)
        self.btn_diff_3.draw(self.screen)
        self.btn_start.draw(self.screen)

    def draw_playing_state(self):
        self.draw_target()
        self.draw_selected_expression()
        self.draw_info()
        self.draw_zones_and_counters()
        for c in self.numb_cards + self.op_cards + self.special_cards:
            c.draw(self.screen)
        self.calculate_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.draw_message()

    def draw_merge_state(self):
        self.draw_target()
        self.draw_zones_and_counters()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        title = FONT_LARGE().render("РЕЖИМ ЗЛИТТЯ", True, ACCENT_COLOR)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 200)))
        hint = FONT_SMALL().render("Виберіть 2 числа та 1 операцію для створення нового числа", True, TEXT_COLOR)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 240)))

        for c in self.numb_cards + self.op_cards:
            c.draw(self.screen)

        self.confirm_merge_btn.draw(self.screen)
        self.skip_merge_btn.draw(self.screen)
        self.draw_message()

    def draw_selection_state(self):
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

                if self.in_menu:
                    self.handle_menu_event(event)
                elif self.logic.state == GameState.PLAYING:
                    self.handle_playing_state(event)
                elif self.logic.state == GameState.MERGE_CHOICE:
                    self.handle_merge_state(event)
                elif self.logic.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]:
                    self.handle_selection_state(event)

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