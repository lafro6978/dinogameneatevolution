import os
import sys
import json
import logging
import functools
import pygame

pygame.init()
pygame.mixer.init()
pygame.font.init()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

ASSETS_DIR = resource_path("assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
GENOMES_DIR = os.path.join(LOGS_DIR, "genomes")

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(GENOMES_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "training_history.log"),
    level=logging.INFO,
    format='%(message)s',
    encoding='utf-8'
)

WIDTH, HEIGHT = 800, 400
TARGET_FPS = 60
GROUND_HEIGHT = 50
HORIZON_Y = HEIGHT - GROUND_HEIGHT + 18
AI_MAX_OBS_HEIGHT = 120.0
AI_MAX_SPEED = 16.0

WHITE, BLACK = (255, 255, 255), (0, 0, 0)
GREEN, RED, BLUE = (34, 177, 76), (237, 28, 36), (0, 162, 232)
GREY, LIGHT_GREY = (83, 83, 83), (115, 115, 115)

# Инициализация дисплея до загрузки ассетов (обязательно для convert_alpha)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Game: NEAT Evolution")
clock = pygame.time.Clock()
NIGHT_SURF = pygame.Surface((WIDTH, HEIGHT)).convert()

class AppSettings:
    """Глобальное состояние игры и статистики"""
    def __init__(self):
        self.GEN = 0
        self.TOTAL_ITERATIONS = 0
        self.DATA_PATH = os.path.join(LOGS_DIR, "data.json")
        self.saved_data = self._load_data()
        self.MANUAL_HI_SCORE = self.saved_data.get("manual_hi", 0)
        self.ALL_TIME_HI_SCORE, best_champion_file = self._load_best_score_and_file()
        self.SESSION_HI_SCORE = 0  
        self.PREV_MAX_SCORE = 0
        self.TURBO_MODE = False
        self.SHOW_VISUALS = False
        self.night_mode_factor = 0.0
        self.VOLUME = 0.2
        self.INITIAL_BG_STATE = None 

        if best_champion_file and os.path.exists(best_champion_file):
            best_dest = os.path.join(GENOMES_DIR, "best_genome.pkl")
            if best_dest != best_champion_file:
                with open(best_champion_file, "rb") as src, open(best_dest, "wb") as dst:
                    dst.write(src.read())

    def _load_data(self):
        if os.path.exists(self.DATA_PATH):
            try:
                with open(self.DATA_PATH, "r", encoding="utf-8") as f: return json.load(f)
            except json.JSONDecodeError: pass
        return {"manual_hi": 0}

    def save_manual_hi_score(self, score: float):
        if score > self.MANUAL_HI_SCORE:
            self.MANUAL_HI_SCORE = int(score)
            with open(self.DATA_PATH, "w", encoding="utf-8") as f:
                json.dump({"manual_hi": self.MANUAL_HI_SCORE}, f, indent=4)

    def _load_best_score_and_file(self):
        best_score, best_file = 0, None
        if os.path.exists(GENOMES_DIR):
            for filename in os.listdir(GENOMES_DIR):
                if filename.startswith("champion_") and filename.endswith(".pkl"):
                    try:
                        score = int(filename.replace("champion_", "").replace(".pkl", ""))
                        if score > best_score:
                            best_score, best_file = score, os.path.join(GENOMES_DIR, filename)
                    except ValueError: continue
        return best_score, best_file

app_state = AppSettings()

