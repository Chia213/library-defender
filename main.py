import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Dark Academia Color Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (45, 35, 25)      # Dark wood
RICH_BROWN = (101, 67, 33)     # Mahogany
GOLD = (212, 175, 55)          # Brass/gold accents
CREAM = (245, 245, 220)        # Parchment
DARK_GREEN = (34, 139, 34)     # Forest green
BURGUNDY = (128, 0, 32)        # Deep red
NAVY = (0, 0, 128)             # Dark blue
AMBER = (255, 191, 0)          # Warm lighting
DIM_GRAY = (105, 105, 105)     # Shadows
WARM_GRAY = (169, 169, 169)    # Stone

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Library Defender 📚")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.game_over = False
        self.score = 0
        
        # Initialize game objects
        self.player = Librarian()
        self.enemies = []
        self.books = []
        
        # Noise meter
        self.noise_level = 0
        self.max_noise = 100
        
        # Enemy spawn timer
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 2000  # milliseconds
        
        # Book throwing cooldown
        self.book_cooldown = 0
        self.book_cooldown_delay = 300  # milliseconds
        
        # Shush attack cooldown
        self.shush_cooldown = 0
        self.shush_cooldown_delay = 1000  # milliseconds
        self.shush_effect_timer = 0
        self.shush_effect_duration = 500  # milliseconds
        
        # Power-ups
        self.power_ups = []
        self.power_up_spawn_timer = 0
        self.power_up_spawn_delay = 10000  # 10 seconds
        
        # Player power-up effects
        self.speed_boost_timer = 0
        self.speed_boost_duration = 5000  # 5 seconds
        self.mega_book_timer = 0
        self.mega_book_duration = 3000  # 3 seconds
        
        # Particle effects
        self.particles = []
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Shush attack (with cooldown)
                    current_time = pygame.time.get_ticks()
                    if current_time - self.shush_cooldown > self.shush_cooldown_delay:
                        self.shush_attack()
                        self.shush_cooldown = current_time
                        self.shush_effect_timer = current_time
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Throw book towards mouse position (with cooldown)
                    current_time = pygame.time.get_ticks()
                    if current_time - self.book_cooldown > self.book_cooldown_delay:
                        self.throw_book(event.pos)
                        self.book_cooldown = current_time
    
    def update(self):
        if self.game_over:
            return
            
        # Update player
        self.player.update()
        
        # Check power-up effects
        current_time = pygame.time.get_ticks()
        if current_time - self.speed_boost_timer > self.speed_boost_duration:
            self.player.speed = 5  # Reset to normal speed
        
        # Spawn enemies (with increasing difficulty)
        current_time = pygame.time.get_ticks()
        # Decrease spawn delay over time (minimum 500ms)
        difficulty_factor = max(0.5, 1.0 - (current_time / 120000))  # 2 minutes to reach max difficulty
        current_spawn_delay = int(self.enemy_spawn_delay * difficulty_factor)
        
        if current_time - self.enemy_spawn_timer > current_spawn_delay:
            self.spawn_enemy()
            self.enemy_spawn_timer = current_time
        
        # Spawn power-ups
        if current_time - self.power_up_spawn_timer > self.power_up_spawn_delay:
            self.spawn_power_up()
            self.power_up_spawn_timer = current_time
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.x < -50:  # Enemy reached the shelves
                self.noise_level += enemy.noise_value
                self.enemies.remove(enemy)
                if self.noise_level >= self.max_noise:
                    self.game_over = True
        
        # Update books
        for book in self.books[:]:
            book.update()
            # Remove books that go off-screen
            if (book.x > SCREEN_WIDTH or book.x < -book.width or 
                book.y > SCREEN_HEIGHT or book.y < -book.height):
                self.books.remove(book)
        
        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if power_up.x < -50:  # Remove power-ups that go off-screen
                self.power_ups.remove(power_up)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Check collisions
        self.check_collisions()
    
    def spawn_enemy(self):
        enemy = NoisyMonster()
        self.enemies.append(enemy)
    
    def spawn_power_up(self):
        power_up = PowerUp()
        self.power_ups.append(power_up)
    
    def throw_book(self, target_pos):
        # Create a book that moves towards the target position
        current_time = pygame.time.get_ticks()
        is_mega_book = current_time - self.mega_book_timer < self.mega_book_duration
        
        book = Book(self.player.x + self.player.width, 
                   self.player.y + self.player.height // 2, 
                   target_pos, is_mega_book)
        self.books.append(book)
    
    def shush_attack(self):
        # AOE attack - silence all enemies in range
        shush_range = 100
        for enemy in self.enemies[:]:
            distance = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
            if distance <= shush_range:
                self.create_particles(enemy.x, enemy.y, enemy.color)
                self.enemies.remove(enemy)
                self.score += 10
    
    def check_collisions(self):
        # Check book-enemy collisions
        for book in self.books[:]:
            for enemy in self.enemies[:]:
                if (abs(book.x - enemy.x) < 30 and abs(book.y - enemy.y) < 30):
                    if book.is_mega:
                        # Mega book has area damage - remove all nearby enemies
                        for nearby_enemy in self.enemies[:]:
                            distance = math.sqrt((nearby_enemy.x - book.x)**2 + (nearby_enemy.y - book.y)**2)
                            if distance < 80:  # Area of effect
                                self.create_particles(nearby_enemy.x, nearby_enemy.y, nearby_enemy.color)
                                self.enemies.remove(nearby_enemy)
                                self.score += 10
                    else:
                        # Regular book - single target
                        self.create_particles(enemy.x, enemy.y, enemy.color)
                        self.enemies.remove(enemy)
                        self.score += 10
                    self.books.remove(book)
                    break
        
        # Check player-power-up collisions
        for power_up in self.power_ups[:]:
            if (abs(power_up.x - self.player.x) < 40 and 
                abs(power_up.y - self.player.y) < 50):
                self.collect_power_up(power_up)
                self.power_ups.remove(power_up)
    
    def collect_power_up(self, power_up):
        current_time = pygame.time.get_ticks()
        if power_up.type == "coffee":
            self.speed_boost_timer = current_time
            self.player.speed = 8  # Double speed
        elif power_up.type == "mega_book":
            self.mega_book_timer = current_time
    
    def create_particles(self, x, y, color, count=5):
        for _ in range(count):
            particle = Particle(x, y, color)
            self.particles.append(particle)
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw library background
        self.draw_library_background()
        
        # Draw game objects
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for book in self.books:
            book.draw(self.screen)
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw shush effect
        self.draw_shush_effect()
        
        # Draw UI
        self.draw_ui()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_library_background(self):
        # Draw dark academia background
        self.screen.fill(DARK_BROWN)
        
        # Draw ornate ceiling with wooden beams
        for i in range(0, SCREEN_WIDTH, 80):
            pygame.draw.rect(self.screen, RICH_BROWN, (i, 0, 60, 40))
            # Ornate ceiling details
            pygame.draw.line(self.screen, GOLD, (i + 10, 10), (i + 50, 10), 2)
            pygame.draw.line(self.screen, GOLD, (i + 10, 20), (i + 50, 20), 2)
            pygame.draw.line(self.screen, GOLD, (i + 10, 30), (i + 50, 30), 2)
        
        # Draw atmospheric lighting from ceiling
        for i in range(100, SCREEN_WIDTH, 200):
            # Create warm, amber lighting effect
            for radius in range(50, 0, -5):
                alpha = int(50 * (1 - radius/50))
                color = (*AMBER, alpha)
                # Simulate lighting with multiple circles
                pygame.draw.circle(self.screen, AMBER, (i, 40), radius, 1)
        
        # Draw majestic bookshelves with dark wood
        for i in range(0, SCREEN_WIDTH, 120):
            # Main shelf structure - dark mahogany
            pygame.draw.rect(self.screen, DARK_BROWN, (i, 40, 100, SCREEN_HEIGHT - 80))
            
            # Ornate shelf frames with gold trim
            pygame.draw.rect(self.screen, RICH_BROWN, (i + 2, 40, 96, SCREEN_HEIGHT - 80), 3)
            pygame.draw.line(self.screen, GOLD, (i + 5, 45), (i + 95, 45), 2)
            pygame.draw.line(self.screen, GOLD, (i + 5, SCREEN_HEIGHT - 85), (i + 95, SCREEN_HEIGHT - 85), 2)
            
            # Shelf dividers with brass details
            for j in range(60, SCREEN_HEIGHT - 80, 35):
                pygame.draw.line(self.screen, RICH_BROWN, (i + 5, j), (i + 95, j), 2)
                # Brass shelf supports
                pygame.draw.circle(self.screen, GOLD, (i + 10, j), 3)
                pygame.draw.circle(self.screen, GOLD, (i + 90, j), 3)
            
            # Ancient books with rich, scholarly colors
            for j in range(50, SCREEN_HEIGHT - 90, 30):
                for k in range(5):
                    book_x = i + 8 + k * 17
                    book_y = j + 3
                    book_width = 14
                    book_height = 25
                    
                    # Scholarly book colors - leather bound, aged
                    colors = [BURGUNDY, NAVY, DARK_GREEN, (75, 0, 130), (139, 69, 19), 
                             (101, 67, 33), (128, 128, 0), (105, 105, 105)]
                    color = colors[k % len(colors)]
                    
                    pygame.draw.rect(self.screen, color, (book_x, book_y, book_width, book_height))
                    
                    # Book spine details - gold lettering
                    pygame.draw.line(self.screen, BLACK, (book_x, book_y), (book_x, book_y + book_height), 1)
                    pygame.draw.line(self.screen, BLACK, (book_x + book_width, book_y), 
                                   (book_x + book_width, book_y + book_height), 1)
                    # Gold title lines
                    pygame.draw.line(self.screen, GOLD, (book_x + 2, book_y + 8), (book_x + book_width - 2, book_y + 8), 1)
                    pygame.draw.line(self.screen, GOLD, (book_x + 2, book_y + 15), (book_x + book_width - 2, book_y + 15), 1)
        
        # Draw ornate reading tables with brass details
        table_y = SCREEN_HEIGHT - 140
        for table_x in [150, 400, 650]:
            # Table top - dark wood
            pygame.draw.rect(self.screen, RICH_BROWN, (table_x, table_y, 120, 15))
            # Brass trim
            pygame.draw.rect(self.screen, GOLD, (table_x, table_y, 120, 15), 2)
            
            # Ornate table legs
            pygame.draw.rect(self.screen, DARK_BROWN, (table_x + 8, table_y + 15, 12, 40))
            pygame.draw.rect(self.screen, DARK_BROWN, (table_x + 100, table_y + 15, 12, 40))
            # Brass feet
            pygame.draw.circle(self.screen, GOLD, (table_x + 14, table_y + 55), 8)
            pygame.draw.circle(self.screen, GOLD, (table_x + 106, table_y + 55), 8)
            
            # Books and scrolls on tables
            pygame.draw.rect(self.screen, BURGUNDY, (table_x + 10, table_y - 12, 18, 12))
            pygame.draw.rect(self.screen, NAVY, (table_x + 35, table_y - 12, 18, 12))
            pygame.draw.rect(self.screen, DARK_GREEN, (table_x + 60, table_y - 12, 18, 12))
            pygame.draw.rect(self.screen, CREAM, (table_x + 85, table_y - 12, 18, 12))
            
            # Scroll details
            pygame.draw.line(self.screen, GOLD, (table_x + 85, table_y - 8), (table_x + 103, table_y - 8), 1)
            pygame.draw.line(self.screen, GOLD, (table_x + 85, table_y - 5), (table_x + 103, table_y - 5), 1)
        
        # Draw Persian rug in center
        rug_x = SCREEN_WIDTH//2 - 80
        rug_y = SCREEN_HEIGHT - 60
        pygame.draw.rect(self.screen, BURGUNDY, (rug_x, rug_y, 160, 40))
        # Ornate rug pattern
        pygame.draw.rect(self.screen, GOLD, (rug_x + 10, rug_y + 5, 140, 30), 3)
        pygame.draw.rect(self.screen, CREAM, (rug_x + 20, rug_y + 10, 120, 20), 2)
        # Corner details
        pygame.draw.circle(self.screen, GOLD, (rug_x + 20, rug_y + 15), 5)
        pygame.draw.circle(self.screen, GOLD, (rug_x + 140, rug_y + 15), 5)
        pygame.draw.circle(self.screen, GOLD, (rug_x + 20, rug_y + 25), 5)
        pygame.draw.circle(self.screen, GOLD, (rug_x + 140, rug_y + 25), 5)
        
        # Draw atmospheric shadows and depth
        for i in range(0, SCREEN_WIDTH, 120):
            # Shadow under shelves
            shadow_rect = pygame.Rect(i + 2, SCREEN_HEIGHT - 80, 96, 20)
            shadow_surface = pygame.Surface((96, 20))
            shadow_surface.set_alpha(30)
            shadow_surface.fill(BLACK)
            self.screen.blit(shadow_surface, (i + 2, SCREEN_HEIGHT - 80))
    
    def draw_shush_effect(self):
        # Draw shush effect circle if recently used
        current_time = pygame.time.get_ticks()
        if current_time - self.shush_effect_timer < self.shush_effect_duration:
            # Calculate alpha based on time remaining
            time_remaining = self.shush_effect_duration - (current_time - self.shush_effect_timer)
            alpha = int(255 * (time_remaining / self.shush_effect_duration))
            
            # Create a surface for the shush effect
            shush_surface = pygame.Surface((200, 200))
            shush_surface.set_alpha(alpha)
            shush_surface.fill((0, 0, 0, 0))  # Transparent background
            
            # Draw the shush circle
            pygame.draw.circle(shush_surface, (255, 255, 255), (100, 100), 100, 3)
            
            # Blit the effect centered on the player
            effect_x = self.player.x + self.player.width // 2 - 100
            effect_y = self.player.y + self.player.height // 2 - 100
            self.screen.blit(shush_surface, (effect_x, effect_y))
    
    def draw_ui(self):
        # Draw ornate noise meter with dark academia styling
        meter_width = 250
        meter_height = 25
        meter_x = SCREEN_WIDTH - meter_width - 15
        meter_y = 15
        
        # Ornate frame
        pygame.draw.rect(self.screen, RICH_BROWN, (meter_x - 5, meter_y - 5, meter_width + 10, meter_height + 10), 3)
        pygame.draw.rect(self.screen, GOLD, (meter_x - 3, meter_y - 3, meter_width + 6, meter_height + 6), 2)
        
        # Background - dark wood
        pygame.draw.rect(self.screen, DARK_BROWN, (meter_x, meter_y, meter_width, meter_height))
        
        # Noise level with atmospheric colors
        noise_width = (self.noise_level / self.max_noise) * meter_width
        if self.noise_level < self.max_noise * 0.3:
            color = DARK_GREEN  # Peaceful
        elif self.noise_level < self.max_noise * 0.7:
            color = AMBER  # Warning
        else:
            color = BURGUNDY  # Danger
        
        pygame.draw.rect(self.screen, color, (meter_x, meter_y, noise_width, meter_height))
        
        # Ornate label
        font = pygame.font.Font(None, 20)
        label_text = font.render("QUIETUDE METER", True, GOLD)
        self.screen.blit(label_text, (meter_x, meter_y - 20))
        
        # Draw score with scholarly styling
        font = pygame.font.Font(None, 32)
        score_text = font.render(f"Knowledge Gained: {self.score}", True, CREAM)
        # Add shadow
        shadow_text = font.render(f"Knowledge Gained: {self.score}", True, BLACK)
        self.screen.blit(shadow_text, (12, 12))
        self.screen.blit(score_text, (10, 10))
        
        # Draw power-up status with ornate styling
        current_time = pygame.time.get_ticks()
        if current_time - self.speed_boost_timer < self.speed_boost_duration:
            font = pygame.font.Font(None, 24)
            speed_text = font.render("☕ SCHOLAR'S VIGOR!", True, AMBER)
            # Add glow effect
            shadow_text = font.render("☕ SCHOLAR'S VIGOR!", True, BLACK)
            self.screen.blit(shadow_text, (12, 52))
            self.screen.blit(speed_text, (10, 50))
        
        if current_time - self.mega_book_timer < self.mega_book_duration:
            font = pygame.font.Font(None, 24)
            mega_text = font.render("📖 ANCIENT WISDOM!", True, GOLD)
            shadow_text = font.render("📖 ANCIENT WISDOM!", True, BLACK)
            self.screen.blit(shadow_text, (12, 82))
            self.screen.blit(mega_text, (10, 80))
        
        # Draw controls with scholarly elegance
        font = pygame.font.Font(None, 20)
        controls_text = font.render("Click: Cast Tomes | Space: Invoke Silence | R: Begin Anew", True, CREAM)
        shadow_text = font.render("Click: Cast Tomes | Space: Invoke Silence | R: Begin Anew", True, BLACK)
        self.screen.blit(shadow_text, (12, SCREEN_HEIGHT - 28))
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        # Dark academia game over screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(DARK_BROWN)
        self.screen.blit(overlay, (0, 0))
        
        # Ornate border
        pygame.draw.rect(self.screen, GOLD, (50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200), 5)
        pygame.draw.rect(self.screen, RICH_BROWN, (55, 105, SCREEN_WIDTH - 110, SCREEN_HEIGHT - 210), 3)
        
        # Title with scholarly elegance
        font = pygame.font.Font(None, 64)
        game_over_text = font.render("THE LIBRARY FALLS TO CHAOS", True, BURGUNDY)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        # Add shadow
        shadow_text = font.render("THE LIBRARY FALLS TO CHAOS", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 2, SCREEN_HEIGHT//2 - 78))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(game_over_text, text_rect)
        
        # Final score with scholarly styling
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Knowledge Preserved: {self.score}", True, CREAM)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        shadow_text = font.render(f"Knowledge Preserved: {self.score}", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 1, SCREEN_HEIGHT//2 - 19))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(score_text, score_rect)
        
        # Restart instruction with scholarly language
        font = pygame.font.Font(None, 28)
        restart_text = font.render("Press R to Begin Anew", True, GOLD)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        shadow_text = font.render("Press R to Begin Anew", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 1, SCREEN_HEIGHT//2 + 41))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(restart_text, restart_rect)
        
        # Decorative elements
        # Corner ornaments
        pygame.draw.circle(self.screen, GOLD, (70, 120), 8)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 70, 120), 8)
        pygame.draw.circle(self.screen, GOLD, (70, SCREEN_HEIGHT - 120), 8)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 120), 8)
    
    def restart_game(self):
        self.game_over = False
        self.score = 0
        self.noise_level = 0
        self.enemies.clear()
        self.books.clear()
        self.power_ups.clear()
        self.particles.clear()
        self.player = Librarian()
        self.book_cooldown = 0
        self.shush_cooldown = 0
        self.shush_effect_timer = 0
        self.speed_boost_timer = 0
        self.mega_book_timer = 0
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

