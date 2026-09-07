import random
import pygame
from config import HORIZON_Y, WIDTH, HEIGHT, assets

class Dinosaur:
    def __init__(self):
        self.last_outputs = [0, 0, 0, 0]
        self.image = assets.images['dino_stand']
        self.mask = assets.masks["dino_stand"]
        self.rect = self.image.get_rect()
        
        self.default_x, self.max_x, self.dash_speed = 55, 115, 15
        self.rect.x, self.rect.bottom = self.default_x, HORIZON_Y
        self.y_vel = 0
        
        self.is_jumping, self.is_ducking, self.is_rolling_forward = False, False, False
        self.step_index, self.roll_timer, self.max_roll_frames = 0, 0, 24
        self.last_decision = 3
        self.roll_trail = []

    def jump(self, play_sound=False):
        if not self.is_jumping and not self.is_ducking and not self.is_rolling_forward:
            self.is_jumping, self.y_vel = True, -14
            if play_sound and assets.sounds['jump']: assets.sounds['jump'].play()

    def duck(self):
        if self.is_jumping: self.y_vel += 2.5 
        elif not self.is_rolling_forward: self.is_ducking = True

    def stand_up(self): self.is_ducking = False

    def roll_forward(self):
        if not self.is_jumping and not self.is_ducking and not self.is_rolling_forward:
            self.is_rolling_forward = True

    def end_roll_forward(self):
        if self.is_rolling_forward:
            self.is_rolling_forward, self.roll_timer = False, 0

    def update(self, is_running=True, dt_scale=1.0):
        if self.is_jumping:
            self.rect.y += self.y_vel * dt_scale
            self.y_vel += 0.8 * dt_scale
            if self.rect.bottom >= HORIZON_Y:
                self.rect.bottom, self.is_jumping, self.y_vel = HORIZON_Y, False, 0

        if self.is_rolling_forward:
            self.roll_timer += 1 * dt_scale
            if self.roll_timer >= self.max_roll_frames: self.end_roll_forward()
            elif self.rect.x < self.max_x:
                self.rect.x = min(self.max_x, self.rect.x + (self.dash_speed * dt_scale))
            
            trail_img = assets.images['dino_duck'][int(self.step_index)].copy()
            self.roll_trail.append((trail_img, self.rect.copy()))
            if len(self.roll_trail) > 4: self.roll_trail.pop(0)
        else:
            self.roll_trail.clear()

        if is_running or self.is_jumping or self.is_rolling_forward:
            self.step_index = (self.step_index + 0.2 * dt_scale) % 2 
        else: self.step_index = 0

        idx = int(self.step_index)
        if self.is_ducking or self.is_rolling_forward: 
            self.image, self.mask = assets.images['dino_duck'][idx], assets.masks["dino_duck"][idx]
        elif self.is_jumping: 
            self.image, self.mask = assets.images['dino_run'][0], assets.masks["dino_run"][0]
        else: 
            if is_running: self.image, self.mask = assets.images['dino_run'][idx], assets.masks["dino_run"][idx]
            else: self.image, self.mask = assets.images['dino_stand'], assets.masks["dino_stand"]

        old_bottom, old_x = self.rect.bottom, self.rect.x
        self.rect = self.image.get_rect(x=old_x)
        self.rect.bottom = old_bottom if self.is_jumping else HORIZON_Y


