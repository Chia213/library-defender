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
        
        # Spawn enemies
        current_time = pygame.time.get_ticks()
        if current_time - self.enemy_spawn_timer > self.enemy_spawn_delay:
            self.spawn_enemy()
            self.enemy_spawn_timer = current_time
        
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
        
        # Check collisions
        self.check_collisions()
    
    def spawn_enemy(self):
        enemy = NoisyMonster()
        self.enemies.append(enemy)
    
    def throw_book(self, target_pos):
        # Create a book that moves towards the target position
        book = Book(self.player.x + self.player.width, 
                   self.player.y + self.player.height // 2, 
                   target_pos)
        self.books.append(book)
    
    def shush_attack(self):
        # AOE attack - silence all enemies in range
        shush_range = 100
        for enemy in self.enemies[:]:
            distance = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
            if distance <= shush_range:
                self.enemies.remove(enemy)
                self.score += 10
    
    def check_collisions(self):
        # Check book-enemy collisions
        for book in self.books[:]:
            for enemy in self.enemies[:]:
                if (abs(book.x - enemy.x) < 30 and abs(book.y - enemy.y) < 30):
                    self.books.remove(book)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
    
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
        self.player = Librarian()
        self.book_cooldown = 0
        self.shush_cooldown = 0
        self.shush_effect_timer = 0
    
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
        self.color = random.choice([RED, GREEN, YELLOW, (255, 0, 255)])
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        # Draw monster (simple circle with eyes)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 15)
        # Draw eyes
        pygame.draw.circle(screen, BLACK, (int(self.x - 5), int(self.y - 5)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + 5), int(self.y - 5)), 3)

class Book:
    def __init__(self, x, y, target_pos):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 15
        self.speed = 8
        self.color = random.choice([RED, BLUE, GREEN, YELLOW])
        
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

if __name__ == "__main__":
    game = Game()
    game.run()