class Librarian:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.width = 40
        self.height = 60
        self.speed = 5
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def draw(self, screen):
        # Draw scholarly librarian with dark academia aesthetic
        
        # Head - warm skin tone
        pygame.draw.circle(screen, (245, 222, 179), (self.x + 20, self.y + 15), 12)
        
        # Distinguished gray hair with scholarly appearance
        pygame.draw.circle(screen, (169, 169, 169), (self.x + 20, self.y + 8), 10)
        # Hair details
        pygame.draw.line(screen, (192, 192, 192), (self.x + 15, self.y + 6), (self.x + 25, self.y + 6), 2)
        
        # Round spectacles with gold frames
        pygame.draw.circle(screen, GOLD, (self.x + 15, self.y + 15), 7, 2)
        pygame.draw.circle(screen, GOLD, (self.x + 25, self.y + 15), 7, 2)
        pygame.draw.line(screen, GOLD, (self.x + 22, self.y + 15), (self.x + 18, self.y + 15), 2)
        
        # Wise eyes
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 15), 2)
        pygame.draw.circle(screen, BLACK, (self.x + 25, self.y + 15), 2)
        
        # Scholarly tweed jacket with elbow patches
        pygame.draw.rect(screen, RICH_BROWN, (self.x + 6, self.y + 25, 28, 30))
        # Elbow patches
        pygame.draw.circle(screen, DARK_BROWN, (self.x + 8, self.y + 40), 4)
        pygame.draw.circle(screen, DARK_BROWN, (self.x + 32, self.y + 40), 4)
        
        # Arms with shirt cuffs
        pygame.draw.rect(screen, CREAM, (self.x + 3, self.y + 30, 10, 18))
        pygame.draw.rect(screen, CREAM, (self.x + 27, self.y + 30, 10, 18))
        # Cuff details
        pygame.draw.line(screen, GOLD, (self.x + 3, self.y + 35), (self.x + 13, self.y + 35), 1)
        pygame.draw.line(screen, GOLD, (self.x + 27, self.y + 35), (self.x + 37, self.y + 35), 1)
        
        # Trousers - dark academia style
        pygame.draw.rect(screen, NAVY, (self.x + 10, self.y + 50, 10, 15))  # Left leg
        pygame.draw.rect(screen, NAVY, (self.x + 20, self.y + 50, 10, 15))  # Right leg
        
        # Leather shoes
        pygame.draw.ellipse(screen, BLACK, (self.x + 8, self.y + 63, 14, 6))
        pygame.draw.ellipse(screen, BLACK, (self.x + 18, self.y + 63, 14, 6))
        
        # Holding an ancient tome
        pygame.draw.rect(screen, BURGUNDY, (self.x + 35, self.y + 35, 15, 12))
        # Book details - gold binding
        pygame.draw.line(screen, GOLD, (self.x + 35, self.y + 35), (self.x + 35, self.y + 47), 2)
        pygame.draw.line(screen, GOLD, (self.x + 50, self.y + 35), (self.x + 50, self.y + 47), 2)
        # Gold title
        pygame.draw.line(screen, GOLD, (self.x + 37, self.y + 38), (self.x + 48, self.y + 38), 1)
        pygame.draw.line(screen, GOLD, (self.x + 37, self.y + 42), (self.x + 48, self.y + 42), 1)
        
        # Scholarly accessories - pocket watch chain
        pygame.draw.line(screen, GOLD, (self.x + 20, self.y + 30), (self.x + 25, self.y + 35), 1)
        pygame.draw.circle(screen, GOLD, (self.x + 25, self.y + 35), 2)