class AssetManager:
    """Единый менеджер ресурсов (AssetManager). Загружает и кэширует медиафайлы."""
    def __init__(self):
        self.images = {}
        self.masks = {}
        self.sounds = {}
        self.fonts = {}
        self.load_sounds()
        self.load_images()

    def set_volume(self, vol):
        app_state.VOLUME = round(max(0.0, min(1.0, vol)), 1)
        for sound in self.sounds.values():
            if sound: sound.set_volume(app_state.VOLUME)

    def load_sounds(self):
        try:
            self.sounds['jump'] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "press.ogg"))
            self.sounds['hit'] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "hit.ogg"))
            self.sounds['score'] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "reached.ogg"))
            self.set_volume(app_state.VOLUME)
        except Exception as e:
            print(f"[INFO] Звуки не найдены: {e}")
            self.sounds = {'jump': None, 'hit': None, 'score': None}

    def _load_img(self, name, target_size=None, fallback=BLACK):
        full_path = os.path.join(IMAGES_DIR, name)
        if os.path.exists(full_path):
            img = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.smoothscale(img, target_size) if target_size else img
        surf = pygame.Surface(target_size if target_size else (20, 20), pygame.SRCALPHA)
        surf.fill(fallback)
        return surf

    def _load_icon(self, name, size=54):
        img = self._load_img(name)
        if img.get_size() == (20, 20): return img
        bg_color = img.get_at((0, 0))
        if bg_color.r > 200 and bg_color.g > 200 and bg_color.b > 200: img.set_colorkey(bg_color)
        scale = size / max(img.get_width(), img.get_height(), 1)
        new_w, new_h = max(1, int(img.get_width() * scale)), max(1, int(img.get_height() * scale))
        scaled = pygame.transform.smoothscale(img, (new_w, new_h))
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.blit(scaled, ((size - new_w) // 2, (size - new_h) // 2))
        return surf

    def load_images(self):
        self.images['dino_run'] = [self._load_img("Chrome_T-Rex_Left_Run.webp", (55, 60)), self._load_img("Chrome_T-Rex_Right_Run.webp", (55, 60))]
        self.images['dino_duck'] = [self._load_img("Chrome_T-Rex_Left_Duck.png", (75, 40)), self._load_img("Chrome_T-Rex_Right_Duck.png", (75, 40))]
        self.images['dino_stand'] = self._load_img("Chrome_T-Rex_STARTMENU.png", (55, 60))
        self.images['dino_dead'] = self._load_img("Dead_Chrome_T-Rex.webp", (55, 60))
        self.images['cactus'] = [self._load_img("1_Cactus_Chrome_Dino.webp", (25, 55)), self._load_img("3_Cactus_Chrome_Dino.webp", (60, 55))]
        self.images['bird'] = [self._load_img("Chrome_Pterodactyl.png", (45, 35)), self._load_img("Chrome_Pterodactyl2.png", (45, 35))]
        self.images['crater'] = self._load_img("Chrome_Krater.png", (160, 40))
        self.images['crater'].set_colorkey(BLACK)
        self.images['cloud'] = self._load_img("Chromium_T-Rex-cloud.png", (80, 25))
        self.images['ground'] = self._load_img("Chromium_T-Rex-horizon.png", (1200, 24))
        self.images['icon_play'] = self._load_icon("Chromium_T-Rex-play.png")
        self.images['icon_restart'] = self._load_icon("Chromium_T-Rex-restart.png")
        self.images['icon_exit'] = self._load_icon("Chromium_T-Rex-exit.png")
        
        # Инфобар
        ib = self._load_img("DINOGAME_infobar_transparent.png")
        if ib.get_size() != (20, 20):
            new_w = max(1, int(ib.get_width() * (38 / ib.get_height())))
            self.images['infobar'] = pygame.transform.smoothscale(ib, (new_w, 38))
        else:
            self.images['infobar'] = pygame.Surface((340, 38), pygame.SRCALPHA)

        # Камни
        raw_rock = self._load_img("Chrome_Stone.png")
        rock_frames = []
        if raw_rock.get_size() != (20, 20):
            fw, fh = raw_rock.get_width() // 4, raw_rock.get_height() // 3
            for row in range(3):
                for col in range(4):
                    frame = raw_rock.subsurface((col * fw, row * fh, fw, fh))
                    scaled = pygame.transform.scale(frame, (135, 135))
                    scaled.lock()
                    for x in range(scaled.get_width()):
                        for y in range(scaled.get_height()):
                            r, g, b, a = scaled.get_at((x, y))
                            if r < 40 and g < 40 and b < 40: scaled.set_at((x, y), (0, 0, 0, 0))
                    scaled.unlock()
                    rock_frames.append(scaled)
        else: rock_frames = [raw_rock]
        self.images['rock'] = rock_frames

        # Маски коллизий (кэширование)
        self.masks['dino_run'] = [pygame.mask.from_surface(img) for img in self.images['dino_run']]
        self.masks['dino_duck'] = [pygame.mask.from_surface(img) for img in self.images['dino_duck']]
        self.masks['dino_stand'] = pygame.mask.from_surface(self.images['dino_stand'])
        self.masks['cactus'] = [pygame.mask.from_surface(img) for img in self.images['cactus']]
        self.masks['bird'] = [pygame.mask.from_surface(img) for img in self.images['bird']]
        self.masks['rock'] = [pygame.mask.from_surface(img) for img in self.images['rock']]
        self.masks['crater'] = pygame.mask.from_surface(self.images['crater'])

        pygame.display.set_icon(self._load_img("icon.png"))

    @functools.lru_cache(maxsize=10)
    def get_font(self, size):
        font_path = os.path.join(FONTS_DIR, "PressStart2P-Regular.ttf")
        if os.path.exists(font_path): return pygame.font.Font(font_path, size)
        return pygame.font.SysFont(['consolas', 'couriernew', 'monospace'], size, bold=True)

assets = AssetManager()