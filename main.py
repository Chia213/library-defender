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

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

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
        # Draw bookshelves
        for i in range(0, SCREEN_WIDTH, 100):
            pygame.draw.rect(self.screen, BROWN, (i, 0, 80, SCREEN_HEIGHT))
            # Draw books on shelves
            for j in range(0, SCREEN_HEIGHT, 20):
                pygame.draw.rect(self.screen, random.choice([RED, BLUE, GREEN, YELLOW]), 
                               (i + 5, j + 5, 70, 10))
    
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
        # Draw noise meter
        meter_width = 200
        meter_height = 20
        meter_x = SCREEN_WIDTH - meter_width - 10
        meter_y = 10
        
        # Background
        pygame.draw.rect(self.screen, GRAY, (meter_x, meter_y, meter_width, meter_height))
        
        # Noise level
        noise_width = (self.noise_level / self.max_noise) * meter_width
        color = GREEN if self.noise_level < self.max_noise * 0.7 else RED
        pygame.draw.rect(self.screen, color, (meter_x, meter_y, noise_width, meter_height))
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Draw power-up status
        current_time = pygame.time.get_ticks()
        if current_time - self.speed_boost_timer < self.speed_boost_duration:
            font = pygame.font.Font(None, 24)
            speed_text = font.render("COFFEE BOOST!", True, (139, 69, 19))
            self.screen.blit(speed_text, (10, 50))
        
        if current_time - self.mega_book_timer < self.mega_book_duration:
            font = pygame.font.Font(None, 24)
            mega_text = font.render("MEGA BOOK!", True, (255, 165, 0))
            self.screen.blit(mega_text, (10, 80))
        
        # Draw controls
        font = pygame.font.Font(None, 24)
        controls_text = font.render("Click to throw books | Space to shush | R to restart", True, BLACK)
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Final score
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # Restart instruction
        font = pygame.font.Font(None, 36)
        restart_text = font.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
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
        # Draw librarian (simple rectangle with glasses)
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        # Draw glasses
        pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 15), 8, 2)
        pygame.draw.circle(screen, BLACK, (self.x + 30, self.y + 15), 8, 2)
        pygame.draw.line(screen, BLACK, (self.x + 18, self.y + 15), (self.x + 22, self.y + 15), 2)

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
        # Draw monster based on type
        if self.monster_type == "student":
            # Draw student (rectangle with backpack)
            pygame.draw.rect(screen, self.color, (self.x - 10, self.y - 15, 20, 30))
            pygame.draw.rect(screen, (100, 50, 50), (self.x + 8, self.y - 10, 8, 15))  # Backpack
        elif self.monster_type == "animal":
            # Draw animal (circle with ears)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 12)
            pygame.draw.circle(screen, self.color, (int(self.x - 8), int(self.y - 8)), 4)  # Ear
            pygame.draw.circle(screen, self.color, (int(self.x + 8), int(self.y - 8)), 4)  # Ear
        else:  # ghost
            # Draw ghost (wavy bottom)
            points = [
                (self.x - 10, self.y - 10),
                (self.x + 10, self.y - 10),
                (self.x + 8, self.y + 5),
                (self.x + 5, self.y + 10),
                (self.x, self.y + 5),
                (self.x - 5, self.y + 10),
                (self.x - 8, self.y + 5)
            ]
            pygame.draw.polygon(screen, self.color, points)
        
        # Draw eyes for all types
        pygame.draw.circle(screen, BLACK, (int(self.x - 4), int(self.y - 3)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + 4), int(self.y - 3)), 2)

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
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        if self.is_mega:
            # Draw a star on mega books
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            pygame.draw.polygon(screen, WHITE, [
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
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 12)
        if self.type == "coffee":
            # Draw coffee cup
            pygame.draw.rect(screen, WHITE, (self.x - 8, self.y - 5, 16, 10), 2)
            pygame.draw.rect(screen, WHITE, (self.x - 6, self.y - 7, 12, 4), 2)
        else:  # mega_book
            # Draw book
            pygame.draw.rect(screen, WHITE, (self.x - 6, self.y - 8, 12, 16), 2)
            pygame.draw.line(screen, WHITE, (self.x - 2, self.y - 8), (self.x - 2, self.y + 8), 1)
            pygame.draw.line(screen, WHITE, (self.x + 2, self.y - 8), (self.x + 2, self.y + 8), 1)

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
