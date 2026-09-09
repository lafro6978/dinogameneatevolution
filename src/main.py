import os
import sys
import time
import pickle
import random
import neat
import pygame
import logging
from config import clock, screen, app_state, assets, resource_path, WIDTH, HEIGHT, TARGET_FPS, WHITE, BLACK, GREY, BLUE, RED, LIGHT_GREY, HORIZON_Y, GROUND_HEIGHT, GENOMES_DIR
from sprites import Cloud
from ai_env import DinoGameEnv
from renderer import GameRenderer

class ReturnToMenu(Exception): pass
class RestartTraining(Exception): pass

class GameManager:
    def __init__(self):
        self.state = "MENU"
        self.config_path = resource_path("config-feedforward.txt")
        self.renderer = GameRenderer()
        self.env = None
        self.ai_net = None

        self.milestones = {"cactus": None, "bird": None, "rock": None}
        
        self.menu_center_x = WIDTH // 2 + 130 
        self.menu_clouds = [Cloud() for _ in range(3)]
        self.ground_x, self.menu_speed, self.step_index = 0, 7.0, 0.0
        self.options = ["1. MANUAL PLAY", "2. AI AUTOPLAY", "3. SETTINGS", "4. EXIT"]
        self.selected_idx = 0
        self.do_intro = True

    def run(self):
        while self.state != "QUIT":
            if self.state == "MENU": self.state_menu()
            elif self.state == "PLAY_MANUAL": self.state_play_unified(force_ai=False)
            elif self.state == "PLAY_AI": self.state_run_neat()
        pygame.quit()
        sys.exit()

    def get_dt_scale(self):
        is_playing = self.state in ["PLAY_AI", "PLAY_MANUAL"]
        fps_limit = 0 if (app_state.TURBO_MODE and is_playing) else TARGET_FPS
        dt = clock.tick(fps_limit)
        return min(dt / (1000.0 / TARGET_FPS) if dt > 0 else 1.0, 3.0)

    # --- UI СОСТОЯНИЯ ---
    def show_settings_screen(self):
        saved_bg = screen.copy()
        vol_down_rect, vol_up_rect = pygame.Rect(WIDTH//2 - 95, HEIGHT//2 - 50, 40, 30), pygame.Rect(WIDTH//2 + 55, HEIGHT//2 - 50, 40, 30)
        back_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT - 60, 120, 40)
        
        while True:
            self.get_dt_scale()
            screen.fill(WHITE)
            self.renderer.draw_text_centered(screen, "SETTINGS", WIDTH//2, 40, 20, BLACK)
            vol_pct = int(app_state.VOLUME * 100)
            
            self.renderer.draw_text_centered(screen, "VOLUME", WIDTH//2, HEIGHT//2 - 70, 12, GREY)
            self.renderer.draw_text_centered(screen, "<", WIDTH//2 - 75, HEIGHT//2 - 35, 16, BLACK)
            self.renderer.draw_text_centered(screen, "OFF" if vol_pct == 0 else f"{vol_pct}%", WIDTH//2, HEIGHT//2 - 35, 16, BLUE if vol_pct > 0 else RED)
            self.renderer.draw_text_centered(screen, ">", WIDTH//2 + 75, HEIGHT//2 - 35, 16, BLACK)
            
            controls = ["W / UP / SPACE - JUMP", "S / DOWN       - DUCK", "D / RIGHT      - ROLL", "A              - TOGGLE AI", "T              - TURBO MODE", "V              - VISUALS", "ESC            - PAUSE"]
            self.renderer.draw_text_centered(screen, "CONTROLS", WIDTH//2, HEIGHT//2, 12, GREY)
            for i, text in enumerate(controls): self.renderer.draw_text(screen, text, WIDTH//2 - 140, HEIGHT//2 + 25 + i*16, 10, GREY)
            
            pygame.draw.rect(screen, LIGHT_GREY, back_rect, border_radius=5)
            self.renderer.draw_text_centered(screen, "BACK", WIDTH//2, HEIGHT - 40, 12, WHITE)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.state = "QUIT"; return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: screen.blit(saved_bg, (0, 0)); return
                    elif event.key in [pygame.K_LEFT, pygame.K_a]: assets.set_volume(app_state.VOLUME - 0.1)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]: assets.set_volume(app_state.VOLUME + 0.1)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos): screen.blit(saved_bg, (0, 0)); return
                    if vol_down_rect.collidepoint(event.pos): assets.set_volume(app_state.VOLUME - 0.1)
                    if vol_up_rect.collidepoint(event.pos): assets.set_volume(app_state.VOLUME + 0.1)

    def show_pause_screen(self):
        y_pos = HEIGHT // 2 + 20
        play_rect = assets.images['icon_play'].get_rect(center=(WIDTH // 2 - 70, y_pos))
        restart_rect = assets.images['icon_restart'].get_rect(center=(WIDTH // 2, y_pos))
        exit_rect = assets.images['icon_exit'].get_rect(center=(WIDTH // 2 + 70, y_pos))
        
        while True:
            self.get_dt_scale()
            self.renderer.draw_text_centered(screen, "P A U S E", WIDTH // 2, HEIGHT // 2 - 50, 24)
            screen.blit(assets.images['icon_play'], play_rect); screen.blit(assets.images['icon_restart'], restart_rect); screen.blit(assets.images['icon_exit'], exit_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.state = "QUIT"; return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_rect.collidepoint(event.pos): return "resume"
                    if restart_rect.collidepoint(event.pos): return "restart"
                    if exit_rect.collidepoint(event.pos): return "menu"
                    w = assets.images['infobar'].get_width()
                    if pygame.Rect(10 + int(w * 0.88), 10, int(w * 0.12), assets.images['infobar'].get_height()).collidepoint(event.pos): self.show_settings_screen()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "resume"

    def show_game_over_screen(self):
        y_pos = HEIGHT // 2 + 20
        restart_rect = assets.images['icon_restart'].get_rect(center=(WIDTH // 2 - 40, y_pos))
        exit_rect = assets.images['icon_exit'].get_rect(center=(WIDTH // 2 + 40, y_pos))

        while True:
            self.get_dt_scale()
            self.renderer.draw_text_centered(screen, "G A M E   O V E R", WIDTH // 2, HEIGHT // 2 - 50, 20)
            screen.blit(assets.images['icon_restart'], restart_rect); screen.blit(assets.images['icon_exit'], exit_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.state = "QUIT"; return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_rect.collidepoint(event.pos): return "restart"
                    if exit_rect.collidepoint(event.pos): return "menu"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return "menu"
                    if event.key in [pygame.K_SPACE, pygame.K_UP]: return "restart"

    def handle_play_events(self, event):
        if event.type == pygame.QUIT: self.state = "QUIT"; return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t: app_state.TURBO_MODE = not app_state.TURBO_MODE
            elif event.key == pygame.K_v: app_state.SHOW_VISUALS = not app_state.SHOW_VISUALS
            elif event.key == pygame.K_ESCAPE: return self.show_pause_screen()
        if event.type == pygame.MOUSEBUTTONDOWN:
            w = assets.images['infobar'].get_width()
            if pygame.Rect(10 + int(w * 0.88), 10, int(w * 0.12), assets.images['infobar'].get_height()).collidepoint(event.pos):
                self.show_settings_screen()
                return self.show_pause_screen()
        return None

    # --- ИГРОВЫЕ СОСТОЯНИЯ ---
    def state_menu(self):
        dt_scale = self.get_dt_scale()
        self.ground_x = (self.ground_x - self.menu_speed * dt_scale) % -assets.images['ground'].get_width()
        for c in self.menu_clouds: c.update(0, dt_scale)
        self.step_index = (self.step_index + 0.2 * dt_scale) % 2
        
        screen.fill(WHITE)
        for c in self.menu_clouds: screen.blit(c.image, c.rect)
        screen.blit(assets.images['ground'], (self.ground_x, HEIGHT - GROUND_HEIGHT))
        screen.blit(assets.images['ground'], (self.ground_x + assets.images['ground'].get_width(), HEIGHT - GROUND_HEIGHT))
        screen.blit(assets.images['dino_run'][int(self.step_index)], assets.images['dino_run'][int(self.step_index)].get_rect(x=55, bottom=HORIZON_Y))
        self.renderer.draw_text_centered(screen, "DINO GAME NEAT EVOLUTION", self.menu_center_x, HEIGHT // 4, 16, BLACK)
        
        option_rects = []
        start_y = HEIGHT // 2 - 20
        for i, opt in enumerate(self.options):
            color = BLACK if i == self.selected_idx else GREY
            text_surf = assets.get_font(12).render(opt, True, color)
            rect = text_surf.get_rect(center=(self.menu_center_x, start_y + i * 30))
            screen.blit(text_surf, rect)
            option_rects.append(rect.inflate(40, 15))
            if i == self.selected_idx:
                cursor_img = pygame.transform.scale(pygame.transform.flip(assets.images['dino_stand'], True, False), (20, 22))
                screen.blit(cursor_img, (rect.left - 35, rect.centery - 11))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.state = "QUIT"; return
            if event.type == pygame.KEYDOWN:
                app_state.night_mode_factor = 0.0 
                if event.key in [pygame.K_UP, pygame.K_w]: self.selected_idx = (self.selected_idx - 1) % len(self.options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]: self.selected_idx = (self.selected_idx + 1) % len(self.options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]: self.execute_menu_choice(event.key)
            if event.type == pygame.MOUSEMOTION:
                for i, r in enumerate(option_rects):
                    if r.collidepoint(event.pos): self.selected_idx = i
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, r in enumerate(option_rects):
                    if r.collidepoint(event.pos): self.execute_menu_choice(idx=i)

    def execute_menu_choice(self, key=None, idx=None):
        choice = idx if idx is not None else self.selected_idx
        
        # Сбрасываем режимы при каждом новом запуске
        app_state.TURBO_MODE = False
        app_state.SHOW_VISUALS = False
        
        if key == pygame.K_1 or choice == 0:
            app_state.INITIAL_BG_STATE = {'ground_x': self.ground_x, 'clouds': self.menu_clouds, 'step_index': self.step_index}
            self.do_intro, self.state = True, "PLAY_MANUAL"
        elif key == pygame.K_2 or choice == 1:
            app_state.INITIAL_BG_STATE = {'ground_x': self.ground_x, 'clouds': self.menu_clouds, 'step_index': self.step_index}
            self.state = "PLAY_AI"
        elif key == pygame.K_3 or choice == 2: 
            self.show_settings_screen()
        elif key == pygame.K_4 or choice == 3: 
            self.state = "QUIT" 

    def state_play_unified(self, force_ai=False):
        random.seed()
        while self.state == "PLAY_MANUAL":
            ai_assistant_active = ai_ever_enabled = force_ai
            
            if os.path.exists(os.path.join(GENOMES_DIR, "best_genome.pkl")):
                config_neat = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)
                with open(os.path.join(GENOMES_DIR, "best_genome.pkl"), "rb") as f: self.ai_net = neat.nn.FeedForwardNetwork.create(pickle.load(f), config_neat)

            self.env = DinoGameEnv(num_dinos=1, intro_mode=self.do_intro, start_hi_blink=force_ai)
            manual_action, iters, restart_requested = 3, 0, False

            while True:
                dt_scale = self.get_dt_scale()
                iters += 1
                
                for event in pygame.event.get():
                    action = self.handle_play_events(event)
                    if action == "quit": return
                    if action == "menu": self.state = "MENU"; return
                    if action == "restart": restart_requested = True; break
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a and not force_ai:
                            if self.ai_net: 
                                ai_assistant_active, ai_ever_enabled, self.env.hi_blinking, self.env.hi_blink_timer = not ai_assistant_active, True, True, 0
                            else: print("[INFO] Модель ИИ не найдена в logs/genomes/!")
                        if not ai_assistant_active:
                            if event.key in [pygame.K_w, pygame.K_UP]: manual_action = 0
                            elif event.key in [pygame.K_s, pygame.K_DOWN]: manual_action = 1
                            elif event.key in [pygame.K_d, pygame.K_RIGHT]: manual_action = 2
                    
                    if event.type == pygame.KEYUP and not ai_assistant_active:
                        if event.key in [pygame.K_s, pygame.K_DOWN] and manual_action == 1: manual_action = 3
                        elif event.key in [pygame.K_d, pygame.K_RIGHT] and manual_action == 2: manual_action = 3

                if restart_requested:
                    self.do_intro = False
                    break

                if ai_assistant_active and self.ai_net:
                    if self.env.intro_mode and self.env.intro_step == 0: action = 0 
                    else:
                        env_state, closest_obs = self.env.get_state(0)
                        if closest_obs:
                            output = self.ai_net.activate(env_state)
                            self.env.dinos[0].last_outputs = output
                            action = output.index(max(output))
                        else: action = 3
                else:
                    action = manual_action
                    if action == 0: manual_action = 3 

                dead_indices = self.env.step([action], is_ai_mode=ai_assistant_active, dt_scale=dt_scale)
                
                curr_visuals = app_state.SHOW_VISUALS if ai_assistant_active else False
                curr_turbo = app_state.TURBO_MODE if ai_assistant_active else False
                current_hi_score = app_state.ALL_TIME_HI_SCORE if ai_assistant_active else app_state.MANUAL_HI_SCORE

                if not curr_turbo or iters % 15 == 0:
                    self.renderer.render_env(screen, self.env, app_state.GEN, curr_visuals, curr_turbo, current_hi_score, best_idx=0, draw_hud=ai_assistant_active, is_ai_assistant=ai_assistant_active)

                if dead_indices:
                    self.env.particles.emit(self.env.dinos[0].rect.centerx, self.env.dinos[0].rect.centery, RED, count=30)
                    if not ai_ever_enabled: app_state.save_manual_hi_score(self.env.score)
                    if ai_assistant_active and self.env.score > app_state.ALL_TIME_HI_SCORE:
                        app_state.ALL_TIME_HI_SCORE = self.env.score
                        app_state._save_data()
                    
                    if assets.sounds['hit'] and not ai_assistant_active: assets.sounds['hit'].play()
                    self.env.dinos[0].image = assets.images['dino_dead']
                    self.renderer.render_env(screen, self.env, app_state.GEN, curr_visuals, curr_turbo, current_hi_score, best_idx=0, draw_hud=ai_assistant_active, is_ai_assistant=ai_assistant_active)
                    
                    action = self.show_game_over_screen()
                    if action == "restart": self.do_intro, restart_requested = False, True; break
                    elif action == "menu": self.state = "MENU"; return
                    elif action == "quit": return

    def state_run_neat(self):
        while self.state == "PLAY_AI":
            app_state.GEN, app_state.night_mode_factor, app_state.SESSION_HI_SCORE = 0, 0.0, 0
            config_neat = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)
            p = neat.Population(config_neat)
            p.add_reporter(neat.StatisticsReporter())
            
            try:
                winner = p.run(self.eval_genomes, 999999999)
                with open(os.path.join(GENOMES_DIR, "best_genome.pkl"), "wb") as f: pickle.dump(winner, f)
                self.state = "MENU"
            except ReturnToMenu: self.state = "MENU"
            except RestartTraining: continue

    def eval_genomes(self, genomes, config):
        app_state.GEN += 1
        nets, ge = [], []
        for _, g in genomes:
            nets.append(neat.nn.FeedForwardNetwork.create(g, config))
            g.fitness = 0; ge.append(g)

        random.seed(app_state.GEN)
        self.env = DinoGameEnv(num_dinos=len(genomes), intro_mode=False, start_hi_blink=True)
        gen_iterations, normal_frames, turbo_real_time, dino_scores = 0, 0, 0.0, []
        
        while self.env.dinos:
            frame_start = time.time()
            dt_scale = self.get_dt_scale()
            gen_iterations += 1
            if not app_state.TURBO_MODE: normal_frames += 1

            for event in pygame.event.get():
                action = self.handle_play_events(event)
                if action == "quit": sys.exit()
                if action == "menu": raise ReturnToMenu()
                if action == "restart": raise RestartTraining()
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_INSERT and self.env.dinos:
                    best_idx = max(range(len(self.env.dinos)), key=lambda i: ge[i].fitness)
                    with open(os.path.join(GENOMES_DIR, "best_genome.pkl"), "wb") as f: pickle.dump(ge[best_idx], f)
                    with open(os.path.join(GENOMES_DIR, f"champion_{int(self.env.score)}.pkl"), "wb") as f: pickle.dump(ge[best_idx], f)
                    print(f"\n[INSERT] Геном сохранен на счете {int(self.env.score)} в папку genomes!")

            actions = []
            for i, net in enumerate(nets):
                env_state, closest_obs = self.env.get_state(i)
                if closest_obs:
                    output = net.activate(env_state)
                    self.env.dinos[i].last_outputs = output
                    actions.append(output.index(max(output)))
                else: actions.append(3)
                ge[i].fitness += 0.1 * (self.env.current_speed / 7.0) * dt_scale

            dead_indices = self.env.step(actions, is_ai_mode=True, dt_scale=dt_scale)
            for idx in sorted(dead_indices, reverse=True):
                dino_scores.append(self.env.score)
                self.env.dinos.pop(idx); nets.pop(idx); ge.pop(idx)

            current_max = int(max(dino_scores)) if dino_scores else int(self.env.score)
            if current_max > app_state.SESSION_HI_SCORE: app_state.SESSION_HI_SCORE = current_max
            
            if not app_state.TURBO_MODE or gen_iterations % 15 == 0:
                best_idx = max(range(len(self.env.dinos)), key=lambda i: ge[i].fitness) if self.env.dinos else None
                self.renderer.render_env(screen, self.env, app_state.GEN, app_state.SHOW_VISUALS, app_state.TURBO_MODE, app_state.SESSION_HI_SCORE, best_idx=best_idx, is_ai_assistant=False)

            if app_state.TURBO_MODE: turbo_real_time += (time.time() - frame_start)

        max_score = int(max(dino_scores)) if dino_scores else 0
        avg_score = int(sum(dino_scores) / len(dino_scores)) if dino_scores else 0
        app_state.TOTAL_ITERATIONS += gen_iterations
        if max_score > app_state.SESSION_HI_SCORE: app_state.SESSION_HI_SCORE = max_score

        if max_score >= 500 and self.milestones["cactus"] is None:
            self.milestones["cactus"] = app_state.GEN
            msg = f"🏆 АНАЛИТИКА: Кактусы полностью освоены за {app_state.GEN} поколений (Счет пробил 500)"
            print(f"\033[93m{msg}\033[0m")
            logging.info(msg)
            
        if max_score >= 750 and self.milestones["bird"] is None:
            self.milestones["bird"] = app_state.GEN
            msg = f"🏆 АНАЛИТИКА: Птицы полностью освоены за {app_state.GEN} поколений (Счет пробил 750)"
            print(f"\033[93m{msg}\033[0m")
            logging.info(msg)
            
        if max_score >= 1500 and self.milestones["rock"] is None:
            self.milestones["rock"] = app_state.GEN
            msg = f"🏆 АНАЛИТИКА: Камни полностью освоены за {app_state.GEN} поколений (Счет пробил 1500)"
            print(f"\033[93m{msg}\033[0m")
            logging.info(msg)

        best_genome_in_gen = max(genomes, key=lambda g: g[1].fitness)[1]
        if max_score > app_state.ALL_TIME_HI_SCORE and max_score > 300:
            app_state.ALL_TIME_HI_SCORE = max_score
            with open(os.path.join(GENOMES_DIR, "best_genome.pkl"), "wb") as f: pickle.dump(best_genome_in_gen, f)
            with open(os.path.join(GENOMES_DIR, f"champion_{int(max_score)}.pkl"), "wb") as f: pickle.dump(best_genome_in_gen, f)

        delta = max_score - app_state.PREV_MAX_SCORE
        delta_str = f"\033[92m▲+{delta:<4d}\033[0m" if delta > 0 else f"\033[91m▼{delta:<5d}\033[0m" if delta < 0 else "▬ 0    "
        normal_sec, total_equiv_sec = normal_frames / TARGET_FPS, gen_iterations / TARGET_FPS
        time_display = f"⏱ [+{turbo_real_time:.1f}s Turbo] (~{total_equiv_sec:.1f}s)" if normal_frames == 0 else f"⏱ {normal_sec:.1f}s [+{turbo_real_time:.1f}s] (~{total_equiv_sec:.1f}s)"
        
        log_msg = f"GEN {app_state.GEN:03d} | Max: {max_score:4d} ({'+' if delta>0 else ''}{delta:>5d}) | Avg: {avg_score:4d} | Steps: {gen_iterations} | Deaths: C={self.env.death_causes['cactus']} B={self.env.death_causes['bird']} R={self.env.death_causes['rock']} | Time: {normal_sec:.1f}s+{turbo_real_time:.1f}s"
        print(f"\033[1;36m⚡ GEN {app_state.GEN:03d}\033[0m │ 🎯 Max: \033[1m{max_score:4d}\033[0m ({delta_str}) │ 📊 Avg: {avg_score:4d} │ 🌵 {self.env.death_causes['cactus']} 🦅 {self.env.death_causes['bird']} ☄️ {self.env.death_causes['rock']} │ {time_display}")
        
        logging.info(log_msg)
        app_state.PREV_MAX_SCORE = max_score
        random.seed()

if __name__ == "__main__":
    game = GameManager()
    game.run()