class NoisyMonster:
    def __init__(self):
        self.x = SCREEN_WIDTH + 50
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.width = 30
        self.height = 30
        self.speed = random.uniform(1, 3)
        self.noise_value = random.randint(5, 15)
        self.monster_type = random.choice(["student", "animal", "ghost"])
        
        # Different colors and properties for different monster types
        if self.monster_type == "student":
            self.color = (255, 200, 200)  # Light pink
            self.noise_value = random.randint(8, 12)
        elif self.monster_type == "animal":
            self.color = (200, 150, 100)  # Brown
            self.noise_value = random.randint(5, 10)
        else:  # ghost
            self.color = (200, 200, 255)  # Light blue
            self.noise_value = random.randint(10, 15)
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        # Draw monster based on type with dark academia styling
        if self.monster_type == "student":
            # Noisy student in modern clothes disrupting the scholarly atmosphere
            # Head
            pygame.draw.circle(screen, (245, 222, 179), (int(self.x), int(self.y - 8)), 8)
            # Messy hair
            pygame.draw.circle(screen, (255, 182, 193), (int(self.x), int(self.y - 12)), 7)
            # Body - casual hoodie
            pygame.draw.rect(screen, (255, 105, 180), (self.x - 8, self.y - 2, 16, 20))
            # Backpack
            pygame.draw.rect(screen, (255, 20, 147), (self.x + 6, self.y - 5, 8, 12))
            # Legs
            pygame.draw.rect(screen, (0, 0, 0), (self.x - 6, self.y + 18, 6, 8))
            pygame.draw.rect(screen, (0, 0, 0), (self.x + 2, self.y + 18, 6, 8))
            # Eyes - mischievous
            pygame.draw.circle(screen, BLACK, (int(self.x - 3), int(self.y - 10)), 2)
            pygame.draw.circle(screen, BLACK, (int(self.x + 3), int(self.y - 10)), 2)
            
        elif self.monster_type == "animal":
            # Mischievous cat disrupting the quiet
            # Head
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)
            # Ears
            pygame.draw.polygon(screen, self.color, [
                (self.x - 8, self.y - 6),
                (self.x - 4, self.y - 12),
                (self.x - 2, self.y - 6)
            ])
            pygame.draw.polygon(screen, self.color, [
                (self.x + 8, self.y - 6),
                (self.x + 4, self.y - 12),
                (self.x + 2, self.y - 6)
            ])
            # Body
            pygame.draw.ellipse(screen, self.color, (self.x - 8, self.y + 2, 16, 12))
            # Tail
            pygame.draw.ellipse(screen, self.color, (self.x + 8, self.y + 4, 8, 4))
            # Eyes - glowing
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x - 3), int(self.y - 2)), 2)
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x + 3), int(self.y - 2)), 2)
            pygame.draw.circle(screen, BLACK, (int(self.x - 3), int(self.y - 2)), 1)
            pygame.draw.circle(screen, BLACK, (int(self.x + 3), int(self.y - 2)), 1)
            
        else:  # ghost
            # Ancient library ghost - more ethereal and scholarly
            # Main body - wavy, translucent
            points = [
                (self.x - 12, self.y - 8),
                (self.x + 12, self.y - 8),
                (self.x + 10, self.y + 2),
                (self.x + 6, self.y + 8),
                (self.x, self.y + 4),
                (self.x - 6, self.y + 8),
                (self.x - 10, self.y + 2)
            ]
            pygame.draw.polygon(screen, self.color, points)
            # Ethereal glow effect
            pygame.draw.polygon(screen, (200, 200, 255), points, 1)
            # Glowing red eyes
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x - 4), int(self.y - 4)), 3)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + 4), int(self.y - 4)), 3)
            # Inner glow
            pygame.draw.circle(screen, (255, 100, 100), (int(self.x - 4), int(self.y - 4)), 1)
            pygame.draw.circle(screen, (255, 100, 100), (int(self.x + 4), int(self.y - 4)), 1)

