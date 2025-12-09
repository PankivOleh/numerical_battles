import pygame
import sys
from game_logic import GameLogic, GameState

# Ініціалізація pygame
pygame.init()

# Константи
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Кольори
BG_COLOR = (25, 25, 35)
CARD_BG = (45, 45, 60)
CARD_HOVER = (65, 65, 85)
CARD_SELECTED = (85, 120, 180)
TEXT_COLOR = (240, 240, 250)
ACCENT_COLOR = (100, 200, 255)
BUTTON_COLOR = (60, 140, 200)
BUTTON_HOVER = (80, 160, 220)
ERROR_COLOR = (220, 80, 80)
SUCCESS_COLOR = (80, 220, 120)

# Шрифти
FONT_LARGE = pygame.font.Font(None, 64)
FONT_MEDIUM = pygame.font.Font(None, 42)
FONT_SMALL = pygame.font.Font(None, 28)
FONT_TINY = pygame.font.Font(None, 22)


class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = BUTTON_HOVER
        self.is_hovered = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 2, border_radius=8)

        text_surf = FONT_SMALL.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


class Card:
    def __init__(self, x, y, width, height, value, card_type, index):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = value
        self.card_type = card_type
        self.index = index
        self.is_hovered = False
        self.is_selected = False

    def draw(self, screen):
        if self.is_selected:
            color = CARD_SELECTED
        elif self.is_hovered:
            color = CARD_HOVER
        else:
            color = CARD_BG

        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 2, border_radius=10)

        # Відображення значення
        if self.card_type == 'special':
            text = f"SP\n{self.value}"
            lines = text.split('\n')
            y_offset = self.rect.centery - 15
            for line in lines:
                text_surf = FONT_SMALL.render(line, True, ACCENT_COLOR)
                text_rect = text_surf.get_rect(center=(self.rect.centerx, y_offset))
                screen.blit(text_surf, text_rect)
                y_offset += 25
        else:
            font = FONT_MEDIUM if self.card_type == 'numb' else FONT_LARGE
            text_surf = font.render(str(self.value), True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Numerical Battles")
        self.clock = pygame.time.Clock()
        self.running = True

        self.logic = GameLogic("Player", difficulty=1)

        # UI елементи
        self.numb_cards = []
        self.op_cards = []
        self.special_cards = []
        self.choice_cards = []

        self.calculate_button = Button(WIDTH // 2 - 100, 250, 200, 50, "Обчислити")
        self.clear_button = Button(WIDTH // 2 - 250, 250, 130, 50, "Очистити")
        self.merge_button = Button(WIDTH // 2 + 130, 250, 130, 50, "Об'єднати")

        self.skip_merge_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Пропустити")
        self.confirm_button = Button(WIDTH // 2 - 100, HEIGHT - 80, 200, 50, "Підтвердити")

        self.message = ""
        self.message_color = TEXT_COLOR
        self.message_timer = 0

        self.update_cards()

    def update_cards(self):
        """Оновлення карт на екрані"""
        numb_data, op_data, special_data = self.logic.get_hand_data()

        # Карти чисел
        self.numb_cards = []
        card_width, card_height = 80, 100
        start_x = 50
        y_pos = HEIGHT - 250

        for i, value in enumerate(numb_data):
            x = start_x + i * (card_width + 15)
            card = Card(x, y_pos, card_width, card_height, value, 'numb', i)
            self.numb_cards.append(card)

        # Карти операцій
        self.op_cards = []
        y_pos = HEIGHT - 130

        for i, value in enumerate(op_data):
            x = start_x + i * (card_width + 15)
            card = Card(x, y_pos, card_width, card_height, value, 'op', i)
            self.op_cards.append(card)

        # Спеціальні карти
        self.special_cards = []
        start_x = WIDTH - 250
        y_pos = HEIGHT - 250

        for i, value in enumerate(special_data):
            x = start_x
            y = y_pos + i * (card_height + 15)
            card = Card(x, y, card_width, card_height, value, 'special', i)
            self.special_cards.append(card)

    def update_choice_cards(self):
        """Оновлення карт вибору"""
        self.choice_cards = []
        choices = self.logic.get_choice_data()

        card_width, card_height = 80, 100
        total_width = len(choices) * (card_width + 15)
        start_x = (WIDTH - total_width) // 2
        y_pos = HEIGHT // 2

        for i, (card_type, value) in enumerate(choices):
            x = start_x + i * (card_width + 15)
            card = Card(x, y_pos, card_width, card_height, value, card_type, i)
            if i in self.logic.selected_choice_indices:
                card.is_selected = True
            self.choice_cards.append(card)

    def draw_target(self):
        """Відображення цільового числа"""
        target_text = f"Ціль: {self.logic.target_number:.2f}"
        text_surf = FONT_LARGE.render(target_text, True, ACCENT_COLOR)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(text_surf, text_rect)

    def draw_selected_expression(self):
        """Відображення вибраного виразу"""
        expr = self.logic.build_expression()
        if expr:
            text_surf = FONT_MEDIUM.render(f"Вираз: {expr}", True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 180))
            self.screen.blit(text_surf, text_rect)

    def draw_info(self):
        """Відображення інформації про гравця"""
        info_texts = [
            f"HP: {self.logic.player.get_hp()}",
            f"Рівень: {self.logic.level}/{self.logic.max_level}",
            f"Складність: {self.logic.difficulty}"
        ]

        y_pos = 20
        for text in info_texts:
            text_surf = FONT_SMALL.render(text, True, TEXT_COLOR)
            self.screen.blit(text_surf, (20, y_pos))
            y_pos += 30

    def draw_message(self):
        """Відображення повідомлення"""
        if self.message and self.message_timer > 0:
            text_surf = FONT_SMALL.render(self.message, True, self.message_color)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 320))
            self.screen.blit(text_surf, text_rect)
            self.message_timer -= 1

    def show_message(self, text, color=TEXT_COLOR, duration=180):
        """Показати повідомлення"""
        self.message = text
        self.message_color = color
        self.message_timer = duration

    def handle_playing_state(self, event):
        """Обробка стану гри"""
        # Обробка карт чисел
        for card in self.numb_cards:
            if card.handle_event(event):
                self.logic.select_card('numb', card.index)
                self.update_cards()

        # Обробка карт операцій
        for card in self.op_cards:
            if card.handle_event(event):
                self.logic.select_card('op', card.index)
                self.update_cards()

        # Обробка спеціальних карт
        for card in self.special_cards:
            if card.handle_event(event):
                if self.logic.use_special_card(card.index):
                    self.show_message(f"Спеціальна карта використана! Нова ціль: {self.logic.target_number:.2f}",
                                      SUCCESS_COLOR)
                    self.update_cards()

        # Кнопка обчислення
        if self.calculate_button.handle_event(event):
            success, msg = self.logic.calculate_result()
            color = SUCCESS_COLOR if success else ERROR_COLOR
            self.show_message(msg, color)

            if self.logic.state == GameState.GAME_OVER:
                return

            if success or not success:
                # Переходимо до фази об'єднання
                self.logic.start_merge_phase()

            self.update_cards()

        # Кнопка очищення
        if self.clear_button.handle_event(event):
            self.logic.clear_selection()
            self.show_message("Вибір очищено", TEXT_COLOR, 60)

        # Кнопка об'єднання
        if self.merge_button.handle_event(event):
            self.logic.start_merge_phase()

    def handle_merge_state(self, event):
        """Обробка стану об'єднання"""
        selected_numb = []
        selected_op = []

        for card in self.numb_cards:
            if card.handle_event(event):
                card.is_selected = not card.is_selected
                if card.is_selected and len(selected_numb) < 2:
                    selected_numb.append(card.index)

        for card in self.op_cards:
            if card.handle_event(event):
                card.is_selected = not card.is_selected
                if card.is_selected and len(selected_op) < 1:
                    selected_op.append(card.index)

        # Рахуємо вибрані карти
        selected_numb = [c.index for c in self.numb_cards if c.is_selected]
        selected_op = [c.index for c in self.op_cards if c.is_selected]

        # Кнопка підтвердження об'єднання
        if self.confirm_button.handle_event(event):
            if len(selected_numb) == 2 and len(selected_op) == 1:
                success, msg = self.logic.merge_cards(selected_numb[0], selected_op[0], selected_numb[1])
                color = SUCCESS_COLOR if success else ERROR_COLOR
                self.show_message(msg, color)

                if success:
                    self.update_cards()
                    self.logic.start_card_selection()
                    self.update_choice_cards()
            else:
                self.show_message("Виберіть 2 числа та 1 операцію!", ERROR_COLOR)

        # Кнопка пропуску
        if self.skip_merge_button.handle_event(event):
            self.logic.skip_merge()
            self.update_choice_cards()

    def handle_selection_state(self, event):
        """Обробка стану вибору карт"""
        for card in self.choice_cards:
            if card.handle_event(event):
                self.logic.select_new_card(card.index)
                self.update_choice_cards()

        if self.confirm_button.handle_event(event):
            if len(self.logic.selected_choice_indices) > 0:
                self.logic.confirm_card_selection()

                if self.logic.state == GameState.SPECIAL_SELECTION:
                    self.update_choice_cards()
                elif self.logic.state == GameState.PLAYING:
                    self.update_cards()
                    self.show_message(f"Раунд {self.logic.level} починається!", ACCENT_COLOR)
                elif self.logic.state == GameState.VICTORY:
                    pass
            else:
                self.show_message("Виберіть хоча б одну карту!", ERROR_COLOR)

    def draw_playing_state(self):
        """Відображення стану гри"""
        self.draw_target()
        self.draw_selected_expression()
        self.draw_info()

        # Карти
        for card in self.numb_cards:
            if card.index in self.logic.selected_indices['numb']:
                card.is_selected = True
            else:
                card.is_selected = False
            card.draw(self.screen)

        for card in self.op_cards:
            if card.index in self.logic.selected_indices['op']:
                card.is_selected = True
            else:
                card.is_selected = False
            card.draw(self.screen)

        for card in self.special_cards:
            card.draw(self.screen)

        # Кнопки
        self.calculate_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.merge_button.draw(self.screen)

        self.draw_message()

    def draw_merge_state(self):
        """Відображення стану об'єднання"""
        title = FONT_LARGE.render("Об'єднання карт", True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        info = FONT_SMALL.render("Виберіть 2 числа та 1 операцію", True, TEXT_COLOR)
        info_rect = info.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(info, info_rect)

        # Карти
        for card in self.numb_cards:
            card.draw(self.screen)

        for card in self.op_cards:
            card.draw(self.screen)

        # Кнопки
        self.confirm_button.draw(self.screen)
        self.skip_merge_button.draw(self.screen)

        self.draw_message()

    def draw_selection_state(self):
        """Відображення стану вибору карт"""
        if self.logic.state == GameState.CARD_SELECTION:
            title_text = "Виберіть до 3 карт"
        else:
            title_text = "Виберіть 1 спеціальну карту"

        title = FONT_LARGE.render(title_text, True, ACCENT_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Карти вибору
        for card in self.choice_cards:
            card.draw(self.screen)

        # Кнопка підтвердження
        self.confirm_button.draw(self.screen)

        self.draw_message()

    def draw_game_over(self):
        """Відображення екрану програшу"""
        title = FONT_LARGE.render("Гра закінчена!", True, ERROR_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)

        info = FONT_MEDIUM.render(f"Досягнуто рівень: {self.logic.level}", True, TEXT_COLOR)
        info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(info, info_rect)

    def draw_victory(self):
        """Відображення екрану перемоги"""
        title = FONT_LARGE.render("Перемога!", True, SUCCESS_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)

        info = FONT_MEDIUM.render(f"Пройдено всі {self.logic.max_level} рівнів!", True, TEXT_COLOR)
        info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(info, info_rect)

    def run(self):
        """Головний цикл гри"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Обробка подій залежно від стану
                if self.logic.state == GameState.PLAYING:
                    self.handle_playing_state(event)
                elif self.logic.state == GameState.MERGE_CHOICE:
                    self.handle_merge_state(event)
                elif self.logic.state in [GameState.CARD_SELECTION, GameState.SPECIAL_SELECTION]:
                    self.handle_selection_state(event)

                # Обробка подій для кнопок
                for button in [self.calculate_button, self.clear_button, self.merge_button,
                               self.skip_merge_button, self.confirm_button]:
                    button.handle_event(event)

            # Відображення
            self.screen.fill(BG_COLOR)

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