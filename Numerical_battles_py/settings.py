import pygame

# --- КОНФІГУРАЦІЯ ---
CONFIG = {
    "WIDTH": 1280,
    "HEIGHT": 720,
    "FULLSCREEN": True
}

FPS = 60
RESOLUTIONS = [(1280, 720), (1366, 768), (1600, 900), (1920, 1080)]

# --- КОЛЬОРИ (MICROSOFT FLUENT DARK) ---
# Основний фон (темний, але не чорний)
BG_COLOR = (32, 32, 32)
GRID_COLOR = (43, 43, 43)     # Дуже тонкий контраст

# Зони (Surface colors)
ZONE_BG_COLOR = (45, 45, 45)
ZONE_BORDER_COLOR = (60, 60, 60)
ZONE_HEADER_COLOR = (55, 55, 55)

# Карти (Світлі, щоб виділятися на темному, clean look)
CARD_BODY = (243, 243, 243)
CARD_BORDER_DEFAULT = (130, 130, 130)
CARD_BORDER_SELECTED = (0, 120, 212)  # Microsoft Blue
CARD_BORDER_MERGE = (255, 140, 0)     # Orange

# Текст на картах (Контрастний темний)
CARD_TEXT_NUMB = (30, 30, 30)
CARD_TEXT_OP = (0, 90, 158)
CARD_TEXT_SPEC = (135, 100, 184)

# Основний текст інтерфейсу
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 120, 212)     # Segoe Blue

# Кнопки (Standard Controls)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER = (65, 65, 65)
BUTTON_SELECTED = (0, 120, 212)

# Статуси (System colors)
ERROR_COLOR = (232, 17, 35)      # Windows Red
SUCCESS_COLOR = (16, 124, 16)    # Windows Green

# Поля вводу
INPUT_BG_COLOR = (25, 25, 25)
INPUT_ACTIVE_BORDER = ACCENT_COLOR
INPUT_INACTIVE_BORDER = (100, 100, 100)

# --- ШРИФТИ (SEGOE UI) ---
_fonts = {}

def get_font(size):
    if size not in _fonts:
        # Пріоритет на стандартний шрифт Windows 10/11
        try:
            _fonts[size] = pygame.font.SysFont("Segoe UI", size) # Звичайний, не жирний для сучасності
        except:
            try:
                _fonts[size] = pygame.font.SysFont("Calibri", size)
            except:
                _fonts[size] = pygame.font.SysFont("Arial", size)
    return _fonts[size]

# Розміри шрифтів (трохи менші для акуратності)
def FONT_TITLE(): return get_font(64)
def FONT_LARGE(): return get_font(48)
def FONT_MEDIUM(): return get_font(24)
def FONT_SMALL(): return get_font(18)
def FONT_TINY(): return get_font(14)

# --- ГЕОМЕТРІЯ ЗОН ---
def GET_RECT_NUMB():
    w, h = 850, 170
    return pygame.Rect((CONFIG["WIDTH"] - w) // 2, CONFIG["HEIGHT"] - 320, w, h)

def GET_RECT_OP():
    w, h = 850, 140
    return pygame.Rect((CONFIG["WIDTH"] - w) // 2, CONFIG["HEIGHT"] - 140, w, h)

def GET_RECT_SPECIAL():
    w, h = 180, 480
    return pygame.Rect(CONFIG["WIDTH"] - w - 20, 120, w, h)

def GET_RECT_EXPRESSION():
    return pygame.Rect(0, 180, CONFIG["WIDTH"], 120)