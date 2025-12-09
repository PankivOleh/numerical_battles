import pygame

# --- КОНСТАНТИ ЕКРАНУ ---
WIDTH, HEIGHT = 1200, 800
FPS = 60

# --- КОЛЬОРИ (Палітра "Cyber-Math") ---
BG_COLOR = (20, 24, 30)         # Темно-синій фон
GRID_COLOR = (30, 35, 45)       # Колір сітки
ZONE_BG_COLOR = (30, 34, 45)    # Фон зон
ZONE_BORDER_COLOR = (50, 60, 80)

# Карти
CARD_BG = (45, 50, 65)
CARD_BORDER = (200, 200, 200)   # Біла рамка для контрасту
CARD_HOVER = (60, 70, 90)
CARD_SELECTED = (70, 130, 200)       # Яскраво-синій
CARD_MERGE_SELECTED = (220, 170, 50) # Золотий

TEXT_COLOR = (240, 240, 250)
ACCENT_COLOR = (0, 200, 255)    # Неон-блакитний

# Кнопки
BUTTON_COLOR = (50, 100, 160)
BUTTON_HOVER = (70, 120, 190)
BUTTON_SELECTED = (60, 160, 100)

ERROR_COLOR = (220, 70, 70)
SUCCESS_COLOR = (70, 200, 100)

INPUT_BG_COLOR = (40, 44, 55)
INPUT_ACTIVE_BORDER = ACCENT_COLOR
INPUT_INACTIVE_BORDER = (80, 90, 110)

# --- ЗОНИ (Симетричні розрахунки) ---
# Зона чисел (Центр знизу)
NUMB_ZONE_W, NUMB_ZONE_H = 820, 140
RECT_NUMB = pygame.Rect((WIDTH - NUMB_ZONE_W) // 2, 520, NUMB_ZONE_W, NUMB_ZONE_H)

# Зона операцій (Центр під числами)
OP_ZONE_W, OP_ZONE_H = 820, 110
RECT_OP = pygame.Rect((WIDTH - OP_ZONE_W) // 2, 670, OP_ZONE_W, OP_ZONE_H)

# Зона спеціальних карт (Справа, вертикальна)
SPEC_ZONE_W, SPEC_ZONE_H = 160, 500
RECT_SPECIAL = pygame.Rect(WIDTH - SPEC_ZONE_W - 30, 150, SPEC_ZONE_W, SPEC_ZONE_H)

# --- ШРИФТИ ---
_fonts = {}

def get_font(size):
    if size not in _fonts:
        # Використовуємо системний шрифт для кращої читабельності чисел
        _fonts[size] = pygame.font.SysFont("Arial", size, bold=True)
    return _fonts[size]

def FONT_TITLE(): return get_font(80)
def FONT_LARGE(): return get_font(56)   # Для чисел на картах
def FONT_MEDIUM(): return get_font(36)
def FONT_SMALL(): return get_font(24)
def FONT_TINY(): return get_font(18)