class Book:
    def __init__(self, x, y, target_pos, is_mega=False):
        self.x = x
        self.y = y
        self.is_mega = is_mega
        self.width = 30 if is_mega else 20
        self.height = 25 if is_mega else 15
        self.speed = 10 if is_mega else 8
        self.color = (255, 165, 0) if is_mega else random.choice([RED, BLUE, GREEN, YELLOW])
        
        # Calculate direction towards target
        dx = target_pos[0] - x
        dy = target_pos[1] - y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx = 0
            self.dy = 0
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
    
    def draw(self, screen):
        # Draw ancient tome with leather binding
        if self.is_mega:
            # Mega book - ancient grimoire
            pygame.draw.rect(screen, (75, 0, 130), (self.x, self.y, self.width, self.height))
            # Gold binding
            pygame.draw.rect(screen, GOLD, (self.x, self.y, self.width, self.height), 2)
            # Mystical star symbol
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            pygame.draw.polygon(screen, GOLD, [
                (center_x, center_y - 8),
                (center_x + 3, center_y - 3),
                (center_x + 8, center_y - 3),
                (center_x + 4, center_y + 1),
                (center_x + 6, center_y + 6),
                (center_x, center_y + 3),
                (center_x - 6, center_y + 6),
                (center_x - 4, center_y + 1),
                (center_x - 8, center_y - 3),
                (center_x - 3, center_y - 3)
            ])
            # Glowing effect
            pygame.draw.polygon(screen, AMBER, [
                (center_x, center_y - 8),
                (center_x + 3, center_y - 3),
                (center_x + 8, center_y - 3),
                (center_x + 4, center_y + 1),
                (center_x + 6, center_y + 6),
                (center_x, center_y + 3),
                (center_x - 6, center_y + 6),
                (center_x - 4, center_y + 1),
                (center_x - 8, center_y - 3),
                (center_x - 3, center_y - 3)
            ], 1)
        else:
            # Regular book - scholarly tome
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            # Leather binding details
            pygame.draw.line(screen, BLACK, (self.x, self.y), (self.x, self.y + self.height), 1)
            pygame.draw.line(screen, BLACK, (self.x + self.width, self.y), (self.x + self.width, self.y + self.height), 1)
            # Gold title lines
            pygame.draw.line(screen, GOLD, (self.x + 2, self.y + 4), (self.x + self.width - 2, self.y + 4), 1)
            pygame.draw.line(screen, GOLD, (self.x + 2, self.y + 8), (self.x + self.width - 2, self.y + 8), 1)
            pygame.draw.line(screen, GOLD, (self.x + 2, self.y + 12), (self.x + self.width - 2, self.y + 12), 1)

