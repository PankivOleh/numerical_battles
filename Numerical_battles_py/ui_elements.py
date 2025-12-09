import pygame
from settings import *


class TextInput:
    def __init__(self, x, y, w, h, placeholder="Enter Name"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.color = INPUT_INACTIVE_BORDER
        self.txt_surface = FONT_MEDIUM().render(placeholder, True, (100, 100, 120))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = INPUT_ACTIVE_BORDER if self.active else INPUT_INACTIVE_BORDER

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = INPUT_INACTIVE_BORDER
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 12:
                        self.text += event.unicode

                txt = self.text if self.text else self.placeholder
                col = TEXT_COLOR if self.text else (100, 100, 120)
                self.txt_surface = FONT_MEDIUM().render(txt, True, col)

    def draw(self, screen):
        pygame.draw.rect(screen, INPUT_BG_COLOR, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=10)
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)


class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.color = color
        self.hover_color = BUTTON_HOVER
        self.is_hovered = False
        self.is_selected = False

    def draw(self, screen):
        draw_color = BUTTON_SELECTED if self.is_selected else (self.hover_color if self.is_hovered else self.color)

        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=12)

        pygame.draw.rect(screen, draw_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255, 30), self.rect, 1, border_radius=12)

        text_surf = FONT_SMALL().render(self.text, True, TEXT_COLOR)
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
        self.width = width
        self.height = height
        self.current_pos = pygame.Vector2(x, y)
        self.target_pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, width, height)

        self.value = value
        self.card_type = card_type
        self.index = index

        self.is_hovered = False
        self.is_selected = False
        self.is_merge_selected = False

        self.update_text(value)

    def update_text(self, value):
        self.value = value
        if isinstance(value, (int, float)) and self.card_type != 'op':
            formatted = f"{value:.3f}"
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            self.display_text = formatted
        else:
            self.display_text = str(value)

    def update(self):
        direction = self.target_pos - self.current_pos
        dist = direction.length()
        if dist > 0.5:
            self.current_pos += direction * 0.15
        else:
            self.current_pos = self.target_pos.copy()

        self.rect.topleft = (int(self.current_pos.x), int(self.current_pos.y))

    def fit_text(self, text, max_width, initial_font_size, color):
        size = initial_font_size
        font = get_font(size)
        while font.size(text)[0] > max_width - 14 and size > 14:
            size -= 2
            font = get_font(size)
        return font.render(text, True, color)

    def draw(self, screen):
        # --- ЛОГІКА "СПЛИВАННЯ" ---
        # Якщо на карту навели мишкою, малюємо її на 25 пікселів вище
        draw_y_offset = -25 if (self.is_hovered and not self.is_selected) else 0

        # Створюємо тимчасовий rect для малювання
        draw_rect = pygame.Rect(self.rect.x, self.rect.y + draw_y_offset, self.width, self.height)

        if self.is_merge_selected:
            border_col = CARD_BORDER_MERGE; border_w = 4
        elif self.is_selected:
            border_col = CARD_BORDER_SELECTED; border_w = 4
        elif self.is_hovered:
            border_col = (180, 180, 200); border_w = 2
        else:
            border_col = CARD_BORDER_DEFAULT; border_w = 1

        # Тінь
        shadow_rect = pygame.Rect(draw_rect.x + 4, draw_rect.y + 4, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0, 60), shadow_rect, border_radius=10)

        # Основа
        pygame.draw.rect(screen, CARD_BODY, draw_rect, border_radius=10)

        # Шапка
        header_h = 25
        header_col = (200, 200, 200)
        if self.card_type == 'op':
            header_col = (200, 220, 255)
        elif self.card_type == 'special':
            header_col = (240, 200, 240)

        pygame.draw.rect(screen, header_col, (draw_rect.x, draw_rect.y, self.width, header_h),
                         border_top_left_radius=10, border_top_right_radius=10)

        # Рамка
        pygame.draw.rect(screen, border_col, draw_rect, border_w, border_radius=10)

        # Текст
        center_y = draw_rect.y + (self.height + header_h) // 2

        if self.card_type == 'special':
            text_surf = self.fit_text(self.display_text, self.width, 36, CARD_TEXT_SPEC)
            lbl = FONT_TINY().render("SPEC", True, (100, 80, 100))
            screen.blit(lbl, lbl.get_rect(center=(draw_rect.centerx, draw_rect.y + 12)))
        elif self.card_type == 'op':
            text_surf = FONT_LARGE().render(self.display_text, True, CARD_TEXT_OP)
        else:
            text_surf = self.fit_text(self.display_text, self.width, 48, CARD_TEXT_NUMB)

        text_rect = text_surf.get_rect(center=(draw_rect.centerx, center_y))
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False