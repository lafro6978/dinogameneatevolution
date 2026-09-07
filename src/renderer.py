import math
import pygame
from config import WIDTH, HEIGHT, WHITE, GREEN, RED, BLUE, BLACK, GREY, LIGHT_GREY, GROUND_HEIGHT, NIGHT_SURF, app_state, assets

class GameRenderer:
    """MVC View: Класс, инкапсулирующий всю логику отрисовки на экран."""
    
    @staticmethod
    def draw_text(surface, text, x, y, size, color=GREY):
        font = assets.get_font(size)
        text_surf = font.render(str(text), True, color)
        surface.blit(text_surf, (x, y))

    @staticmethod
    def draw_text_centered(surface, text, cx, cy, size, color=GREY):
        font = assets.get_font(size)
        text_surf = font.render(str(text), True, color)
        surface.blit(text_surf, text_surf.get_rect(center=(cx, cy)))

    @staticmethod
    def draw_hud(surface, gen, speed, alive, visual_on, turbo_on, is_ai_assistant=False):
        x, y = 10, 10
        img = assets.images['infobar']
        surface.blit(img, (x, y))
        w, h = img.get_size()
        box_cy = y + int(h * 0.65)
        font_s = 7
        
        if is_ai_assistant: GameRenderer.draw_text_centered(surface, "TOP", x + int(w * 0.185) + 3, box_cy, font_s)
        else: GameRenderer.draw_text_centered(surface, f"{gen:03d}", x + int(w * 0.185) + 3, box_cy, font_s)
            
        GameRenderer.draw_text_centered(surface, f"{int(speed):02d}", x + int(w * 0.338) - 6, box_cy, font_s)
        GameRenderer.draw_text_centered(surface, f"{alive:02d}", x + int(w * 0.485) - 8, box_cy, font_s)
        GameRenderer.draw_text_centered(surface, "ON" if visual_on else "OFF", x + int(w * 0.676) - 24, box_cy, font_s)
        GameRenderer.draw_text_centered(surface, "ON" if turbo_on else "OFF", x + int(w * 0.829) - 24, box_cy, font_s)

    def render_env(self, surface, env, gen, show_visuals, turbo_mode, hi_score, best_idx=None, custom_msg=None, draw_hud=True, is_ai_assistant=False):
        surface.fill(WHITE)
        for cloud in env.clouds: surface.blit(cloud.image, cloud.rect)
        
        # Декорации ночи
        if app_state.night_mode_factor > 0.2:
            for star in env.stars:
                surface.set_at((int(star.x), int(star.y)), BLACK)
                surface.set_at((int(star.x) + 1, int(star.y)), BLACK)
            
            moon_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            moon_surf.fill((255, 255, 255, 0))
            pygame.draw.circle(moon_surf, BLACK, (12, 12), 10)
            pygame.draw.circle(moon_surf, WHITE, ([7, 10, 12, 14, 17][env.moon.phase % 5], 12), 9)
            surface.blit(moon_surf, (int(env.moon.x), env.moon.y))

        # Земля
        ground = assets.images['ground']
        surface.blit(ground, (env.ground_x, HEIGHT - GROUND_HEIGHT))
        surface.blit(ground, (env.ground_x + ground.get_width(), HEIGHT - GROUND_HEIGHT))
        
        # Препятствия
        for obs in env.obstacle_pool:
            if obs.active: surface.blit(obs.image, obs.rect)
        
        # Занавес (интро)
        if env.intro_mode:
            if env.intro_step < 2: pygame.draw.rect(surface, WHITE, (175, 0, WIDTH - 175, HEIGHT))
            else:
                reveal_width = int(175 + (WIDTH - 175) * ((env.intro_timer / env.intro_duration) ** 2)) 
                if reveal_width < WIDTH: pygame.draw.rect(surface, WHITE, (reveal_width, 0, WIDTH - reveal_width, HEIGHT))

        # Динозавры и их хвост рывка
        for dino in env.dinos:
            for i, (img, rct) in enumerate(dino.roll_trail):
                fade_img = img.copy()
                fade_img.set_alpha(int((i + 1) / len(dino.roll_trail) * 90))
                surface.blit(fade_img, rct)
            surface.blit(dino.image, dino.rect)
            
        # Частицы
        for p in env.particles.particles:
            alpha = max(0, min(255, int((p['timer'] / 40) * 255)))
            surf = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
            surf.fill((*p['color'][:3], alpha))
            surface.blit(surf, (int(p['x']), int(p['y'])))

        # AI Телеметрия
        if show_visuals and env.dinos and best_idx is not None and best_idx < len(env.dinos):
            lead_dino = env.dinos[best_idx]
            _, closest_obs = env.get_state(best_idx)
            
            if closest_obs:
                color = GREEN if (closest_obs.rect.left - lead_dino.rect.right) > 150 else RED
                pygame.draw.line(surface, color, lead_dino.rect.center, closest_obs.rect.center, 2)
                for comp in lead_dino.mask.connected_components():
                    for point in comp.outline(): pygame.draw.circle(surface, BLUE, (lead_dino.rect.x + point[0], lead_dino.rect.y + point[1]), 1)
                for comp in closest_obs.mask.connected_components():
                    for point in comp.outline(): pygame.draw.circle(surface, color, (closest_obs.rect.x + point[0], closest_obs.rect.y + point[1]), 1)
            
            raw_outs = lead_dino.last_outputs
            exp_vals = [math.exp(min(max(v, -10), 10)) for v in raw_outs]
            total_exp = sum(exp_vals) if sum(exp_vals) > 0 else 1.0
            percents = [int((ev / total_exp) * 100) for ev in exp_vals]
            action_names = ["JMP", "DCK", "ROL", "RUN"]
            best_act = percents.index(max(percents))
            obs_name = closest_obs.type[:4].upper() if closest_obs else "NONE"
            dist_val = int(closest_obs.rect.left - lead_dino.rect.right) if closest_obs else 0
            
            info_surf = pygame.Surface((115, 86), pygame.SRCALPHA)
            info_surf.fill((255, 255, 255, 230)) 
            pygame.draw.rect(info_surf, BLUE, info_surf.get_rect(), 1)
            
            self.draw_text(info_surf, "AI TELEMETRY", 6, 4, 7, BLACK)
            self.draw_text(info_surf, f"OBS:{obs_name}", 6, 14, 7, GREY)
            self.draw_text(info_surf, f"DST:{dist_val}px", 6, 24, 7, GREY)
            for idx in range(4): self.draw_text(info_surf, f"{action_names[idx]}: {percents[idx]}%", 6, 40 + idx * 11, 7, BLUE if idx == best_act else GREY)
            surface.blit(info_surf, (lead_dino.rect.right + 15, lead_dino.rect.top - 45))

        # Переход день/ночь
        if app_state.night_mode_factor > 0.01:
            NIGHT_SURF.fill(WHITE)
            NIGHT_SURF.blit(surface, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            NIGHT_SURF.set_alpha(int(app_state.night_mode_factor * 255))
            surface.blit(NIGHT_SURF, (0, 0))

        if draw_hud: self.draw_hud(surface, gen, env.current_speed, len(env.dinos), show_visuals, turbo_mode, is_ai_assistant)
        if custom_msg: self.draw_text(surface, custom_msg[0], 10, 60, 16, custom_msg[1])

        # Счёт
        score_x, hi_score_x = WIDTH - 100, WIDTH - 260
        if hi_score > 0:
            if not env.hi_blinking or (env.hi_blink_timer // 15) % 2 == 0:
                self.draw_text(surface, f"HI {str(int(hi_score)).zfill(5)}", hi_score_x, 15, 14, LIGHT_GREY)
        if not env.is_blinking or (env.blink_timer // 15) % 2 == 0:
            self.draw_text(surface, str(int(env.blink_score_target if env.is_blinking else env.score)).zfill(5), score_x, 15, 14, GREY)
            
        pygame.display.flip()