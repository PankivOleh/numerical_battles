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

        # Тінь кнопки
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)

        # Основне тіло
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255, 30), self.rect, 1, border_radius=12)  # Блик

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
        self.rect = pygame.Rect(x, y, width, height)
        self.value = value
        self.card_type = card_type
        self.index = index
        self.is_hovered = False
        self.is_selected = False
        self.is_merge_selected = False

        # --- ФОРМАТУВАННЯ ЧИСЛА ---
        if isinstance(value, (int, float)) and card_type != 'op':
            # Форматуємо до 3 знаків
            formatted = f"{value:.3f}"
            # Видаляємо зайві нулі та крапку в кінці (5.500 -> 5.5, 5.000 -> 5)
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            self.display_text = formatted
        else:
            self.display_text = str(value)

    def fit_text(self, text, max_width, initial_font_size):
        """Зменшує шрифт, доки текст не влізе в задану ширину"""
        size = initial_font_size
        font = get_font(size)
        while font.size(text)[0] > max_width - 10 and size > 12:
            size -= 4
            font = get_font(size)
        return font.render(text, True, TEXT_COLOR)

    def draw(self, screen):
        # Колір
        if self.is_merge_selected:
            color = CARD_MERGE_SELECTED
        elif self.is_selected:
            color = CARD_SELECTED
        elif self.is_hovered:
            color = CARD_HOVER
        else:
            color = CARD_BG

        # Тінь
        pygame.draw.rect(screen, (0, 0, 0, 80), self.rect.move(3, 3), border_radius=12)

        # Основа
        pygame.draw.rect(screen, color, self.rect, border_radius=12)

        # Рамка (якщо карта спеціальна - рамка інша)
        border_col = ACCENT_COLOR if self.card_type == 'special' else CARD_BORDER
        border_width = 3 if (self.is_selected or self.is_merge_selected) else 1
        pygame.draw.rect(screen, border_col, self.rect, border_width, border_radius=12)

        # Малювання тексту з авто-масштабуванням
        if self.card_type == 'special':
            text_surf = self.fit_text(self.display_text, self.rect.width, 42)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

            lbl = FONT_TINY().render("SPEC", True, (150, 150, 150))
            lbl_rect = lbl.get_rect(center=(self.rect.centerx, self.rect.top + 15))
            screen.blit(lbl, lbl_rect)
        elif self.card_type == 'op':
            text_surf = FONT_LARGE().render(self.display_text, True, ACCENT_COLOR)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
        else:
            # Для чисел - масштабуємо
            text_surf = self.fit_text(self.display_text, self.rect.width, 56)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False