class Obstacle:
    def __init__(self):
        self.active, self.has_landed = False, False
        self.y_vel, self.float_y, self.anim_index = 0, 0.0, 0.0
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def spawn(self, obs_type, current_speed=7.0):
        self.type, self.active, self.has_landed = obs_type, True, False
        self.step_index, self.y_vel = 0, 0
        self.anim_index = random.uniform(0, len(assets.images['rock']))
        
        if self.type == "cactus":
            idx = random.randint(0, len(assets.images['cactus']) - 1)
            self.image, self.mask = assets.images['cactus'][idx], assets.masks["cactus"][idx]
            self.rect = self.image.get_rect(bottom=HORIZON_Y, x=WIDTH)
        elif self.type == "bird":
            self.image, self.mask = assets.images['bird'][0], assets.masks["bird"][0]
            y_offset = {"low": 15, "mid": 40, "high": 120}[random.choice(["low", "mid", "high"])]
            self.rect = self.image.get_rect(bottom=HORIZON_Y - y_offset, x=WIDTH)
        elif self.type == "rock":
            self.image, self.mask = assets.images['rock'][0], assets.masks["rock"][0]
            self.rect = self.image.get_rect(bottom=-30, x=WIDTH)
            self.float_y = float(self.rect.y)
            time_to_impact = (WIDTH - 55) / current_speed
            self.y_vel = (HORIZON_Y - self.rect.bottom) / time_to_impact if time_to_impact > 0 else 4.5

    def update(self, speed, base_speed, particles_sys, dt_scale=1.0):
        if not self.active: return
        self.rect.x -= speed * dt_scale
        
        if self.type == "bird":
            self.step_index = (self.step_index + 0.1 * dt_scale) % 2
            idx = int(self.step_index)
            self.image, self.mask = assets.images['bird'][idx], assets.masks["bird"][idx]
        elif self.type == "rock" and not self.has_landed:
            self.anim_index = (self.anim_index + 0.25 * dt_scale) % len(assets.images['rock'])
            idx = int(self.anim_index)
            self.image, self.mask = assets.images['rock'][idx], assets.masks["rock"][idx]
            
            if self.rect.bottom < HORIZON_Y:
                self.float_y += self.y_vel * dt_scale * (speed / base_speed if base_speed > 0 else 1.0)
                self.rect.y = int(self.float_y)
            if self.rect.bottom >= HORIZON_Y:
                self.has_landed, self.y_vel = True, 0
                self.image, self.mask = assets.images['crater'], assets.masks["crater"]
                self.rect = self.image.get_rect(centerx=self.rect.centerx, bottom=HORIZON_Y + 28)
                particles_sys.emit(self.rect.centerx, HORIZON_Y, (83, 83, 83), count=20)
                
        if self.rect.x < -200: self.active = False


class Cloud:
    def __init__(self):
        self.image = assets.images['cloud']
        self.rect = self.image.get_rect(x=WIDTH + random.randint(0, 300), y=random.randint(20, 100))
        self.speed = random.uniform(1.0, 2.0)
        
    def update(self, camera_shift, dt_scale=1.0):
        self.rect.x -= (self.speed + camera_shift) * dt_scale
        if self.rect.x < -100: self.rect.x, self.rect.y = WIDTH + random.randint(0, 300), random.randint(20, 100)


class ParticleSystem:
    def __init__(self): self.particles = []
        
    def emit(self, x: int, y: int, color: tuple, count: int = 15):
        for _ in range(count):
            self.particles.append({
                'x': float(x), 'y': float(y), 
                'vx': random.uniform(-4, 4), 'vy': random.uniform(-6, -1), 
                'timer': random.randint(20, 40), 'color': color, 'size': random.randint(2, 4)
            })
            
    def update(self, camera_shift: float, dt_scale: float = 1.0):
        for p in self.particles[:]:
            p['x'] += (p['vx'] - camera_shift) * dt_scale
            p['y'] += p['vy'] * dt_scale
            p['vy'] += 0.4 * dt_scale
            p['timer'] -= 1 * dt_scale
            if p['timer'] <= 0: self.particles.remove(p)


class Star:
    def __init__(self):
        self.x, self.y = random.randint(0, WIDTH), random.randint(10, HEIGHT // 2 - 30)
        self.speed = 0.3
        
    def update(self, camera_shift, dt_scale=1.0):
        self.x -= (self.speed + camera_shift * 0.1) * dt_scale
        if self.x < 0: self.x, self.y = WIDTH + random.randint(0, 50), random.randint(10, HEIGHT // 2 - 30)


class Moon:
    def __init__(self): self.x, self.y, self.phase = WIDTH + 100, 40, 0
        
    def update(self, camera_shift, dt_scale=1.0):
        self.x -= (0.2 + camera_shift * 0.05) * dt_scale
        if self.x < -40: self.x = WIDTH + random.randint(150, 300)