class PowerUp:
    def __init__(self):
        self.x = SCREEN_WIDTH + 50
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.width = 25
        self.height = 25
        self.speed = 2
        self.type = random.choice(["coffee", "mega_book"])
        self.color = (139, 69, 19) if self.type == "coffee" else (255, 165, 0)
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        # Draw power-up with dark academia styling
        if self.type == "coffee":
            # Vintage coffee cup with steam
            pygame.draw.circle(screen, (139, 69, 19), (int(self.x), int(self.y)), 12)
            # Cup details
            pygame.draw.arc(screen, GOLD, (self.x - 10, self.y - 8, 20, 16), 0, 3.14, 2)
            # Handle
            pygame.draw.arc(screen, GOLD, (self.x + 6, self.y - 4, 8, 8), 1.57, 3.14, 2)
            # Steam
            pygame.draw.line(screen, CREAM, (self.x - 2, self.y - 12), (self.x - 2, self.y - 18), 1)
            pygame.draw.line(screen, CREAM, (self.x, self.y - 12), (self.x, self.y - 16), 1)
            pygame.draw.line(screen, CREAM, (self.x + 2, self.y - 12), (self.x + 2, self.y - 18), 1)
            # Glow effect
            pygame.draw.circle(screen, AMBER, (int(self.x), int(self.y)), 15, 1)
        else:  # mega_book
            # Ancient tome power-up
            pygame.draw.rect(screen, (75, 0, 130), (self.x - 8, self.y - 10, 16, 20))
            # Gold binding
            pygame.draw.rect(screen, GOLD, (self.x - 8, self.y - 10, 16, 20), 2)
            # Mystical symbols
            pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y - 5)), 3, 1)
            pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y + 5)), 3, 1)
            # Glowing aura
            pygame.draw.circle(screen, AMBER, (int(self.x), int(self.y)), 18, 1)
            pygame.draw.circle(screen, AMBER, (int(self.x), int(self.y)), 20, 1)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 30  # frames
        self.max_life = 30
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.dy += 0.1  # gravity
    
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        size = int(self.size * (self.life / self.max_life))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

if __name__ == "__main__":
    game = Game()
    game.run()
