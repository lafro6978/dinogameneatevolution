import math
import random
import pygame
from config import app_state, assets, WIDTH, HORIZON_Y, AI_MAX_OBS_HEIGHT, AI_MAX_SPEED
from sprites import Dinosaur, Obstacle, Cloud, ParticleSystem, Star, Moon

class DinoGameEnv:
    def __init__(self, num_dinos=1, intro_mode=False, start_hi_blink=False):
        self.dinos = [Dinosaur() for _ in range(num_dinos)]
        self.obstacle_pool = [Obstacle() for _ in range(10)]
        self.clouds = [Cloud() for _ in range(3)]
        
        # Инкапсуляция глобальных объектов среды в класс
        self.particles = ParticleSystem()
        self.stars = [Star() for _ in range(30)]
        self.moon = Moon()
        
        self.score, self.ground_x = 0, 0
        self.game_speed, self.spawn_timer = 7.0, 0
        self.next_spawn_interval = random.randint(60, 110)
        self.death_causes = {"cactus": 0, "bird": 0, "rock": 0}
        self.camera_shift = 0
        
        self.intro_mode = intro_mode
        self.intro_step = 0 if intro_mode else 2
        self.intro_timer, self.intro_duration = 0, 120 
        self.is_blinking, self.blink_timer, self.blink_score_target = False, 0, 0
        self.hi_blinking, self.hi_blink_timer = start_hi_blink, 0
        self.current_speed = 0 if intro_mode else self.game_speed

        if app_state.INITIAL_BG_STATE:
            self.ground_x = app_state.INITIAL_BG_STATE['ground_x']
            for i, mc in enumerate(app_state.INITIAL_BG_STATE['clouds']):
                if i < len(self.clouds):
                    self.clouds[i].rect.x, self.clouds[i].rect.y = mc.rect.x, mc.rect.y
                    self.clouds[i].speed = mc.speed
            self.current_speed = self.game_speed
            for d in self.dinos: d.step_index = app_state.INITIAL_BG_STATE['step_index']
            self.intro_mode, self.intro_step = False, 2
            app_state.INITIAL_BG_STATE = None 

    def get_state(self, index):
        dino = self.dinos[index]
        closest_obs = None
        min_dist = float('inf')
        for obs in self.obstacle_pool:
            if obs.active and not (obs.type == "rock" and obs.has_landed) and obs.rect.right > dino.rect.left:
                dist = obs.rect.left - dino.rect.right
                if dist < min_dist: min_dist, closest_obs = dist, obs

        if closest_obs:
            dist_to_dino = closest_obs.rect.left - dino.rect.right
            obs_height_norm = max(0.0, (HORIZON_Y - closest_obs.rect.bottom) / AI_MAX_OBS_HEIGHT)
            total_speed = self.current_speed + self.camera_shift
            return (
                float(max(0.0, dist_to_dino) / WIDTH), float(obs_height_norm), float(min(1.0, total_speed / AI_MAX_SPEED)),
                float(1.0 if closest_obs.type == "cactus" else 0.0), float(1.0 if closest_obs.type == "bird" else 0.0),
                float(1.0 if closest_obs.type == "rock" else 0.0), float(1.0 if dino.is_jumping else 0.0)
            ), closest_obs
        return (1.0, 0.0, float(min(1.0, self.current_speed / AI_MAX_SPEED)), 0.0, 0.0, 0.0, float(1.0 if dino.is_jumping else 0.0)), None

    def step(self, actions, is_ai_mode=False, dt_scale=1.0):
        if self.hi_blinking:
            self.hi_blink_timer += 1 * dt_scale
            if self.hi_blink_timer > 120: self.hi_blinking = False

        if self.intro_mode:
            if self.intro_step < 2: self.current_speed = 0
            if self.intro_step == 2:
                self.intro_timer += 1 * dt_scale
                self.current_speed = 2.0 + (5.0 * (self.intro_timer / self.intro_duration))
                if self.intro_timer >= self.intro_duration: self.intro_mode = False
        else:
            self.current_speed = min(13.5, self.game_speed + (self.score // 100) * 0.4)
        
        for i, dino in enumerate(self.dinos):
            decision = actions[i]
            dino.last_decision = decision
            if decision == 0:
                dino.end_roll_forward()
                if dino.is_ducking: dino.stand_up()
                dino.jump(play_sound=(len(self.dinos) == 1 and not is_ai_mode))
                if self.intro_mode and self.intro_step == 0: self.intro_step = 1
            elif decision == 1:
                dino.end_roll_forward()
                dino.duck()
            elif decision == 2:
                if dino.is_ducking: dino.stand_up()
                if not dino.is_rolling_forward: dino.roll_forward()
                else: dino.roll_timer = 1 
            else:
                dino.end_roll_forward()
                if dino.is_ducking: dino.stand_up()

        if self.intro_mode and self.intro_step == 1:
            if all(not d.is_jumping for d in self.dinos): self.intro_step = 2

        if not self.intro_mode or self.intro_step == 2:
            if self.current_speed > 0 and not (self.intro_mode and self.intro_timer < 60):
                self.spawn_timer += 1 * dt_scale
                if self.spawn_timer > self.next_spawn_interval:
                    for obs in self.obstacle_pool:
                        if not obs.active:
                            weights = (1.0, 0.0, 0.0) if self.score < 250 else (0.55, 0.45, 0.0) if self.score < 700 else (0.45, 0.35, 0.20)
                            obs.spawn(random.choices(["cactus", "bird", "rock"], weights=weights)[0], self.current_speed)
                            self.spawn_timer = 0
                            min_f = int(max(55, 75 - self.current_speed * 1.5))
                            max_f = int(max(95, 125 - self.current_speed * 1.5))
                            self.next_spawn_interval = random.randint(min_f, max_f)
                            break

        self.camera_shift = 0
        max_return_x = max([d.rect.x for d in self.dinos if not d.is_rolling_forward and d.rect.x > d.default_x] + [55])
        if max_return_x > 55:
            diff = max_return_x - 55
            self.camera_shift = min(max(1, int(diff * 0.05 * dt_scale)), diff)

        total_speed = self.current_speed + self.camera_shift
        is_running = (total_speed > 0)
        
        for dino in self.dinos:
            if not dino.is_rolling_forward and dino.rect.x > dino.default_x:
                dino.rect.x = max(dino.default_x, dino.rect.x - self.camera_shift)
            dino.update(is_running, dt_scale)
            
        for obs in self.obstacle_pool:
            if obs.active: obs.update(total_speed, self.current_speed, self.particles, dt_scale)

        self.particles.update(total_speed, dt_scale)
        for star in self.stars: star.update(self.camera_shift, dt_scale)
        self.moon.update(self.camera_shift, dt_scale)
        
        if not self.intro_mode or self.intro_step == 2:
            for cloud in self.clouds: cloud.update(self.camera_shift, dt_scale)

        ground_width = assets.images['ground'].get_width()
        self.ground_x = (self.ground_x - total_speed * dt_scale) % -ground_width
        
        if self.current_speed > 0:
            old_score = int(self.score)
            self.score += 0.1 * dt_scale
            new_score = int(self.score)
            if new_score > old_score and new_score % 100 == 0 and new_score > 0:
                self.is_blinking, self.blink_timer, self.blink_score_target = True, 0, new_score
                if assets.sounds['score'] and len(self.dinos) == 1 and not is_ai_mode: assets.sounds['score'].play()

        if self.is_blinking:
            self.blink_timer += 1 * dt_scale
            if self.blink_timer > 60: self.is_blinking = False

        dead_indices = []
        for obs in self.obstacle_pool:
            if not obs.active or (obs.type == "rock" and obs.has_landed): continue
            for i, dino in enumerate(self.dinos):
                if dino.is_rolling_forward and obs.type == "rock": continue
                collision = False
                if dino.rect.colliderect(obs.rect):
                    offset_x = obs.rect.x - dino.rect.x
                    offset_y = obs.rect.y - dino.rect.y
                    if dino.mask.overlap(obs.mask, (offset_x, offset_y)): collision = True
                if collision and i not in dead_indices:
                    dead_indices.append(i)
                    self.death_causes[obs.type] += 1
                    
        target_night = 1.0 if (int(self.score) // 700) % 2 == 1 else 0.0
        app_state.night_mode_factor += (target_night - app_state.night_mode_factor) * 0.015 * dt_scale

        prev_night = getattr(self, '_prev_night_factor', 0.0)
        if prev_night < 0.1 and target_night > 0.9: self.moon.phase += 1
        self._prev_night_factor = target_night
        
        return dead_indices