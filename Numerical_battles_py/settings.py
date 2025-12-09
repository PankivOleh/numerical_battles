import pygame

# --- КОНСТАНТИ ЕКРАНУ ---
WIDTH, HEIGHT = 1200, 800
FPS = 60

# --- КОЛЬОРИ ---
BG_COLOR = (20, 24, 30)
GRID_COLOR = (30, 35, 45)

# Кольори зон
ZONE_BG_COLOR = (28, 32, 40)
ZONE_BORDER_COLOR = (50, 60, 80)
ZONE_HEADER_COLOR = (40, 45, 60) # Для заголовка зони

# Карти (Новий дизайн)
CARD_BODY = (245, 245, 250)      # Біла основа
CARD_BACK = (45, 50, 65)         # Темна сорочка (для неактивних, якщо треба)
CARD_BORDER_DEFAULT = (100, 100, 120)
CARD_BORDER_SELECTED = (0, 180, 255)
CARD_BORDER_MERGE = (255, 180, 50)

# Текст на картах
CARD_TEXT_NUMB = (30, 30, 40)    # Темний текст для чисел
CARD_TEXT_OP = (0, 100, 200)     # Синій для операцій
CARD_TEXT_SPEC = (150, 50, 150)  # Фіолетовий для спец

TEXT_COLOR = (220, 220, 230)
ACCENT_COLOR = (0, 200, 255)

BUTTON_COLOR = (50, 100, 160)
BUTTON_HOVER = (70, 120, 190)
BUTTON_SELECTED = (60, 160, 100)

ERROR_COLOR = (220, 70, 70)
SUCCESS_COLOR = (70, 200, 100)

INPUT_BG_COLOR = (40, 44, 55)
INPUT_ACTIVE_BORDER = ACCENT_COLOR
INPUT_INACTIVE_BORDER = (80, 90, 110)

# --- ЗОНИ (Збільшені) ---
# Зона виразу (куди летять карти) - Центр екрану
RECT_EXPRESSION = pygame.Rect(0, 180, WIDTH, 120)

# Зона чисел
NUMB_ZONE_W, NUMB_ZONE_H = 850, 170  # Зробили вищою
RECT_NUMB = pygame.Rect((WIDTH - NUMB_ZONE_W) // 2, 480, NUMB_ZONE_W, NUMB_ZONE_H)

# Зона операцій
OP_ZONE_W, OP_ZONE_H = 850, 140      # Зробили вищою
RECT_OP = pygame.Rect((WIDTH - OP_ZONE_W) // 2, 660, OP_ZONE_W, OP_ZONE_H)

# Зона спеціальних карт
SPEC_ZONE_W, SPEC_ZONE_H = 180, 550
RECT_SPECIAL = pygame.Rect(WIDTH - SPEC_ZONE_W - 20, 120, SPEC_ZONE_W, SPEC_ZONE_H)

# --- ШРИФТИ ---
_fonts = {}

def get_font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont("Arial", size, bold=True)
    return _fonts[size]

def FONT_TITLE(): return get_font(80)
def FONT_LARGE(): return get_font(50)
def FONT_MEDIUM(): return get_font(32)
def FONT_SMALL(): return get_font(24)
def FONT_TINY(): return get_font(18)