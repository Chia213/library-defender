import pygame
import sys
import random
import math
import json
import os
import numpy as np
from pathlib import Path

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Difficulty Levels
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_EXPERT = 3

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

# Additional colors for books
RED = (220, 20, 60)            # Crimson red books
BLUE = (70, 130, 180)          # Steel blue books  
GREEN = (46, 125, 50)          # Forest green books
YELLOW = (255, 193, 7)         # Golden yellow books

# Game States
MENU = 0
CHARACTER_SELECT = 1
DIFFICULTY_SELECT = 2
PLAYING = 3
GAME_OVER = 4
SETTINGS = 5
STORY_MODE = 6
CHAPTER_SELECT = 7
CUTSCENE = 8

# Maze/Library Layout Constants
TILE_SIZE = 40
MAZE_WIDTH = SCREEN_WIDTH // TILE_SIZE
MAZE_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Tile Types
EMPTY = 0
WALL = 1
BOOKSHELF = 2
READING_DESK = 3
LAMP = 4
CARPET = 5
ENTRANCE = 6

# Story Mode Constants
STORY_CHAPTERS = {
    1: {
        "title": "The Silence Invasion",
        "description": "Strange creatures have invaded the main reading hall!",
        "map_type": "main_hall",
        "objective": "Defend the library for 3 minutes",
        "unlocked": True
    },
    2: {
        "title": "The Fiction Rebellion", 
        "description": "Characters are escaping from the fiction section!",
        "map_type": "fiction_maze",
        "objective": "Collect 5 different genres while defending",
        "unlocked": False
    },
    3: {
        "title": "The Reference Rampage",
        "description": "The reference section is under siege!",
        "map_type": "reference_fortress",
        "objective": "Protect the ancient encyclopedias",
        "unlocked": False
    },
    4: {
        "title": "The Poetry Pandemonium",
        "description": "Chaos has consumed the poetry corner!",
        "map_type": "poetry_garden",
        "objective": "Defeat enemies using only poetry books",
        "unlocked": False
    },
    5: {
        "title": "The Final Chapter",
        "description": "Face the Lord of Ignorance in the Grand Archive!",
        "map_type": "grand_archive",
        "objective": "Defeat the ultimate boss enemy",
        "unlocked": False
    }
}

class LibraryMaze:
    def __init__(self, map_type="default"):
        self.width = MAZE_WIDTH
        self.height = MAZE_HEIGHT
        self.map_type = map_type
        self.tiles = [[EMPTY for _ in range(self.width)] for _ in range(self.height)]
        self.generate_map_layout()
    
    def generate_map_layout(self):
        """Generate different map layouts based on story chapter"""
        if self.map_type == "main_hall":
            self.generate_main_hall()
        elif self.map_type == "fiction_maze":
            self.generate_fiction_maze()
        elif self.map_type == "reference_fortress":
            self.generate_reference_fortress()
        elif self.map_type == "poetry_garden":
            self.generate_poetry_garden()
        elif self.map_type == "grand_archive":
            self.generate_grand_archive()
        else:
            self.generate_default_library()
        
    def generate_default_library(self):
        """Generate the original library layout"""
        # Fill with carpet base
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = CARPET
        
        # Create outer walls
        for x in range(self.width):
            self.tiles[0][x] = WALL
            self.tiles[self.height-1][x] = WALL
        for y in range(self.height):
            self.tiles[y][0] = WALL
            self.tiles[y][self.width-1] = WALL
        
        # Create bookshelf rows (library aisles)
        for row in range(2, self.height-2, 3):  # Every 3 rows
            for x in range(2, self.width-2):
                if x % 4 != 0:  # Leave gaps for aisles
                    self.tiles[row][x] = BOOKSHELF
                    if row + 1 < self.height - 2:
                        self.tiles[row + 1][x] = BOOKSHELF
        
        # Add reading areas
        reading_spots = [
            (3, 3), (self.width-4, 3), 
            (3, self.height-4), (self.width-4, self.height-4),
            (self.width//2, self.height//2)
        ]
        
        for x, y in reading_spots:
            if 0 < x < self.width-1 and 0 < y < self.height-1:
                # Clear area around reading spot
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if 0 < x+dx < self.width-1 and 0 < y+dy < self.height-1:
                            self.tiles[y+dy][x+dx] = CARPET
                
                # Place reading desk
                self.tiles[y][x] = READING_DESK
                # Place lamp nearby
                if x + 1 < self.width - 1:
                    self.tiles[y][x + 1] = LAMP
        
        # Create main entrance area
        entrance_x = self.width // 2
        for y in range(1, 4):
            for x in range(entrance_x - 2, entrance_x + 3):
                if 0 < x < self.width - 1:
                    self.tiles[y][x] = ENTRANCE
    
    def generate_main_hall(self):
        """Chapter 1: Large open reading hall with scattered furniture"""
        # Fill with carpet
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = CARPET
        
        # Outer walls
        for x in range(self.width):
            self.tiles[0][x] = WALL
            self.tiles[self.height-1][x] = WALL
        for y in range(self.height):
            self.tiles[y][0] = WALL
            self.tiles[y][self.width-1] = WALL
        
        # Central reading area with scattered desks
        center_x, center_y = self.width // 2, self.height // 2
        for i in range(8):  # 8 reading stations
            angle = (i * 2 * 3.14159) / 8
            desk_x = int(center_x + 4 * math.cos(angle))
            desk_y = int(center_y + 3 * math.sin(angle))
            if 1 < desk_x < self.width-1 and 1 < desk_y < self.height-1:
                self.tiles[desk_y][desk_x] = READING_DESK
                # Add lamps around desks
                if desk_x + 1 < self.width-1:
                    self.tiles[desk_y][desk_x + 1] = LAMP
        
        # Perimeter bookshelves
        for x in range(2, self.width-2):
            if x % 3 == 0:
                self.tiles[2][x] = BOOKSHELF
                self.tiles[self.height-3][x] = BOOKSHELF
        for y in range(2, self.height-2):
            if y % 3 == 0:
                self.tiles[y][2] = BOOKSHELF
                self.tiles[y][self.width-3] = BOOKSHELF
    
    def generate_fiction_maze(self):
        """Chapter 2: Complex maze of fiction bookshelves"""
        # Fill with carpet
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = CARPET
        
        # Outer walls
        for x in range(self.width):
            self.tiles[0][x] = WALL
            self.tiles[self.height-1][x] = WALL
        for y in range(self.height):
            self.tiles[y][0] = WALL
            self.tiles[y][self.width-1] = WALL
        
        # Create simple maze-like layout
        for y in range(2, self.height-2, 2):
            for x in range(2, self.width-2, 2):
                self.tiles[y][x] = BOOKSHELF
                # Create some connecting walls
                if random.random() > 0.4:
                    if x + 1 < self.width-2:
                        self.tiles[y][x + 1] = BOOKSHELF
                if random.random() > 0.4:
                    if y + 1 < self.height-2:
                        self.tiles[y + 1][x] = BOOKSHELF
        
        # Ensure player spawn area is clear
        center_x, center_y = self.width // 2, self.height // 2
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if 0 < center_x + dx < self.width and 0 < center_y + dy < self.height:
                    self.tiles[center_y + dy][center_x + dx] = ENTRANCE
    
    def generate_reference_fortress(self):
        """Chapter 3: Fortress-like reference section"""
        # Fill with carpet
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = CARPET
        
        # Outer walls
        for x in range(self.width):
            self.tiles[0][x] = WALL
            self.tiles[self.height-1][x] = WALL
        for y in range(self.height):
            self.tiles[y][0] = WALL
            self.tiles[y][self.width-1] = WALL
        
        # Create fortress-like defensive positions
        mid_x, mid_y = self.width // 2, self.height // 2
        
        # Inner defensive walls
        for x in range(mid_x - 3, mid_x + 4):
            if 2 < x < self.width - 2:
                self.tiles[mid_y - 2][x] = BOOKSHELF
                self.tiles[mid_y + 2][x] = BOOKSHELF
        for y in range(mid_y - 2, mid_y + 3):
            if 2 < y < self.height - 2:
                self.tiles[y][mid_x - 3] = BOOKSHELF
                self.tiles[y][mid_x + 3] = BOOKSHELF
        
        # Central entrance
        self.tiles[mid_y][mid_x] = ENTRANCE
    
    def generate_poetry_garden(self):
        """Chapter 4: Organic poetry section"""
        # Fill with carpet
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = CARPET
        
        # Outer walls
        for x in range(self.width):
            self.tiles[0][x] = WALL
            self.tiles[self.height-1][x] = WALL
        for y in range(self.height):
            self.tiles[y][0] = WALL
            self.tiles[y][self.width-1] = WALL
        
        # Create organic curved patterns
        center_x, center_y = self.width // 2, self.height // 2
        
        # Spiral bookshelf pattern
        for radius in range(2, 6, 2):
            for angle_deg in range(0, 360, 20):
                angle = math.radians(angle_deg)
                x = int(center_x + radius * math.cos(angle))
                y = int(center_y + radius * 0.7 * math.sin(angle))
                if 2 < x < self.width-2 and 2 < y < self.height-2:
                    self.tiles[y][x] = BOOKSHELF
        
        # Central poetry circle
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if 0 < center_x + dx < self.width and 0 < center_y + dy < self.height:
                    self.tiles[center_y + dy][center_x + dx] = ENTRANCE
    
    def generate_grand_archive(self):
        """Chapter 5: Epic final battle arena"""
        # Fill with entrance (marble floor)
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = ENTRANCE
        
        # Outer walls
        for x in range(self.width):
            self.tiles[0][x] = WALL
            self.tiles[self.height-1][x] = WALL
        for y in range(self.height):
            self.tiles[y][0] = WALL
            self.tiles[y][self.width-1] = WALL
        
        # Grand columns
        columns = [(4, 4), (self.width-5, 4), (4, self.height-5), (self.width-5, self.height-5)]
        
        for x, y in columns:
            if 1 < x < self.width-1 and 1 < y < self.height-1:
                # Create 2x2 pillar
                for dy in range(2):
                    for dx in range(2):
                        if 0 < x + dx < self.width and 0 < y + dy < self.height:
                            self.tiles[y + dy][x + dx] = BOOKSHELF
        
        # Central battle area - keep clear
        center_x, center_y = self.width // 2, self.height // 2
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if 0 < center_x + dx < self.width and 0 < center_y + dy < self.height:
                    self.tiles[center_y + dy][center_x + dx] = ENTRANCE
    
    def is_walkable(self, x, y):
        """Check if a position is walkable"""
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return False
            
        tile_type = self.tiles[tile_y][tile_x]
        return tile_type in [EMPTY, CARPET, ENTRANCE]
    
    def get_tile_at(self, x, y):
        """Get tile type at pixel coordinates"""
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return WALL
            
        return self.tiles[tile_y][tile_x]

class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.sprite_path = Path("sprites")
        self.sprite_path.mkdir(exist_ok=True)
        self.current_character = "female"  # Default character
        self.load_sprites()
    
    def load_sprites(self):
        """Load all sprite images from the sprites directory"""
        try:
            # Define the sprites we're looking for (both male and female)
            sprite_files = {
                # Female librarian sprites
                'female_librarian_down': 'female_librarian_down.png',
                'female_librarian_up': 'female_librarian_up.png', 
                'female_librarian_left': 'female_librarian_left.png',
                'female_librarian_right': 'female_librarian_right.png',
                'female_librarian_idle': 'female_librarian_idle.png',
                # Male librarian sprites
                'male_librarian_down': 'male_librarian_down.png',
                'male_librarian_up': 'male_librarian_up.png', 
                'male_librarian_left': 'male_librarian_left.png',
                'male_librarian_right': 'male_librarian_right.png',
                'male_librarian_idle': 'male_librarian_idle.png'
            }
            
            for sprite_name, filename in sprite_files.items():
                sprite_file = self.sprite_path / filename
                if sprite_file.exists():
                    try:
                        image = pygame.image.load(str(sprite_file)).convert_alpha()
                        # Scale to appropriate size for our game
                        scaled_image = pygame.transform.scale(image, (30, 35))
                        self.sprites[sprite_name] = scaled_image
                        print(f"Loaded sprite: {sprite_name}")
                    except pygame.error as e:
                        print(f"Could not load {filename}: {e}")
                        self.sprites[sprite_name] = None
                else:
                    print(f"Sprite file not found: {filename}")
                    self.sprites[sprite_name] = None
            
            # Check if we have any sprites loaded
            if not any(self.sprites.values()):
                print("No sprite images found, creating sample sprites...")
                self.create_sample_sprites()
                
        except Exception as e:
            print(f"Error loading sprites: {e}")
    
    def get_sprite(self, sprite_name):
        """Get a sprite by name, returns None if not found"""
        return self.sprites.get(sprite_name)
    
    def get_current_character_sprite(self, direction):
        """Get sprite for current character and direction"""
        sprite_name = f"{self.current_character}_librarian_{direction}"
        return self.get_sprite(sprite_name)
    
    def set_character(self, character_type):
        """Set the current character type (male or female)"""
        if character_type in ["male", "female"]:
            self.current_character = character_type
            print(f"Character set to: {character_type}")
    
    def has_sprites(self):
        """Check if any sprites are loaded"""
        return any(self.sprites.values())
    
    def create_sample_sprites(self):
        """Create sample sprite files for testing"""
        print("Creating sample sprite files for both male and female librarians...")
        
        # Create both male and female librarian sprites
        sprite_data = {
            # Female librarian (smaller, longer hair, different colors)
            'female_librarian_down': {'hair_color': (139, 69, 19), 'robe_color': (75, 0, 130), 'skin_color': (255, 228, 196)},
            'female_librarian_up': {'hair_color': (139, 69, 19), 'robe_color': (75, 0, 130), 'skin_color': (255, 228, 196)},
            'female_librarian_left': {'hair_color': (139, 69, 19), 'robe_color': (75, 0, 130), 'skin_color': (255, 228, 196)},
            'female_librarian_right': {'hair_color': (139, 69, 19), 'robe_color': (75, 0, 130), 'skin_color': (255, 228, 196)},
            'female_librarian_idle': {'hair_color': (139, 69, 19), 'robe_color': (75, 0, 130), 'skin_color': (255, 228, 196)},
            # Male librarian (broader, shorter hair, different colors)
            'male_librarian_down': {'hair_color': (101, 67, 33), 'robe_color': (45, 35, 25), 'skin_color': (240, 220, 190)},
            'male_librarian_up': {'hair_color': (101, 67, 33), 'robe_color': (45, 35, 25), 'skin_color': (240, 220, 190)},
            'male_librarian_left': {'hair_color': (101, 67, 33), 'robe_color': (45, 35, 25), 'skin_color': (240, 220, 190)},
            'male_librarian_right': {'hair_color': (101, 67, 33), 'robe_color': (45, 35, 25), 'skin_color': (240, 220, 190)},
            'male_librarian_idle': {'hair_color': (101, 67, 33), 'robe_color': (45, 35, 25), 'skin_color': (240, 220, 190)}
        }
        
        for sprite_name, colors in sprite_data.items():
            surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            is_male = sprite_name.startswith('male')
            
            # Draw character based on gender
            if is_male:
                # Male librarian - broader, more angular
                # Head (slightly larger)
                pygame.draw.circle(surface, colors['skin_color'], (16, 10), 8)
                
                # Hair (shorter, more angular)
                pygame.draw.ellipse(surface, colors['hair_color'], (10, 4, 12, 8))
                
                # Body/Robe (broader shoulders)
                pygame.draw.ellipse(surface, colors['robe_color'], (9, 16, 14, 14))
                
                # Facial hair (small beard)
                pygame.draw.ellipse(surface, colors['hair_color'], (14, 14, 4, 2))
                
            else:
                # Female librarian - softer, more curved
                # Head
                pygame.draw.circle(surface, colors['skin_color'], (16, 10), 7)
                
                # Hair (longer, flowing)
                pygame.draw.ellipse(surface, colors['hair_color'], (11, 5, 10, 10))
                pygame.draw.ellipse(surface, colors['hair_color'], (12, 8, 8, 6))  # Side hair
                
                # Body/Robe (more fitted)
                pygame.draw.ellipse(surface, colors['robe_color'], (10, 16, 12, 14))
            
            # Common features for both genders
            # Glasses
            pygame.draw.circle(surface, (212, 175, 55), (13, 10), 3, 1)
            pygame.draw.circle(surface, (212, 175, 55), (19, 10), 3, 1)
            pygame.draw.line(surface, (212, 175, 55), (15, 10), (17, 10), 1)
            
            # Eyes
            pygame.draw.circle(surface, (0, 0, 0), (13, 10), 1)
            pygame.draw.circle(surface, (0, 0, 0), (19, 10), 1)
            
            # Book (different position for male/female)
            if '_up' not in sprite_name:  # Don't show book when facing up
                if '_right' in sprite_name:
                    book_x = 22 if is_male else 21
                else:
                    book_x = 6 if is_male else 7
                pygame.draw.rect(surface, (128, 0, 32), (book_x, 18, 6, 4))
                pygame.draw.line(surface, (212, 175, 55), (book_x, 19), (book_x + 6, 19), 1)
            
            # Save the sprite
            filename = self.sprite_path / f"{sprite_name}.png"
            pygame.image.save(surface, str(filename))
            print(f"Created sample sprite: {filename}")
        
        # Reload sprites after creating samples
        self.load_sprites()

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.generate_sounds()
    
    def generate_tone(self, frequency, duration, volume=0.5, fade_out=0.1):
        """Generate a tone using numpy"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        # Generate sine wave
        for i in range(frames):
            wave = volume * np.sin(2 * np.pi * frequency * i / sample_rate)
            # Add some harmonics for richer sound
            wave += volume * 0.3 * np.sin(4 * np.pi * frequency * i / sample_rate)
            wave += volume * 0.1 * np.sin(6 * np.pi * frequency * i / sample_rate)
            
            # Fade out
            if fade_out > 0 and i > frames * (1 - fade_out):
                fade_factor = 1 - (i - frames * (1 - fade_out)) / (frames * fade_out)
                wave *= fade_factor
            
            arr[i] = [wave, wave]
        
        # Convert to pygame sound
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def generate_noise(self, duration, volume=0.3):
        """Generate white noise"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.random.uniform(-volume, volume, (frames, 2))
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_sounds(self):
        """Generate all game sounds"""
        try:
            # Book throwing sounds - multiple variations
            self.sounds['book_throw'] = self.generate_whoosh(200, 0.15)
            self.sounds['book_throw_2'] = self.generate_whoosh(180, 0.12)
            self.sounds['book_throw_3'] = self.generate_whoosh(220, 0.18)
            
            # Shush sound variations
            self.sounds['shush'] = self.generate_shush_sound()
            self.sounds['shush_whisper'] = self.generate_whisper_sound()
            
            # Enemy defeat sounds by type
            self.sounds['enemy_defeat'] = self.generate_tone(523, 0.2, 0.4, 0.5)  # C5
            self.sounds['student_defeat'] = self.generate_tone(440, 0.15, 0.3, 0.6)  # A4
            self.sounds['animal_defeat'] = self.generate_meow_sound()
            self.sounds['ghost_defeat'] = self.generate_ethereal_sound()
            self.sounds['chaos_lord_defeat'] = self.generate_boss_defeat_sound()
            self.sounds['literary_villain_defeat'] = self.generate_tone(330, 0.25, 0.4, 0.6)  # Dark academic defeat
            
            # Power-up sounds
            self.sounds['power_up'] = self.generate_power_up_chord()
            self.sounds['coffee_pickup'] = self.generate_coffee_sound()
            self.sounds['book_pickup'] = self.generate_page_flip_sound()
            self.sounds['aura_pickup'] = self.generate_mystical_sound()
            self.sounds['freeze_pickup'] = self.generate_clock_sound()
            
            # Ambient and UI sounds
            self.sounds['game_over'] = self.generate_dramatic_chord()
            self.sounds['menu_select'] = self.generate_tone(440, 0.1, 0.3, 0.5)
            self.sounds['noise_warning'] = self.generate_rumble()
            self.sounds['new_high_score'] = self.generate_victory_fanfare()
            self.sounds['player_hit'] = self.generate_tone(200, 0.3, 0.5, 0.7)  # Low hurt sound
            
            # Background ambience
            self.sounds['library_ambience'] = self.generate_library_ambience()
            self.sounds['page_turn'] = self.generate_page_turn_sound()
            self.sounds['footsteps'] = self.generate_footstep_sound()
            
        except Exception as e:
            print(f"Could not generate sounds: {e}")
            # Create silent sounds as fallback
            silent = pygame.mixer.Sound(buffer=np.zeros((1, 2), dtype=np.int16))
            for key in ['book_throw', 'shush', 'enemy_defeat', 'power_up', 'game_over', 'menu_select', 'noise_warning']:
                self.sounds[key] = silent
    
    def generate_whoosh(self, base_freq, duration):
        """Generate a whoosh sound for book throwing"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            # Frequency sweep from high to low
            freq = base_freq + (100 * (1 - i/frames))
            # Volume envelope that fades
            volume = 0.3 * (1 - i/frames) * np.sin(np.pi * i/frames)
            
            wave = volume * np.sin(2 * np.pi * freq * i / sample_rate)
            # Add some noise for texture
            noise = 0.1 * volume * np.random.uniform(-1, 1)
            arr[i] = [wave + noise, wave + noise]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_shush_sound(self):
        """Generate a realistic shush sound"""
        duration = 0.4
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            # High frequency noise filtered
            noise = np.random.uniform(-1, 1)
            # Apply high-pass filter effect
            filtered_noise = noise * (0.7 + 0.3 * np.sin(20 * np.pi * i / sample_rate))
            
            # Volume envelope
            volume = 0.4 * np.exp(-3 * i / frames)
            arr[i] = [filtered_noise * volume, filtered_noise * volume]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_whisper_sound(self):
        """Generate a soft whisper sound"""
        return self.generate_noise(0.2, 0.15)
    
    def generate_meow_sound(self):
        """Generate a cat meow sound"""
        duration = 0.3
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            # Two-tone meow: starts high, goes low
            if i < frames // 2:
                freq = 800 + 200 * np.sin(10 * np.pi * i / frames)
            else:
                freq = 400 + 100 * np.sin(5 * np.pi * i / frames)
            
            volume = 0.3 * np.sin(np.pi * i / frames)
            wave = volume * np.sin(2 * np.pi * freq * i / sample_rate)
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_ethereal_sound(self):
        """Generate an ethereal ghost sound"""
        duration = 0.4
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            # Multiple overlapping sine waves for ethereal effect
            freq1 = 220 + 50 * np.sin(3 * np.pi * i / frames)
            freq2 = 440 + 30 * np.sin(5 * np.pi * i / frames)
            freq3 = 880 + 20 * np.sin(7 * np.pi * i / frames)
            
            volume = 0.2 * (1 - i / frames)
            wave = volume * (np.sin(2 * np.pi * freq1 * i / sample_rate) +
                           0.5 * np.sin(2 * np.pi * freq2 * i / sample_rate) +
                           0.25 * np.sin(2 * np.pi * freq3 * i / sample_rate))
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_boss_defeat_sound(self):
        """Generate a dramatic boss defeat sound"""
        duration = 0.8
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        # Dramatic chord progression
        chord_freqs = [130.81, 164.81, 196.00, 261.63]  # C3, E3, G3, C4
        
        for i in range(frames):
            volume = 0.4 * (1 - (i / frames)**2)  # Quadratic fade
            wave = 0
            for freq in chord_freqs:
                wave += (1/len(chord_freqs)) * np.sin(2 * np.pi * freq * i / sample_rate)
            
            wave *= volume
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_power_up_chord(self):
        """Generate an ascending power-up chord"""
        duration = 0.5
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        # C major arpeggio
        notes = [261.63, 329.63, 392.00, 523.25]  # C, E, G, C
        note_duration = frames // len(notes)
        
        for note_idx, freq in enumerate(notes):
            start_frame = note_idx * note_duration
            end_frame = min(start_frame + note_duration + note_duration//2, frames)
            
            for i in range(start_frame, end_frame):
                local_i = i - start_frame
                local_duration = end_frame - start_frame
                volume = 0.3 * np.sin(np.pi * local_i / local_duration)
                wave = volume * np.sin(2 * np.pi * freq * i / sample_rate)
                arr[i] += [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_coffee_sound(self):
        """Generate a coffee percolating sound"""
        return self.generate_tone(150, 0.2, 0.2, 0.8)
    
    def generate_page_flip_sound(self):
        """Generate a page turning sound"""
        return self.generate_noise(0.1, 0.2)
    
    def generate_mystical_sound(self):
        """Generate a mystical aura sound"""
        return self.generate_tone(432, 0.4, 0.3, 0.7)  # A4 tuned to 432Hz
    
    def generate_clock_sound(self):
        """Generate a clock ticking sound"""
        duration = 0.3
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        # Sharp tick sound
        for i in range(min(frames, 1000)):  # Very short duration
            volume = 0.4 * np.exp(-5 * i / 1000)
            wave = volume * np.sin(2 * np.pi * 1000 * i / sample_rate)
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_dramatic_chord(self):
        """Generate a dramatic game over chord"""
        return self.generate_tone(196, 1.2, 0.4, 0.8)  # G3, longer duration
    
    def generate_rumble(self):
        """Generate a low rumble for noise warning"""
        duration = 0.6
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            # Low frequency rumble with slight variation
            freq = 40 + 20 * np.sin(2 * np.pi * i / frames)
            volume = 0.3 * np.sin(np.pi * i / frames)
            wave = volume * np.sin(2 * np.pi * freq * i / sample_rate)
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(arr)
    
    def generate_victory_fanfare(self):
        """Generate a victory fanfare for high scores"""
        return self.generate_power_up_chord()  # Reuse the chord for now
    
    def generate_library_ambience(self):
        """Generate subtle library ambience"""
        return self.generate_noise(2.0, 0.05)  # Very quiet, long duration
    
    def generate_page_turn_sound(self):
        """Generate a realistic page turn sound"""
        return self.generate_noise(0.15, 0.1)
    
    def generate_footstep_sound(self):
        """Generate a soft footstep sound"""
        return self.generate_tone(80, 0.1, 0.2, 0.9)
    
    def play(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_random_variant(self, base_name, variants=3):
        """Play a random variant of a sound"""
        if variants > 1:
            variant = random.randint(1, variants)
            if variant == 1:
                self.play(base_name)
            else:
                self.play(f"{base_name}_{variant}")
        else:
            self.play(base_name)

class HighScoreManager:
    def __init__(self):
        self.high_scores_file = "high_scores.json"
        self.high_scores = self.load_high_scores()
    
    def load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists(self.high_scores_file):
                with open(self.high_scores_file, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open(self.high_scores_file, 'w') as f:
                json.dump(self.high_scores, f, indent=2)
        except:
            pass
    
    def add_score(self, score):
        """Add a new score and return if it's a high score"""
        self.high_scores.append(score)
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:10]  # Keep top 10
        self.save_high_scores()
        return score in self.high_scores[:3]  # Return True if top 3
    
    def get_high_scores(self):
        """Get the high scores list"""
        return self.high_scores

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Library Defender 📚")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = MENU
        self.score = 0
        self.is_new_high_score = False
        self.selected_character = "female"  # Default character choice
        self.selected_difficulty = DIFFICULTY_NORMAL  # Default difficulty
        self.menu_selection = 0  # Current menu selection
        
        # Managers
        self.sound_manager = SoundManager()
        self.high_score_manager = HighScoreManager()
        self.library_maze = LibraryMaze()
        self.sprite_manager = SpriteManager()
        
        # Key bindings (customizable)
        self.key_bindings = {
            'move_up': pygame.K_UP,
            'move_down': pygame.K_DOWN,
            'move_left': pygame.K_LEFT,
            'move_right': pygame.K_RIGHT,
            'shoot': pygame.K_x,  # X key for shooting
            'shush': pygame.K_SPACE,  # Space for shush attack
            'restart': pygame.K_r
        }
        
        # Shooting direction (for keyboard shooting)
        self.last_move_direction = {'x': 1, 'y': 0}  # Default: shoot right
        
        # Initialize game objects (will be properly set in reset_game)
        self.player = None
        self.enemies = []
        self.books = []
        
        # Literary features
        self.collected_books = set()  # Track unique books found
        self.discovered_authors = set()  # Track authors encountered
        self.current_quote = ""
        self.quote_timer = 0
        self.quote_author = ""
        self.reading_level = 1  # Bibliophile progression
        
        # Story Mode
        self.story_progress = {1: True, 2: False, 3: False, 4: False, 5: False}  # Chapter unlocks
        self.current_chapter = 1
        self.chapter_objective = ""
        self.chapter_progress = 0
        self.chapter_timer = 0
        self.is_story_mode = False
        
        # Noise meter
        self.noise_level = 0
        self.max_noise = 100
        
        # Enemy spawn timer
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1500  # milliseconds (will be adjusted by difficulty)
        
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
        self.silence_aura_timer = 0
        self.silence_aura_duration = 8000  # 8 seconds
        self.time_freeze_timer = 0
        self.time_freeze_duration = 4000  # 4 seconds
        
        # New power-up effects
        self.shield_timer = 0
        self.shield_duration = 5000  # 5 seconds
        self.multi_shot_timer = 0
        self.multi_shot_duration = 4000  # 4 seconds
        self.magnet_timer = 0
        self.magnet_duration = 6000  # 6 seconds
        self.freeze_time_timer = 0
        self.freeze_time_duration = 3000  # 3 seconds
        
        # Particle effects
        self.particles = []
        
        # Settings mode
        self.setting_key = None  # Which key is being rebound
        
        # Initialize game objects
        self.reset_game()
    
    def reset_game(self):
        """Reset game to initial state"""
        # Create appropriate map for story mode
        if self.is_story_mode and self.current_chapter in STORY_CHAPTERS:
            chapter_data = STORY_CHAPTERS[self.current_chapter]
            self.library_maze = LibraryMaze(chapter_data["map_type"])
            self.chapter_objective = chapter_data["objective"]
            self.chapter_progress = 0
            self.chapter_timer = pygame.time.get_ticks()
        else:
            self.library_maze = LibraryMaze("default")
        
        self.player = Librarian(self.library_maze, self.sprite_manager)
        self.enemies = []
        self.books = []
        self.power_ups = []
        self.particles = []
        
        # Reset timers
        self.noise_level = 0
        self.enemy_spawn_timer = 0
        self.power_up_spawn_timer = 0
        self.book_cooldown = 0
        self.shush_cooldown = 0
        self.shush_effect_timer = 0
        self.wave_number = 1  # Start with wave 1
        self.speed_boost_timer = 0
        self.mega_book_timer = 0
        self.silence_aura_timer = 0
        self.time_freeze_timer = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    self.handle_menu_events(event)
                elif self.state == CHARACTER_SELECT:
                    self.handle_character_select_events(event)
                elif self.state == PLAYING:
                    self.handle_playing_events(event)
                elif self.state == GAME_OVER:
                    self.handle_game_over_events(event)
                elif self.state == SETTINGS:
                    self.handle_settings_events(event)
                elif self.state == CHAPTER_SELECT:
                    self.handle_chapter_select_events(event)
                elif self.state == DIFFICULTY_SELECT:
                    self.handle_difficulty_select_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == PLAYING:
                    self.handle_playing_mouse(event)
                elif self.state == MENU:
                    self.handle_menu_mouse(event)
                elif self.state == CHARACTER_SELECT:
                    self.handle_character_select_mouse(event)
                elif self.state == CHAPTER_SELECT:
                    self.handle_chapter_select_mouse(event)
                elif self.state == DIFFICULTY_SELECT:
                    self.handle_difficulty_select_mouse(event)
    
    def handle_menu_events(self, event):
        # Arrow key navigation
        if event.key == pygame.K_UP:
            self.menu_selection = (self.menu_selection - 1) % 4
            self.sound_manager.play('menu_select')
        elif event.key == pygame.K_DOWN:
            self.menu_selection = (self.menu_selection + 1) % 4
            self.sound_manager.play('menu_select')
        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self.sound_manager.play('menu_select')
            if self.menu_selection == 0:  # Endless Mode
                self.state = CHARACTER_SELECT
                self.is_story_mode = False
            elif self.menu_selection == 1:  # Story Mode
                self.state = CHAPTER_SELECT
                self.is_story_mode = True
            elif self.menu_selection == 2:  # Difficulty Selection
                self.state = DIFFICULTY_SELECT
            elif self.menu_selection == 3:  # Settings
                self.state = SETTINGS
        # Legacy key bindings for direct access
        elif event.key == pygame.K_s:  # S for Story Mode
            self.sound_manager.play('menu_select')
            self.state = CHAPTER_SELECT
            self.is_story_mode = True
        elif event.key == pygame.K_d:  # D for Difficulty Selection
            self.sound_manager.play('menu_select')
            self.state = DIFFICULTY_SELECT
        elif event.key == pygame.K_ESCAPE:
            self.sound_manager.play('menu_select')
            self.state = SETTINGS
    
    def handle_menu_mouse(self, event):
        if event.button == 1:  # Left click
            # Calculate which menu option was clicked
            mouse_y = event.pos[1]
            start_y = 250
            option_height = 80
            
            for i in range(4):
                option_y = start_y + i * option_height
                if option_y - 10 <= mouse_y <= option_y + 50:
                    self.menu_selection = i
                    self.sound_manager.play('menu_select')
                    
                    if i == 0:  # Endless Mode
                        self.state = CHARACTER_SELECT
                        self.is_story_mode = False
                    elif i == 1:  # Story Mode
                        self.state = CHAPTER_SELECT
                        self.is_story_mode = True
                    elif i == 2:  # Difficulty Selection
                        self.state = DIFFICULTY_SELECT
                    elif i == 3:  # Settings
                        self.state = SETTINGS
                    break
    
    def handle_character_select_events(self, event):
        if event.key == pygame.K_1:
            self.selected_character = "female"
            self.sprite_manager.set_character("female")
            self.sound_manager.play('menu_select')
        elif event.key == pygame.K_2:
            self.selected_character = "male"
            self.sprite_manager.set_character("male")
            self.sound_manager.play('menu_select')
        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self.sound_manager.play('menu_select')
            self.state = PLAYING
            self.reset_game()
        elif event.key == pygame.K_ESCAPE:
            self.sound_manager.play('menu_select')
            self.state = MENU
    
    def handle_character_select_mouse(self, event):
        if event.button == 1:  # Left click
            mouse_x, mouse_y = event.pos
            
            # Female character button (left side)
            if 150 <= mouse_x <= 350 and 300 <= mouse_y <= 400:
                self.selected_character = "female"
                self.sprite_manager.set_character("female")
                self.sound_manager.play('menu_select')
            # Male character button (right side)
            elif 450 <= mouse_x <= 650 and 300 <= mouse_y <= 400:
                self.selected_character = "male"
                self.sprite_manager.set_character("male")
                self.sound_manager.play('menu_select')
            # Start game button
            elif 300 <= mouse_x <= 500 and 500 <= mouse_y <= 550:
                self.sound_manager.play('menu_select')
                self.state = PLAYING
                self.reset_game()
    
    def handle_chapter_select_events(self, event):
        if event.key == pygame.K_ESCAPE:
            self.sound_manager.play('menu_select')
            self.state = MENU
        elif event.key >= pygame.K_1 and event.key <= pygame.K_5:
            chapter = event.key - pygame.K_0
            if chapter in STORY_CHAPTERS and self.story_progress.get(chapter, False):
                self.sound_manager.play('menu_select')
                self.current_chapter = chapter
                self.state = CHARACTER_SELECT
    
    def handle_chapter_select_mouse(self, event):
        if event.button == 1:  # Left click
            mouse_x, mouse_y = event.pos
            
            # Chapter buttons (5 chapters, vertically arranged)
            for i in range(1, 6):
                chapter_y = 150 + (i-1) * 80
                if 100 <= mouse_x <= 700 and chapter_y <= mouse_y <= chapter_y + 60:
                    if self.story_progress.get(i, False):
                        self.sound_manager.play('menu_select')
                        self.current_chapter = i
                        self.state = CHARACTER_SELECT
                        break
            
            # Back button
            if 50 <= mouse_x <= 150 and 500 <= mouse_y <= 540:
                self.sound_manager.play('menu_select')
                self.state = MENU
    
    def handle_difficulty_select_events(self, event):
        if event.key == pygame.K_ESCAPE:
            self.sound_manager.play('menu_select')
            self.state = MENU
        elif event.key == pygame.K_1:
            self.selected_difficulty = DIFFICULTY_EASY
            self.sound_manager.play('menu_select')
        elif event.key == pygame.K_2:
            self.selected_difficulty = DIFFICULTY_NORMAL
            self.sound_manager.play('menu_select')
        elif event.key == pygame.K_3:
            self.selected_difficulty = DIFFICULTY_HARD
            self.sound_manager.play('menu_select')
        elif event.key == pygame.K_4:
            self.selected_difficulty = DIFFICULTY_EXPERT
            self.sound_manager.play('menu_select')
        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            self.sound_manager.play('menu_select')
            self.state = MENU
    
    def handle_difficulty_select_mouse(self, event):
        if event.button == 1:  # Left click
            mouse_x, mouse_y = event.pos
            
            # Difficulty buttons (4 difficulties, vertically arranged)
            for i in range(4):
                difficulty_y = 200 + i * 100
                if 400 <= mouse_x <= 800 and difficulty_y <= mouse_y <= difficulty_y + 60:
                    self.selected_difficulty = i
                    self.sound_manager.play('menu_select')
                    break
            
            # Back button
            if 50 <= mouse_x <= 150 and 600 <= mouse_y <= 640:
                self.sound_manager.play('menu_select')
                self.state = MENU
    
    def handle_playing_events(self, event):
        if event.key == self.key_bindings['shush']:
            # Shush attack (with cooldown)
            current_time = pygame.time.get_ticks()
            if current_time - self.shush_cooldown > self.shush_cooldown_delay:
                self.shush_attack()
                self.shush_cooldown = current_time
                self.shush_effect_timer = current_time
                self.sound_manager.play('shush')
        elif event.key == self.key_bindings['shoot']:
            # Keyboard shooting (with cooldown)
            current_time = pygame.time.get_ticks()
            if current_time - self.book_cooldown > self.book_cooldown_delay:
                self.throw_book_keyboard()
                self.book_cooldown = current_time
                self.sound_manager.play_random_variant('book_throw', 3)
        elif event.key == pygame.K_ESCAPE:
            # Go to settings
            self.state = SETTINGS
            self.setting_key = None
    
    def handle_playing_mouse(self, event):
        if event.button == 1:  # Left mouse button
            # Throw book towards mouse position (with cooldown)
            current_time = pygame.time.get_ticks()
            if current_time - self.book_cooldown > self.book_cooldown_delay:
                self.throw_book_mouse(event.pos)
                self.book_cooldown = current_time
                self.sound_manager.play_random_variant('book_throw', 3)
    
    def handle_game_over_events(self, event):
        if event.key == self.key_bindings['restart']:
            # Restart game
            self.state = PLAYING
            self.reset_game()
        elif event.key == pygame.K_ESCAPE:
            # Back to menu
            self.state = MENU
    
    def handle_settings_events(self, event):
        if event.key == pygame.K_ESCAPE:
            # Return to previous state
            if hasattr(self, 'previous_state'):
                self.state = self.previous_state
            else:
                self.state = MENU
            self.setting_key = None
        elif event.key == pygame.K_1:
            self.setting_key = 'shoot'
        elif event.key == pygame.K_2:
            self.setting_key = 'shush'
        elif event.key == pygame.K_3:
            self.setting_key = 'move_up'
        elif event.key == pygame.K_4:
            self.setting_key = 'move_down'
        elif event.key == pygame.K_5:
            self.setting_key = 'move_left'
        elif event.key == pygame.K_6:
            self.setting_key = 'move_right'
        elif self.setting_key:
            # Assign new key
            self.key_bindings[self.setting_key] = event.key
            self.setting_key = None
            self.sound_manager.play('menu_select')
    
    def update(self):
        if self.state != PLAYING or not self.player:
            return
            
        # Update player and track movement direction for keyboard shooting
        keys = pygame.key.get_pressed()
        old_x, old_y = self.player.x, self.player.y
        self.player.update(self.key_bindings)
        
        # Track last movement direction for keyboard shooting
        if self.player.x != old_x or self.player.y != old_y:
            if self.player.x > old_x:
                self.last_move_direction = {'x': 1, 'y': 0}  # Right
            elif self.player.x < old_x:
                self.last_move_direction = {'x': -1, 'y': 0}  # Left
            elif self.player.y > old_y:
                self.last_move_direction = {'x': 0, 'y': 1}  # Down
            elif self.player.y < old_y:
                self.last_move_direction = {'x': 0, 'y': -1}  # Up
        
        # Check power-up effects
        current_time = pygame.time.get_ticks()
        if current_time - self.speed_boost_timer > self.speed_boost_duration:
            self.player.speed = 5  # Reset to normal speed
        
        # Handle magnet effect - automatically collect nearby power-ups
        if current_time - self.magnet_timer < self.magnet_duration:
            for power_up in self.power_ups[:]:
                distance = math.sqrt((power_up.x - self.player.x)**2 + (power_up.y - self.player.y)**2)
                if distance <= 100:  # Magnet range
                    # Move power-up toward player
                    dx = self.player.x - power_up.x
                    dy = self.player.y - power_up.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        power_up.x += (dx / dist) * 5
                        power_up.y += (dy / dist) * 5
        
        # Silence aura effect - automatically damages nearby enemies
        if current_time - self.silence_aura_timer < self.silence_aura_duration:
            for enemy in self.enemies[:]:
                distance = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                if distance <= 60:  # Smaller than shush range
                    enemy.health -= 1
                    if enemy.health <= 0:
                        self.create_particles(enemy.x, enemy.y, enemy.color)
                        if enemy in self.enemies:  # Safety check
                            self.enemies.remove(enemy)
                        score_bonus = 20 if enemy.monster_type == "chaos_lord" else 10
                        self.score += score_bonus
        
        # Spawn enemies (with increasing difficulty)
        current_time = pygame.time.get_ticks()
        # Decrease spawn delay over time (minimum 500ms)
        time_difficulty_factor = max(0.5, 1.0 - (current_time / 120000))  # 2 minutes to reach max difficulty
        
        # Apply difficulty multiplier
        difficulty_multiplier = {
            DIFFICULTY_EASY: 0.7,
            DIFFICULTY_NORMAL: 1.0,
            DIFFICULTY_HARD: 1.4,
            DIFFICULTY_EXPERT: 1.8
        }
        
        current_spawn_delay = int(self.enemy_spawn_delay * time_difficulty_factor * difficulty_multiplier[self.selected_difficulty])
        
        if current_time - self.enemy_spawn_timer > current_spawn_delay:
            self.spawn_enemy()
            self.enemy_spawn_timer = current_time
        
        # Spawn power-ups
        if current_time - self.power_up_spawn_timer > self.power_up_spawn_delay:
            self.spawn_power_up()
            self.power_up_spawn_timer = current_time
        
        # Update enemies (with time freeze effect)
        current_time = pygame.time.get_ticks()
        time_frozen = current_time - self.time_freeze_timer < self.time_freeze_duration
        freeze_time_active = current_time - self.freeze_time_timer < self.freeze_time_duration
        
        for enemy in self.enemies[:]:
            if not time_frozen and not freeze_time_active:  # Only move if time isn't frozen
                # Give enemy the player's position for chasing
                enemy.player_x = self.player.x + self.player.width // 2
                enemy.player_y = self.player.y + self.player.height // 2
                enemy.update()
            
            # Check if enemy touches player (GAME OVER)
            if (abs(enemy.x - self.player.x) < 30 and abs(enemy.y - self.player.y) < 30):
                # Check if player has shield
                if current_time - self.shield_timer < self.shield_duration:
                    # Shield protects player - destroy enemy instead
                    self.create_particles(enemy.x, enemy.y, enemy.color)
                    if enemy in self.enemies:  # Safety check
                        self.enemies.remove(enemy)
                    self.score += 10
                    self.sound_manager.play('enemy_defeat')
                else:
                    # Player caught! Game over
                    self.state = GAME_OVER
                    self.sound_manager.play('game_over')
                    self.is_new_high_score = self.high_score_manager.add_score(self.score)
                    if self.is_new_high_score:
                        self.sound_manager.play('new_high_score')
                    return  # Exit update loop immediately
            
            # Handle exploding bomb explosion
            if enemy.monster_type == "exploding_bomb" and enemy.health <= 0:
                # Create explosion effect - damage nearby enemies and player
                explosion_radius = 80
                for nearby_enemy in self.enemies[:]:
                    if nearby_enemy != enemy:
                        distance = math.sqrt((nearby_enemy.x - enemy.x)**2 + (nearby_enemy.y - enemy.y)**2)
                        if distance < explosion_radius:
                            nearby_enemy.health -= 2  # Explosion damage
                            if nearby_enemy.health <= 0:
                                self.create_particles(nearby_enemy.x, nearby_enemy.y, nearby_enemy.color)
                                if nearby_enemy in self.enemies:  # Safety check
                                    self.enemies.remove(nearby_enemy)
                                self.score += 10
                
                # Check if player is in explosion radius
                player_distance = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)
                if player_distance < explosion_radius:
                    # Player takes damage from explosion
                    if current_time - self.shield_timer > self.shield_duration:  # Shield doesn't protect from explosion
                        self.state = GAME_OVER
                        self.sound_manager.play('game_over')
                        self.is_new_high_score = self.high_score_manager.add_score(self.score)
                        if self.is_new_high_score:
                            self.sound_manager.play('new_high_score')
                        return
            
            # Remove enemies that go off-screen (they escaped, no penalty)
            if enemy.x < -50 or enemy.x > SCREEN_WIDTH + 50 or enemy.y < -50 or enemy.y > SCREEN_HEIGHT + 50:
                self.enemies.remove(enemy)
        
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
        
        # Check win condition - all monsters killed
        if len(self.enemies) == 0 and len(self.books) == 0:
            # All monsters defeated! Spawn next wave or end game
            self.spawn_next_wave()
    
    def spawn_enemy(self):
        # More variety in enemy types based on time and difficulty
        current_time = pygame.time.get_ticks()
        
        # Adjust spawn rates based on difficulty
        difficulty_multiplier = {
            DIFFICULTY_EASY: 0.7,
            DIFFICULTY_NORMAL: 1.0,
            DIFFICULTY_HARD: 1.4,
            DIFFICULTY_EXPERT: 1.8
        }
        
        # Spawn multiple enemies on higher difficulties
        spawn_count = 1
        if self.selected_difficulty >= DIFFICULTY_HARD and random.random() < 0.4:
            spawn_count = 2
        if self.selected_difficulty == DIFFICULTY_EXPERT and random.random() < 0.3:
            spawn_count = 3
        # Even on normal difficulty, occasionally spawn 2 enemies
        if self.selected_difficulty == DIFFICULTY_NORMAL and random.random() < 0.15:
            spawn_count = 2
            
        for _ in range(spawn_count):
            if current_time > 60000:  # After 1 minute, add chaos lords and literary villains
                enemy_type = random.choices(
                        ["student", "animal", "ghost", "chaos_lord", "literary_villain", "book_worm", "noise_demon"],
                        weights=[25, 20, 15, 15, 10, 10, 5]
                )[0]
            elif current_time > 30000:  # After 30 seconds, add more ghosts and literary villains
                enemy_type = random.choices(
                        ["student", "animal", "ghost", "literary_villain", "book_worm"],
                        weights=[30, 25, 20, 15, 10]
                )[0]
            else:
                enemy_type = random.choices(
                        ["student", "animal", "ghost", "book_worm"],
                        weights=[40, 30, 20, 10]
                )[0]
            
            enemy = NoisyMonster(enemy_type, self.library_maze)
            self.enemies.append(enemy)
    
    def spawn_next_wave(self):
        """Spawn the next wave of enemies when all are defeated"""
        current_time = pygame.time.get_ticks()
        
        # Increase wave difficulty
        wave_number = getattr(self, 'wave_number', 1) + 1
        self.wave_number = wave_number
        
        # Spawn more enemies each wave
        enemies_to_spawn = min(3 + wave_number, 8)  # Cap at 8 enemies per wave
        
        for _ in range(enemies_to_spawn):
            # Spawn enemies immediately (no delay to avoid freezing)
            self.spawn_enemy()
        
        # Bonus score for clearing wave
        wave_bonus = wave_number * 100
        self.score += wave_bonus
        
        # Show wave completion message
        self.current_quote = f"Wave {wave_number-1} Complete! +{wave_bonus} points"
        self.quote_author = "Librarian"
        self.quote_timer = current_time
    
    def spawn_power_up(self):
        power_up = PowerUp()
        self.power_ups.append(power_up)
    
    def throw_book_mouse(self, target_pos):
        # Create a book that moves towards the mouse position
        current_time = pygame.time.get_ticks()
        is_mega_book = current_time - self.mega_book_timer < self.mega_book_duration
        is_multi_shot = current_time - self.multi_shot_timer < self.multi_shot_duration
        
        if is_multi_shot:
            # Multi-shot: throw 3 books in a spread pattern
            angles = [-15, 0, 15]  # degrees
            for angle in angles:
                # Calculate target position with angle offset
                dx = target_pos[0] - (self.player.x + self.player.width)
                dy = target_pos[1] - (self.player.y + self.player.height // 2)
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:  # Avoid division by zero
                    # Apply angle rotation
                    rad_angle = math.radians(angle)
                    cos_a = math.cos(rad_angle)
                    sin_a = math.sin(rad_angle)
                    
                    new_dx = dx * cos_a - dy * sin_a
                    new_dy = dx * sin_a + dy * cos_a
                    
                    new_target = (self.player.x + self.player.width + new_dx, 
                                self.player.y + self.player.height // 2 + new_dy)
                else:
                    new_target = target_pos
                
                book = Book(self.player.x + self.player.width, 
                           self.player.y + self.player.height // 2, 
                           new_target, is_mega_book)
                self.books.append(book)
        else:
            # Single shot
            book = Book(self.player.x + self.player.width, 
                       self.player.y + self.player.height // 2, 
                       target_pos, is_mega_book)
            self.books.append(book)
    
    def throw_book_keyboard(self):
        # Create a book that moves in the last movement direction
        current_time = pygame.time.get_ticks()
        is_mega_book = current_time - self.mega_book_timer < self.mega_book_duration
        is_multi_shot = current_time - self.multi_shot_timer < self.multi_shot_duration
        
        # Calculate target position based on last movement direction
        start_x = self.player.x + self.player.width
        start_y = self.player.y + self.player.height // 2
        
        # Shoot in the direction of last movement (or right by default)
        target_x = start_x + (self.last_move_direction['x'] * 300)
        target_y = start_y + (self.last_move_direction['y'] * 300)
        
        if is_multi_shot:
            # Multi-shot: throw 3 books in a spread pattern
            angles = [-15, 0, 15]  # degrees
            for angle in angles:
                # Calculate target position with angle offset
                dx = target_x - start_x
                dy = target_y - start_y
                
                # Apply angle rotation
                rad_angle = math.radians(angle)
                cos_a = math.cos(rad_angle)
                sin_a = math.sin(rad_angle)
                
                new_dx = dx * cos_a - dy * sin_a
                new_dy = dx * sin_a + dy * cos_a
                
                new_target_x = start_x + new_dx
                new_target_y = start_y + new_dy
                
                book = Book(start_x, start_y, (new_target_x, new_target_y), is_mega_book)
                self.books.append(book)
        else:
            # Single shot
            book = Book(start_x, start_y, (target_x, target_y), is_mega_book)
            self.books.append(book)
    
    def shush_attack(self):
        # AOE attack - silence all enemies in range
        shush_range = 100
        for enemy in self.enemies[:]:
            distance = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
            if distance <= shush_range:
                enemy.health -= 2  # Shush does more damage
                if enemy.health <= 0:
                    self.create_particles(enemy.x, enemy.y, enemy.color)
                    if enemy in self.enemies:  # Safety check
                        self.enemies.remove(enemy)
                    score_bonus = 20 if enemy.monster_type == "chaos_lord" else 10
                    self.score += score_bonus
                    self.play_enemy_defeat_sound(enemy.monster_type)
    
    def check_collisions(self):
        # Check book-enemy collisions
        for book in self.books[:]:
            for enemy in self.enemies[:]:
                if (abs(book.x - enemy.x) < 30 and abs(book.y - enemy.y) < 30):
                    if book.is_mega:
                        # Mega book has area damage - damage all nearby enemies
                        for nearby_enemy in self.enemies[:]:
                            distance = math.sqrt((nearby_enemy.x - book.x)**2 + (nearby_enemy.y - book.y)**2)
                            if distance < 80:  # Area of effect
                                nearby_enemy.health -= 1
                                if nearby_enemy.health <= 0:
                                    self.create_particles(nearby_enemy.x, nearby_enemy.y, nearby_enemy.color)
                                    if nearby_enemy in self.enemies:  # Safety check
                                        self.enemies.remove(nearby_enemy)
                                    score_bonus = 20 if nearby_enemy.monster_type == "chaos_lord" else 10
                                    self.score += score_bonus
                                    self.play_enemy_defeat_sound(nearby_enemy.monster_type)
                    else:
                        # Regular book - single target damage with literary effects
                        # Handle shielded knight special mechanics
                        if enemy.monster_type == "shielded_knight" and hasattr(enemy, 'shield_health') and enemy.shield_health > 0:
                            # Shield absorbs damage first
                            enemy.shield_health -= book.damage
                            if enemy.shield_health <= 0:
                                enemy.health -= abs(enemy.shield_health)  # Excess damage goes to health
                        else:
                            enemy.health -= book.damage  # Use book type damage
                        
                        # Special effects for magical tomes
                        if book.book_type == "magical_tome":
                            # Magical tome has special effects
                            if random.random() < 0.3:  # 30% chance for special effect
                                if book.genre == "fantasy":
                                    # Freeze nearby enemies
                                    for nearby_enemy in self.enemies[:]:
                                        if nearby_enemy != enemy:
                                            distance = math.sqrt((nearby_enemy.x - book.x)**2 + (nearby_enemy.y - book.y)**2)
                                            if distance < 60:
                                                nearby_enemy.speed *= 0.5  # Slow down
                                elif book.genre == "horror":
                                    # Fear effect - enemies move away
                                    enemy.speed *= 1.5  # Speed up to run away
                                elif book.genre == "science":
                                    # Chain lightning effect
                                    for nearby_enemy in self.enemies[:]:
                                        if nearby_enemy != enemy:
                                            distance = math.sqrt((nearby_enemy.x - book.x)**2 + (nearby_enemy.y - book.y)**2)
                                            if distance < 80:
                                                nearby_enemy.health -= 1
                        
                        if enemy.health <= 0:
                            self.create_particles(enemy.x, enemy.y, enemy.color)
                            if enemy in self.enemies:  # Safety check
                                self.enemies.remove(enemy)
                            score_bonus = 20 if enemy.monster_type == "chaos_lord" else 10
                            self.score += score_bonus
                            self.play_enemy_defeat_sound(enemy.monster_type)
                            
                            # Literary collection system
                            self.collect_book(book)
                    if book in self.books:  # Safety check
                        self.books.remove(book)
                    break
        
        # Check player-power-up collisions
        for power_up in self.power_ups[:]:
            if (abs(power_up.x - self.player.x) < 40 and 
                abs(power_up.y - self.player.y) < 50):
                self.collect_power_up(power_up)
                if power_up in self.power_ups:  # Safety check
                    self.power_ups.remove(power_up)
                self.play_power_up_sound(power_up.type)
    
    def collect_power_up(self, power_up):
        current_time = pygame.time.get_ticks()
        if power_up.type == "coffee":
            self.speed_boost_timer = current_time
            self.player.speed = 8  # Double speed
        elif power_up.type == "mega_book":
            self.mega_book_timer = current_time
        elif power_up.type == "silence_aura":
            self.silence_aura_timer = current_time
        elif power_up.type == "time_freeze":
            self.time_freeze_timer = current_time
        elif power_up.type == "shield":
            self.shield_timer = current_time
        elif power_up.type == "multi_shot":
            self.multi_shot_timer = current_time
        elif power_up.type == "magnet":
            self.magnet_timer = current_time
        elif power_up.type == "freeze_time":
            self.freeze_time_timer = current_time
    
    def play_enemy_defeat_sound(self, enemy_type):
        """Play appropriate defeat sound based on enemy type"""
        sound_map = {
            'student': 'student_defeat',
            'animal': 'animal_defeat',
            'ghost': 'ghost_defeat',
            'chaos_lord': 'chaos_lord_defeat',
            'literary_villain': 'literary_villain_defeat'
        }
        sound_name = sound_map.get(enemy_type, 'enemy_defeat')
        self.sound_manager.play(sound_name)
    
    def play_power_up_sound(self, power_up_type):
        """Play appropriate pickup sound based on power-up type"""
        sound_map = {
            'coffee': 'coffee_pickup',
            'mega_book': 'book_pickup',
            'silence_aura': 'aura_pickup',
            'time_freeze': 'freeze_pickup'
        }
        sound_name = sound_map.get(power_up_type, 'power_up')
        self.sound_manager.play(sound_name)
    
    def collect_book(self, book):
        """Handle book collection for literary features"""
        # Add to collections
        self.collected_books.add(book.genre)
        self.discovered_authors.add(book.author)
        
        # Display quote
        self.current_quote = book.quote
        self.quote_author = book.author
        self.quote_timer = pygame.time.get_ticks()
        
        # Level up reading level
        if len(self.collected_books) >= self.reading_level * 3:
            self.reading_level += 1
            # Bonus score for literary progression
            self.score += self.reading_level * 50
    
    def get_bibliophile_title(self):
        """Get current bibliophile title based on reading level"""
        titles = [
            "Novice Reader", "Book Enthusiast", "Avid Reader", 
            "Bibliophile", "Literary Scholar", "Master Librarian",
            "Keeper of Knowledge", "Literary Sage", "Grand Bibliophile"
        ]
        return titles[min(self.reading_level - 1, len(titles) - 1)]
    
    def create_particles(self, x, y, color, count=5):
        for _ in range(count):
            particle = Particle(x, y, color)
            self.particles.append(particle)
    
    def draw(self):
        self.screen.fill(WHITE)
        
        if self.state == MENU:
            self.draw_menu()
        elif self.state == CHARACTER_SELECT:
            self.draw_character_select()
        elif self.state == CHAPTER_SELECT:
            self.draw_chapter_select()
        elif self.state == DIFFICULTY_SELECT:
            self.draw_difficulty_select()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        elif self.state == SETTINGS:
            self.draw_game()
            self.draw_settings()
        
        pygame.display.flip()
    
    def draw_game(self):
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
    
    def draw_menu(self):
        # Modern gradient background
        self.draw_modern_gradient_background()
        
        # Modern title with enhanced typography
        self.draw_modern_title()
        
        # Clean menu options with modern styling
        self.draw_modern_menu_options()
        
        # Modern instructions panel
        self.draw_modern_instructions()
        
        # Latest score display (fixed)
        self.draw_latest_score()
        
        # Modern decorative elements
        self.draw_modern_decorations()
    
    def draw_modern_gradient_background(self):
        """Draw an enhanced modern gradient background with animated elements"""
        # Create a sophisticated animated gradient
        time_offset = pygame.time.get_ticks() * 0.001
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            # Animated gradient with subtle color shifts
            # Ensure all color values are valid integers between 0-255
            r = max(0, min(255, int(15 + (20 * ratio) + 5 * math.sin(time_offset + ratio * 2))))
            g = max(0, min(255, int(20 + (25 * ratio) + 3 * math.cos(time_offset + ratio * 1.5))))
            b = max(0, min(255, int(30 + (30 * ratio) + 4 * math.sin(time_offset * 0.8 + ratio * 3))))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Add animated floating particles
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(30):
            x = (i * 80 + time_offset * 20) % (SCREEN_WIDTH + 40) - 20
            y = (i * 60 + time_offset * 15) % (SCREEN_HEIGHT + 40) - 20
            alpha = int(20 + 15 * math.sin(time_offset * 2 + i))
            size = 1 + int(2 * math.sin(time_offset * 3 + i * 0.5))
            pygame.draw.circle(overlay, (255, 255, 255, alpha), (int(x), int(y)), size)
        
        # Add subtle grid pattern
        for i in range(0, SCREEN_WIDTH, 60):
            for j in range(0, SCREEN_HEIGHT, 60):
                alpha = int(5 + 3 * math.sin(time_offset + i * 0.01 + j * 0.01))
                pygame.draw.circle(overlay, (255, 255, 255, alpha), (i, j), 1)
        
        self.screen.blit(overlay, (0, 0))
    
    def draw_modern_title(self):
        """Draw modern title with enhanced typography and animations"""
        time_offset = pygame.time.get_ticks() * 0.002
        
        # Main title with modern styling and animation
        title_font = pygame.font.Font(None, 88)
        subtitle_font = pygame.font.Font(None, 36)
        
        # Animated title with pulsing glow
        pulse = 1.0 + 0.1 * math.sin(time_offset * 3)
        title_text = title_font.render("LIBRARY DEFENDER", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        
        # Enhanced glow effect with animation
        for offset in range(5, 0, -1):
            glow_intensity = int(60 - offset * 10 + 20 * math.sin(time_offset * 2 + offset))
            glow_color = (255, 215, 0)
            glow_surface = pygame.Surface((title_rect.width + offset * 6, title_rect.height + offset * 6), pygame.SRCALPHA)
            glow_text = title_font.render("LIBRARY DEFENDER", True, glow_color)
            glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
            glow_surface.blit(glow_text, glow_rect)
            # Apply alpha to the entire surface
            glow_surface.set_alpha(glow_intensity)
            self.screen.blit(glow_surface, (title_rect.x - offset * 3, title_rect.y - offset * 3))
        
        # Main title with subtle animation
        title_y = 120 + int(2 * math.sin(time_offset * 1.5))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        self.screen.blit(title_text, title_rect)
        
        # Enhanced subtitle with fade effect
        fade = 0.8 + 0.2 * math.sin(time_offset * 2)
        # Ensure color values are valid integers
        color_val = max(0, min(255, int(200 * fade)))
        subtitle_color = (color_val, color_val, color_val)
        subtitle_text = subtitle_font.render("Defend the Sacred Silence", True, subtitle_color)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Add decorative line under title
        line_y = subtitle_rect.bottom + 10
        line_width = 200 + int(20 * math.sin(time_offset * 2))
        line_x = (SCREEN_WIDTH - line_width) // 2
        # Create a surface for the line with alpha
        line_surface = pygame.Surface((line_width, 2), pygame.SRCALPHA)
        line_surface.fill((255, 215, 0, 100))
        self.screen.blit(line_surface, (line_x, line_y))
        
    def draw_modern_menu_options(self):
        """Draw modern menu options with enhanced animations and effects"""
        time_offset = pygame.time.get_ticks() * 0.003
        menu_font = pygame.font.Font(None, 38)
        menu_options = [
            ("SPACE", "Endless Mode", "Defend against endless waves"),
            ("S", "Story Mode", "Epic campaign adventure"),
            ("D", "Difficulty", "Choose your challenge level"),
            ("ESC", "Settings", "Customize your experience")
        ]
        
        start_y = 260
        for i, (key, title, description) in enumerate(menu_options):
            y_pos = start_y + i * 85
            
            # Animated button position
            hover_offset = 0
            if i == self.menu_selection:
                hover_offset = int(3 * math.sin(time_offset * 4 + i))
            
            # Modern button background with enhanced styling
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, y_pos - 15 + hover_offset, 440, 70)
            
            # Enhanced button styling with animations
            if i == self.menu_selection:
                # Selected button with pulsing effect
                pulse = 0.8 + 0.2 * math.sin(time_offset * 6)
                # Ensure color values are valid integers
                r = max(0, min(255, int(255 * pulse)))
                g = max(0, min(255, int(215 * pulse)))
                b = max(0, min(255, int(0 * pulse)))
                glow_color = (r, g, b, 40)
                pygame.draw.rect(self.screen, glow_color, button_rect)
                pygame.draw.rect(self.screen, (255, 215, 0), button_rect, 3)
                
                # Add inner glow
                inner_rect = pygame.Rect(button_rect.x + 2, button_rect.y + 2, button_rect.width - 4, button_rect.height - 4)
                inner_surface = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
                inner_surface.fill((255, 215, 0, 20))
                self.screen.blit(inner_surface, (inner_rect.x, inner_rect.y))
                
                text_color = (255, 255, 200)
                key_color = (255, 255, 0)
            else:
                # Unselected button with subtle animation
                alpha = 15 + int(5 * math.sin(time_offset * 2 + i))
                unselected_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
                unselected_surface.fill((255, 255, 255, alpha))
                self.screen.blit(unselected_surface, (button_rect.x, button_rect.y))
                pygame.draw.rect(self.screen, (120, 120, 120), button_rect, 1)
                text_color = (220, 220, 220)
                key_color = (180, 180, 180)
            
            # Enhanced key binding with glow
            key_text = menu_font.render(f"[{key}]", True, key_color)
            key_rect = key_text.get_rect(center=(SCREEN_WIDTH // 2 - 130, y_pos + hover_offset))
            self.screen.blit(key_text, key_rect)
            
            # Title with enhanced styling
            title_text = menu_font.render(title, True, text_color)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + hover_offset))
            self.screen.blit(title_text, title_rect)
            
            # Description with fade effect
            desc_font = pygame.font.Font(None, 22)
            desc_alpha = 0.7 + 0.3 * math.sin(time_offset * 1.5 + i)
            # Ensure color values are valid integers
            color_val = max(0, min(255, int(150 * desc_alpha)))
            desc_color = (color_val, color_val, color_val)
            desc_text = desc_font.render(description, True, desc_color)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 30 + hover_offset))
            self.screen.blit(desc_text, desc_rect)
    
    def draw_modern_instructions(self):
        """Draw enhanced modern instructions panel with animations"""
        time_offset = pygame.time.get_ticks() * 0.002
        
        # Enhanced instructions panel with gradient
        panel_rect = pygame.Rect(40, SCREEN_HEIGHT - 220, SCREEN_WIDTH - 80, 180)
        
        # Create gradient background for panel
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        for y in range(panel_rect.height):
            ratio = y / panel_rect.height
            alpha = int(120 + 30 * ratio)
            color = (10, 15, 25, alpha)
            pygame.draw.line(panel_surface, color, (0, y), (panel_rect.width, y))
        
        # Add animated border
        border_alpha = int(80 + 20 * math.sin(time_offset * 3))
        border_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        border_surface.fill((255, 215, 0, border_alpha))
        panel_surface.blit(border_surface, (0, 0))
        
        # Add inner glow
        inner_rect = pygame.Rect(2, 2, panel_rect.width - 4, panel_rect.height - 4)
        inner_surface = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
        inner_surface.fill((255, 215, 0, 20))
        panel_surface.blit(inner_surface, (inner_rect.x, inner_rect.y))
        
        self.screen.blit(panel_surface, panel_rect)
        
        # Enhanced instructions title with glow
        title_font = pygame.font.Font(None, 28)
        title_text = title_font.render("CONTROLS", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 25))
        
        # Title glow effect
        for offset in range(2, 0, -1):
            glow_surface = pygame.Surface((title_rect.width + offset * 4, title_rect.height + offset * 4), pygame.SRCALPHA)
            glow_text = title_font.render("CONTROLS", True, (255, 215, 0))
            glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
            glow_surface.blit(glow_text, glow_rect)
            # Apply alpha to the entire surface
            glow_surface.set_alpha(30 - offset * 10)
            self.screen.blit(glow_surface, (title_rect.x - offset * 2, title_rect.y - offset * 2))
        
        self.screen.blit(title_text, title_rect)
        
        # Enhanced instructions with icons and animations
        instruction_font = pygame.font.Font(None, 20)
        instructions = [
            ("🎮", "WASD / Arrow Keys: Move"),
            ("📚", "Mouse Click / Space: Throw Books"),
            ("🤫", "Shift: Shush Attack"),
            ("⚡", "Collect Power-ups for Advantages")
        ]
        
        for i, (icon, instruction) in enumerate(instructions):
            # Animated text color
            text_alpha = 0.8 + 0.2 * math.sin(time_offset * 2 + i * 0.5)
            # Ensure color values are valid integers
            color_val = max(0, min(255, int(200 * text_alpha)))
            text_color = (color_val, color_val, color_val)
            
            # Icon
            icon_text = instruction_font.render(icon, True, (255, 215, 0))
            icon_rect = icon_text.get_rect(center=(panel_rect.centerx - 120, panel_rect.y + 60 + i * 25))
            self.screen.blit(icon_text, icon_rect)
            
            # Instruction text
            instruction_text = instruction_font.render(instruction, True, text_color)
            instruction_rect = instruction_text.get_rect(center=(panel_rect.centerx, panel_rect.y + 60 + i * 25))
            self.screen.blit(instruction_text, instruction_rect)
    
    def draw_latest_score(self):
        """Draw enhanced latest score with animations and effects"""
        time_offset = pygame.time.get_ticks() * 0.002
        high_scores = self.high_score_manager.get_high_scores()
        
        if high_scores:
            # Enhanced score panel with gradient
            score_panel = pygame.Rect(SCREEN_WIDTH - 280, 40, 240, 140)
            
            # Create gradient background
            panel_surface = pygame.Surface((score_panel.width, score_panel.height), pygame.SRCALPHA)
            for y in range(score_panel.height):
                ratio = y / score_panel.height
                alpha = int(180 + 40 * ratio)
                color = (15, 20, 30, alpha)
                pygame.draw.line(panel_surface, color, (0, y), (score_panel.width, y))
            
            # Animated border
            border_alpha = int(100 + 30 * math.sin(time_offset * 4))
            border_surface = pygame.Surface((score_panel.width, score_panel.height), pygame.SRCALPHA)
            border_surface.fill((255, 215, 0, border_alpha))
            panel_surface.blit(border_surface, (0, 0))
            
            # Inner glow
            inner_rect = pygame.Rect(3, 3, score_panel.width - 6, score_panel.height - 6)
            inner_surface = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
            inner_surface.fill((255, 215, 0, 30))
            panel_surface.blit(inner_surface, (inner_rect.x, inner_rect.y))
            
            self.screen.blit(panel_surface, score_panel)
            
            # Enhanced title with glow
            title_font = pygame.font.Font(None, 26)
            title_text = title_font.render("LATEST SCORE", True, (255, 215, 0))
            title_rect = title_text.get_rect(center=(score_panel.centerx, score_panel.y + 25))
            
            # Title glow
            for offset in range(2, 0, -1):
                glow_surface = pygame.Surface((title_rect.width + offset * 4, title_rect.height + offset * 4), pygame.SRCALPHA)
                glow_text = title_font.render("LATEST SCORE", True, (255, 215, 0))
                glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
                glow_surface.blit(glow_text, glow_rect)
                # Apply alpha to the entire surface
                glow_surface.set_alpha(40 - offset * 15)
                self.screen.blit(glow_surface, (title_rect.x - offset * 2, title_rect.y - offset * 2))
            
            self.screen.blit(title_text, title_rect)
            
            # Enhanced latest score with pulsing effect
            score_font = pygame.font.Font(None, 36)
            latest_score = high_scores[0] if high_scores else 0
            pulse = 1.0 + 0.1 * math.sin(time_offset * 5)
            # Ensure all color values are valid integers between 0-255
            r = max(0, min(255, int(255 * pulse)))
            g = max(0, min(255, int(255 * pulse)))
            b = max(0, min(255, int(200 * pulse)))
            score_color = (r, g, b)
            score_text = score_font.render(f"{latest_score:,}", True, score_color)
            score_rect = score_text.get_rect(center=(score_panel.centerx, score_panel.y + 65))
            self.screen.blit(score_text, score_rect)
            
            # Enhanced high score indicator
            if len(high_scores) > 1:
                high_score_font = pygame.font.Font(None, 20)
                high_score_text = high_score_font.render("🏆 HIGH SCORE", True, (255, 215, 0))
                high_score_rect = high_score_text.get_rect(center=(score_panel.centerx, score_panel.y + 95))
                self.screen.blit(high_score_text, high_score_rect)
                
                # Add achievement indicator
                achievement_font = pygame.font.Font(None, 16)
                achievement_text = achievement_font.render("NEW RECORD!", True, (0, 255, 0))
                achievement_rect = achievement_text.get_rect(center=(score_panel.centerx, score_panel.y + 115))
                self.screen.blit(achievement_text, achievement_rect)
    
    def draw_modern_decorations(self):
        """Draw enhanced modern decorative elements with animations"""
        time_offset = pygame.time.get_ticks() * 0.001
        
        # Enhanced floating particles with different sizes and speeds
        for i in range(25):
            speed = 0.5 + (i % 3) * 0.3
            x = (i * 80 + time_offset * speed * 30) % (SCREEN_WIDTH + 40) - 20
            y = (i * 60 + time_offset * speed * 20) % (SCREEN_HEIGHT + 40) - 20
            size = 1 + (i % 3)
            alpha = int(40 + 20 * math.sin(time_offset * 2 + i))
            color = (255, 255, 255, alpha)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), size)
        
        # Enhanced corner accents with animations
        corner_size = 25
        corners = [(0, 0), (SCREEN_WIDTH - corner_size, 0), 
                  (0, SCREEN_HEIGHT - corner_size), (SCREEN_WIDTH - corner_size, SCREEN_HEIGHT - corner_size)]
        
        for i, (x, y) in enumerate(corners):
            # Animated corner glow
            pulse = 0.8 + 0.2 * math.sin(time_offset * 3 + i)
            alpha = int(120 * pulse)
            
            # Outer glow
            glow_surface = pygame.Surface((corner_size, corner_size), pygame.SRCALPHA)
            glow_surface.fill((255, 215, 0, alpha))
            self.screen.blit(glow_surface, (x, y))
            # Inner border
            pygame.draw.rect(self.screen, (255, 215, 0), (x, y, corner_size, corner_size), 3)
            # Inner glow
            inner_size = corner_size - 6
            inner_glow_surface = pygame.Surface((inner_size, inner_size), pygame.SRCALPHA)
            inner_glow_surface.fill((255, 215, 0, 60))
            self.screen.blit(inner_glow_surface, (x + 3, y + 3))
        
        # Add floating book icons
        for i in range(8):
            x = (i * 150 + time_offset * 10) % (SCREEN_WIDTH + 30) - 15
            y = (i * 100 + time_offset * 8) % (SCREEN_HEIGHT + 30) - 15
            alpha = int(30 + 15 * math.sin(time_offset * 1.5 + i))
            # Draw book icon
            book_surface = pygame.Surface((8, 12), pygame.SRCALPHA)
            book_surface.fill((255, 215, 0, alpha))
            self.screen.blit(book_surface, (int(x), int(y)))
            pygame.draw.rect(self.screen, (255, 215, 0), (int(x), int(y), 8, 12), 1)
        
        # Add subtle scan lines effect
        scan_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            alpha = int(5 + 3 * math.sin(time_offset * 10 + y * 0.01))
            pygame.draw.line(scan_overlay, (255, 255, 255, alpha), (0, y), (SCREEN_WIDTH, y), 1)
        self.screen.blit(scan_overlay, (0, 0))
        
        # High scores
        high_scores = self.high_score_manager.get_high_scores()
        if high_scores:
            font = pygame.font.Font(None, 24)
            scores_title = font.render("HALL OF SCHOLARLY FAME", True, GOLD)
            scores_rect = scores_title.get_rect(center=(SCREEN_WIDTH//2, 480))
            shadow = font.render("HALL OF SCHOLARLY FAME", True, BLACK)
            shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH//2 + 1, 481))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(scores_title, scores_rect)
            
            font = pygame.font.Font(None, 20)
            for i, score in enumerate(high_scores[:5]):  # Show top 5
                score_text = font.render(f"{i+1}. {score} Knowledge Points", True, CREAM)
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 510 + i * 20))
                self.screen.blit(score_text, score_rect)
        
        # Decorative elements
        self.draw_menu_decorations()
    
    def draw_character_select(self):
        # Character selection screen with dark academia theme
        self.screen.fill(DARK_BROWN)
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("Choose Your Librarian", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Character preview areas
        female_rect = pygame.Rect(150, 200, 200, 200)
        male_rect = pygame.Rect(450, 200, 200, 200)
        
        # Draw character preview backgrounds
        selected_color = GOLD if self.selected_character == "female" else CREAM
        pygame.draw.rect(self.screen, selected_color, female_rect, 3)
        pygame.draw.rect(self.screen, CREAM, female_rect.inflate(-6, -6))
        
        selected_color = GOLD if self.selected_character == "male" else CREAM
        pygame.draw.rect(self.screen, selected_color, male_rect, 3)
        pygame.draw.rect(self.screen, CREAM, male_rect.inflate(-6, -6))
        
        # Draw character previews (large sprites)
        female_sprite = self.sprite_manager.get_sprite("female_librarian_down")
        male_sprite = self.sprite_manager.get_sprite("male_librarian_down")
        
        if female_sprite:
            # Scale up for preview
            large_female = pygame.transform.scale(female_sprite, (100, 120))
            female_pos = (female_rect.centerx - 50, female_rect.centery - 40)
            self.screen.blit(large_female, female_pos)
        else:
            # Draw placeholder
            pygame.draw.circle(self.screen, (255, 182, 193), female_rect.center, 40)
            font = pygame.font.Font(None, 24)
            text = font.render("Female", True, BLACK)
            text_rect = text.get_rect(center=female_rect.center)
            self.screen.blit(text, text_rect)
        
        if male_sprite:
            # Scale up for preview
            large_male = pygame.transform.scale(male_sprite, (100, 120))
            male_pos = (male_rect.centerx - 50, male_rect.centery - 40)
            self.screen.blit(large_male, male_pos)
        else:
            # Draw placeholder
            pygame.draw.circle(self.screen, (173, 216, 230), male_rect.center, 40)
            font = pygame.font.Font(None, 24)
            text = font.render("Male", True, BLACK)
            text_rect = text.get_rect(center=male_rect.center)
            self.screen.blit(text, text_rect)
        
        # Character labels
        font = pygame.font.Font(None, 36)
        female_text = font.render("Female Librarian", True, CREAM)
        female_text_rect = female_text.get_rect(center=(female_rect.centerx, female_rect.bottom + 30))
        self.screen.blit(female_text, female_text_rect)
        
        male_text = font.render("Male Librarian", True, CREAM)
        male_text_rect = male_text.get_rect(center=(male_rect.centerx, male_rect.bottom + 30))
        self.screen.blit(male_text, male_text_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 28)
        instructions = [
            "Press 1 for Female Librarian",
            "Press 2 for Male Librarian", 
            "Press SPACE to Start Game",
            "Press ESC to go Back"
        ]
        
        start_y = 480
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, CREAM)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 30))
            self.screen.blit(text, text_rect)
        
        # Current selection indicator
        selection_font = pygame.font.Font(None, 32)
        current_text = f"Selected: {self.selected_character.title()} Librarian"
        current_color = GOLD
        text = selection_font.render(current_text, True, current_color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(text, text_rect)
    
    def draw_chapter_select(self):
        # Story mode chapter selection screen
        self.screen.fill(DARK_BROWN)
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("The Great Library Crisis", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        subtitle_font = pygame.font.Font(None, 28)
        subtitle_text = subtitle_font.render("Choose Your Chapter", True, CREAM)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Chapter buttons
        for chapter_num in range(1, 6):
            chapter_data = STORY_CHAPTERS[chapter_num]
            is_unlocked = self.story_progress.get(chapter_num, False)
            
            # Button position
            button_y = 150 + (chapter_num - 1) * 80
            button_rect = pygame.Rect(100, button_y, 600, 60)
            
            # Button appearance based on unlock status
            if is_unlocked:
                button_color = RICH_BROWN
                border_color = GOLD
                text_color = CREAM
            else:
                button_color = DIM_GRAY
                border_color = WARM_GRAY
                text_color = WARM_GRAY
            
            # Draw button
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, border_color, button_rect, 3)
            
            # Chapter number and title
            chapter_font = pygame.font.Font(None, 32)
            chapter_title = f"Chapter {chapter_num}: {chapter_data['title']}"
            title_text = chapter_font.render(chapter_title, True, text_color)
            self.screen.blit(title_text, (button_rect.x + 20, button_rect.y + 10))
            
            # Description
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(chapter_data['description'], True, text_color)
            self.screen.blit(desc_text, (button_rect.x + 20, button_rect.y + 35))
            
            # Lock icon for locked chapters
            if not is_unlocked:
                lock_font = pygame.font.Font(None, 40)
                lock_text = lock_font.render("🔒", True, WARM_GRAY)
                self.screen.blit(lock_text, (button_rect.right - 50, button_rect.y + 10))
        
        # Back button
        back_button = pygame.Rect(50, 500, 100, 40)
        pygame.draw.rect(self.screen, BURGUNDY, back_button)
        pygame.draw.rect(self.screen, GOLD, back_button, 2)
        back_font = pygame.font.Font(None, 24)
        back_text = back_font.render("Back", True, CREAM)
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 20)
        instructions = [
            "Click on unlocked chapters or press 1-5",
            "Complete chapters to unlock the next ones",
            "ESC to return to main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, CREAM)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 560 + i * 25))
            self.screen.blit(text, text_rect)
    
    def draw_difficulty_select(self):
        # Difficulty selection screen
        self.screen.fill(DARK_BROWN)
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("Choose Your Challenge", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        subtitle_font = pygame.font.Font(None, 28)
        subtitle_text = subtitle_font.render("Select Difficulty Level", True, CREAM)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Difficulty options
        difficulties = [
            ("Easy", "Perfect for beginners - slower enemies, more time to react", DARK_GREEN),
            ("Normal", "Balanced challenge - standard enemy spawn rates", AMBER),
            ("Hard", "For experienced players - faster spawns, tougher enemies", BURGUNDY),
            ("Expert", "Ultimate challenge - maximum chaos and difficulty", NAVY)
        ]
        
        for i, (name, description, color) in enumerate(difficulties):
            y_pos = 200 + i * 100
            
            # Button background
            button_rect = pygame.Rect(400, y_pos, 400, 60)
            if self.selected_difficulty == i:
                pygame.draw.rect(self.screen, color, button_rect)
                pygame.draw.rect(self.screen, GOLD, button_rect, 3)
            else:
                pygame.draw.rect(self.screen, RICH_BROWN, button_rect)
                pygame.draw.rect(self.screen, GOLD, button_rect, 2)
            
            # Difficulty name
            name_font = pygame.font.Font(None, 36)
            name_text = name_font.render(f"{i+1}. {name}", True, WHITE if self.selected_difficulty == i else GOLD)
            name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 20))
            self.screen.blit(name_text, name_rect)
            
            # Description
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(description, True, CREAM)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 40))
            self.screen.blit(desc_text, desc_rect)
        
        # Back button
        back_font = pygame.font.Font(None, 32)
        back_text = back_font.render("ESC - Back to Main Menu", True, GOLD)
        back_rect = back_text.get_rect(center=(100, 620))
        self.screen.blit(back_text, back_rect)
        
        # Instructions
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "Press 1-4 to select difficulty or click on buttons",
            "SPACE or ENTER to confirm and return to main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, CREAM)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 650 + i * 25))
            self.screen.blit(text, text_rect)
    
    def draw_menu_decorations(self):
        # Ornate corner decorations
        pygame.draw.circle(self.screen, GOLD, (100, 100), 12)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 100, 100), 12)
        pygame.draw.circle(self.screen, GOLD, (100, SCREEN_HEIGHT - 100), 12)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 12)
        
        # Books decoration
        for i, x in enumerate([120, 140, 160]):
            pygame.draw.rect(self.screen, [BURGUNDY, NAVY, DARK_GREEN][i], (x, 90, 12, 20))
            pygame.draw.line(self.screen, GOLD, (x, 95), (x + 12, 95), 1)
        
        for i, x in enumerate([SCREEN_WIDTH - 180, SCREEN_WIDTH - 160, SCREEN_WIDTH - 140]):
            pygame.draw.rect(self.screen, [BURGUNDY, NAVY, DARK_GREEN][i], (x, 90, 12, 20))
            pygame.draw.line(self.screen, GOLD, (x, 95), (x + 12, 95), 1)
    
    def draw_library_background(self):
        """Draw the maze-based library layout with enhanced graphics"""
        # Create gradient background
        self.draw_gradient_background()
        
        # Draw each tile with enhanced graphics
        for y in range(self.library_maze.height):
            for x in range(self.library_maze.width):
                tile_type = self.library_maze.tiles[y][x]
                pixel_x = x * TILE_SIZE
                pixel_y = y * TILE_SIZE
                
                self.draw_enhanced_tile(pixel_x, pixel_y, tile_type)
        
        # Add atmospheric lighting and shadows
        self.draw_ambient_lighting()
        self.draw_dynamic_shadows()
    
    def draw_gradient_background(self):
        """Draw a subtle gradient background"""
        for y in range(SCREEN_HEIGHT):
            # Create a subtle gradient from dark brown to slightly lighter
            ratio = y / SCREEN_HEIGHT
            # Ensure all color values are valid integers between 0-255
            r = max(0, min(255, int(DARK_BROWN[0] + (20 * ratio))))
            g = max(0, min(255, int(DARK_BROWN[1] + (15 * ratio))))
            b = max(0, min(255, int(DARK_BROWN[2] + (10 * ratio))))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
    
    def draw_enhanced_tile(self, x, y, tile_type):
        """Draw enhanced tile with better graphics"""
        if tile_type == WALL:
            # Enhanced stone wall with depth
            # Main wall
            pygame.draw.rect(self.screen, (80, 60, 40), (x, y, TILE_SIZE, TILE_SIZE))
            # Highlight
            pygame.draw.line(self.screen, (120, 100, 60), (x, y), (x + TILE_SIZE, y), 2)
            pygame.draw.line(self.screen, (120, 100, 60), (x, y), (x, y + TILE_SIZE), 2)
            # Shadow
            pygame.draw.line(self.screen, (40, 30, 20), (x + TILE_SIZE - 1, y), (x + TILE_SIZE - 1, y + TILE_SIZE), 2)
            pygame.draw.line(self.screen, (40, 30, 20), (x, y + TILE_SIZE - 1), (x + TILE_SIZE, y + TILE_SIZE - 1), 2)
            # Stone texture
            for i in range(3):
                stone_x = x + random.randint(2, TILE_SIZE - 4)
                stone_y = y + random.randint(2, TILE_SIZE - 4)
                pygame.draw.circle(self.screen, (100, 80, 50), (stone_x, stone_y), 1)
                
        elif tile_type == BOOKSHELF:
            # Enhanced bookshelf with 3D effect
            # Main shelf
            pygame.draw.rect(self.screen, (101, 67, 33), (x, y, TILE_SIZE, TILE_SIZE))
            # Books with different colors
            book_colors = [(139, 69, 19), (160, 82, 45), (210, 180, 140), (101, 67, 33)]
            for i in range(4):
                book_x = x + 2 + i * 6
                book_color = book_colors[i % len(book_colors)]
                pygame.draw.rect(self.screen, book_color, (book_x, y + 2, 5, TILE_SIZE - 4))
                # Book spine details
                pygame.draw.line(self.screen, (255, 215, 0), (book_x + 1, y + 4), (book_x + 1, y + TILE_SIZE - 4), 1)
            # Shelf shadow
            pygame.draw.line(self.screen, (60, 40, 20), (x, y + TILE_SIZE - 1), (x + TILE_SIZE, y + TILE_SIZE - 1), 2)
            
        elif tile_type == LAMP:
            # Enhanced lamp with glow effect
            # Lamp post
            pygame.draw.rect(self.screen, (139, 69, 19), (x + 12, y + 8, 6, TILE_SIZE - 8))
            # Lamp head
            pygame.draw.circle(self.screen, (255, 215, 0), (x + 15, y + 8), 8)
            pygame.draw.circle(self.screen, (255, 255, 200), (x + 15, y + 8), 6)
            # Glow effect
            glow_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 215, 0, 50), (10, 10), 10)
            self.screen.blit(glow_surface, (x + 5, y - 2))
            
        else:  # WALKABLE
            # Enhanced walkable area with subtle pattern
            pygame.draw.rect(self.screen, (139, 119, 101), (x, y, TILE_SIZE, TILE_SIZE))
            # Subtle wood grain effect
            for i in range(2):
                grain_y = y + 4 + i * 8
                pygame.draw.line(self.screen, (120, 100, 80), (x + 2, grain_y), (x + TILE_SIZE - 2, grain_y), 1)
    
    def draw_dynamic_shadows(self):
        """Draw dynamic shadows for depth"""
        # Create shadow overlay
        shadow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Add shadows around walls
        for y in range(self.library_maze.height):
            for x in range(self.library_maze.width):
                if self.library_maze.tiles[y][x] == WALL:
                    shadow_x = x * TILE_SIZE + 2
                    shadow_y = y * TILE_SIZE + 2
                    pygame.draw.rect(shadow_surface, (0, 0, 0, 30), 
                                   (shadow_x, shadow_y, TILE_SIZE, TILE_SIZE))
        
        self.screen.blit(shadow_surface, (0, 0))
    
    def draw_tile(self, x, y, tile_type):
        """Draw a single tile with enhanced graphics"""
        if tile_type == WALL:
            # Stone wall with texture
            pygame.draw.rect(self.screen, DIM_GRAY, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(self.screen, WARM_GRAY, (x, y, TILE_SIZE, TILE_SIZE), 2)
            # Add stone texture
            for i in range(3):
                for j in range(3):
                    stone_x = x + i * (TILE_SIZE // 3) + 2
                    stone_y = y + j * (TILE_SIZE // 3) + 2
                    pygame.draw.rect(self.screen, BLACK, (stone_x, stone_y, 2, 2))
        
        elif tile_type == BOOKSHELF:
            # Detailed bookshelf
            pygame.draw.rect(self.screen, RICH_BROWN, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(self.screen, GOLD, (x, y, TILE_SIZE, TILE_SIZE), 2)
            
            # Draw books on shelf
            book_colors = [BURGUNDY, NAVY, DARK_GREEN, (75, 0, 130), (139, 69, 19)]
            book_width = TILE_SIZE // 6
            for i in range(5):
                book_x = x + 2 + i * book_width
                book_y = y + 5
                book_height = TILE_SIZE - 10
                color = book_colors[i % len(book_colors)]
                
                pygame.draw.rect(self.screen, color, (book_x, book_y, book_width - 1, book_height))
                # Book spine details
                pygame.draw.line(self.screen, GOLD, (book_x + 1, book_y + 5), 
                               (book_x + book_width - 2, book_y + 5), 1)
                pygame.draw.line(self.screen, GOLD, (book_x + 1, book_y + 15), 
                               (book_x + book_width - 2, book_y + 15), 1)
        
        elif tile_type == READING_DESK:
            # Ornate reading desk
            pygame.draw.rect(self.screen, RICH_BROWN, (x + 5, y + 15, TILE_SIZE - 10, TILE_SIZE - 20))
            pygame.draw.rect(self.screen, GOLD, (x + 5, y + 15, TILE_SIZE - 10, TILE_SIZE - 20), 2)
            
            # Books on desk
            pygame.draw.rect(self.screen, BURGUNDY, (x + 8, y + 10, 12, 8))
            pygame.draw.rect(self.screen, NAVY, (x + 22, y + 12, 10, 6))
            
            # Quill and inkwell
            pygame.draw.circle(self.screen, BLACK, (x + TILE_SIZE - 8, y + 18), 3)
            pygame.draw.line(self.screen, (139, 69, 19), (x + TILE_SIZE - 8, y + 15), 
                           (x + TILE_SIZE - 5, y + 10), 2)
        
        elif tile_type == LAMP:
            # Ornate lamp with glow
            pygame.draw.circle(self.screen, GOLD, (x + TILE_SIZE//2, y + TILE_SIZE//2), 8)
            pygame.draw.circle(self.screen, AMBER, (x + TILE_SIZE//2, y + TILE_SIZE//2), 12, 2)
            # Lamp base
            pygame.draw.rect(self.screen, RICH_BROWN, (x + TILE_SIZE//2 - 3, y + TILE_SIZE//2 + 8, 6, 8))
            
            # Light glow effect
            for radius in range(20, 5, -2):
                alpha = max(10, 30 - radius)
                glow_surface = pygame.Surface((radius * 2, radius * 2))
                glow_surface.set_alpha(alpha)
                glow_surface.fill(AMBER)
                glow_rect = glow_surface.get_rect(center=(x + TILE_SIZE//2, y + TILE_SIZE//2))
                self.screen.blit(glow_surface, glow_rect)
        
        elif tile_type == CARPET:
            # Rich carpet with pattern
            pygame.draw.rect(self.screen, BURGUNDY, (x, y, TILE_SIZE, TILE_SIZE))
            # Carpet pattern
            pattern_color = (100, 0, 20)  # Darker burgundy
            for i in range(0, TILE_SIZE, 8):
                for j in range(0, TILE_SIZE, 8):
                    if (i + j) % 16 == 0:
                        pygame.draw.rect(self.screen, pattern_color, (x + i, y + j, 4, 4))
        
        elif tile_type == ENTRANCE:
            # Marble entrance
            pygame.draw.rect(self.screen, CREAM, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(self.screen, GOLD, (x, y, TILE_SIZE, TILE_SIZE), 1)
            # Marble veining
            pygame.draw.line(self.screen, WARM_GRAY, (x, y + 10), (x + TILE_SIZE, y + 20), 1)
            pygame.draw.line(self.screen, WARM_GRAY, (x + 5, y), (x + 15, y + TILE_SIZE), 1)
    
    def draw_ambient_lighting(self):
        """Add atmospheric lighting effects"""
        # Find all lamps and create light circles around them
        for y in range(self.library_maze.height):
            for x in range(self.library_maze.width):
                if self.library_maze.tiles[y][x] == LAMP:
                    center_x = x * TILE_SIZE + TILE_SIZE // 2
                    center_y = y * TILE_SIZE + TILE_SIZE // 2
                    
                    # Create larger ambient light
                    for radius in range(60, 20, -5):
                        alpha = max(5, 25 - (radius - 20))
                        light_surface = pygame.Surface((radius * 2, radius * 2))
                        light_surface.set_alpha(alpha)
                        light_surface.fill(AMBER)
                        light_rect = light_surface.get_rect(center=(center_x, center_y))
                        self.screen.blit(light_surface, light_rect)
    
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
        # Draw wave counter and score info
        meter_width = 250
        meter_height = 25
        meter_x = SCREEN_WIDTH - meter_width - 15
        meter_y = 15
        
        # Ornate frame
        pygame.draw.rect(self.screen, RICH_BROWN, (meter_x - 5, meter_y - 5, meter_width + 10, meter_height + 10), 3)
        pygame.draw.rect(self.screen, GOLD, (meter_x - 3, meter_y - 3, meter_width + 6, meter_height + 6), 2)
        
        # Background - dark wood
        pygame.draw.rect(self.screen, DARK_BROWN, (meter_x, meter_y, meter_width, meter_height))
        
        # Wave and enemy count display
        font = pygame.font.Font(None, 20)
        wave_text = font.render(f"Wave: {getattr(self, 'wave_number', 1)} | Enemies: {len(self.enemies)}", True, WHITE)
        text_rect = wave_text.get_rect(center=(meter_x + meter_width//2, meter_y + meter_height//2))
        self.screen.blit(wave_text, text_rect)
        
        # Ornate label
        label_text = font.render("BATTLE STATUS", True, GOLD)
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
        
        if current_time - self.silence_aura_timer < self.silence_aura_duration:
            font = pygame.font.Font(None, 24)
            aura_text = font.render("🔮 AURA OF SILENCE!", True, (100, 149, 237))
            shadow_text = font.render("🔮 AURA OF SILENCE!", True, BLACK)
            self.screen.blit(shadow_text, (12, 112))
            self.screen.blit(aura_text, (10, 110))
        
        if current_time - self.time_freeze_timer < self.time_freeze_duration:
            font = pygame.font.Font(None, 24)
            freeze_text = font.render("⏰ TIME STANDS STILL!", True, (255, 215, 0))
            shadow_text = font.render("⏰ TIME STANDS STILL!", True, BLACK)
            self.screen.blit(shadow_text, (12, 142))
            self.screen.blit(freeze_text, (10, 140))
        
        # Literary quote display
        if self.current_quote and (current_time - self.quote_timer) < 4000:  # Show for 4 seconds
            # Quote text
            quote_font = pygame.font.Font(None, 22)
            quote_lines = self.wrap_text(f'"{self.current_quote}"', quote_font, SCREEN_WIDTH - 120)
            
            # Calculate dynamic height based on number of lines
            line_height = 22
            author_height = 20
            padding = 16  # 8 pixels top and bottom
            quote_height = len(quote_lines) * line_height + author_height + padding
            
            # Quote background - positioned at bottom with dynamic height
            quote_bg = pygame.Rect(50, SCREEN_HEIGHT - quote_height - 20, SCREEN_WIDTH - 100, quote_height)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), quote_bg)
            pygame.draw.rect(self.screen, GOLD, quote_bg, 2)
            
            # Draw quote lines
            y_offset = quote_bg.y + 8
            for line in quote_lines:
                text = quote_font.render(line, True, CREAM)
                self.screen.blit(text, (quote_bg.x + 10, y_offset))
                y_offset += line_height
            
            # Author attribution
            author_font = pygame.font.Font(None, 18)
            author_text = author_font.render(f"— {self.quote_author}", True, GOLD)
            self.screen.blit(author_text, (quote_bg.right - 150, quote_bg.bottom - 20))
        
        # Bibliophile progress (top-right corner)
        progress_font = pygame.font.Font(None, 20)
        title_text = progress_font.render(f"{self.get_bibliophile_title()}", True, GOLD)
        title_rect = title_text.get_rect()
        title_rect.topright = (SCREEN_WIDTH - 15, meter_y + 50)
        self.screen.blit(title_text, title_rect)
        
        collection_font = pygame.font.Font(None, 16)
        collection_text = collection_font.render(f"Genres: {len(self.collected_books)}/9", True, CREAM)
        collection_rect = collection_text.get_rect()
        collection_rect.topright = (SCREEN_WIDTH - 15, meter_y + 72)
        self.screen.blit(collection_text, collection_rect)
        
        authors_text = collection_font.render(f"Authors: {len(self.discovered_authors)}", True, CREAM)
        authors_rect = authors_text.get_rect()
        authors_rect.topright = (SCREEN_WIDTH - 15, meter_y + 90)
        self.screen.blit(authors_text, authors_rect)
        
        # Draw controls with scholarly elegance
        font = pygame.font.Font(None, 16)
        controls_text = font.render("Click/X: Cast Tomes | Space: Silence | Arrows: Move | ESC: Settings | R: Restart", True, CREAM)
        shadow_text = font.render("Click/X: Cast Tomes | Space: Silence | Arrows: Move | ESC: Settings | R: Restart", True, BLACK)
        self.screen.blit(shadow_text, (12, SCREEN_HEIGHT - 28))
        self.screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within given width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    lines.append(word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
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
        game_over_text = font.render("THE LIBRARIAN WAS CAUGHT!", True, BURGUNDY)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        # Add shadow
        shadow_text = font.render("THE LIBRARIAN WAS CAUGHT!", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 2, SCREEN_HEIGHT//2 - 78))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(game_over_text, text_rect)
        
        # Final score with scholarly styling
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Knowledge Preserved: {self.score}", True, CREAM)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        shadow_text = font.render(f"Knowledge Preserved: {self.score}", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 1, SCREEN_HEIGHT//2 - 39))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(score_text, score_rect)
        
        # High score notification
        if self.is_new_high_score:
            font = pygame.font.Font(None, 28)
            high_score_text = font.render("🌟 NEW SCHOLARLY ACHIEVEMENT! 🌟", True, GOLD)
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 5))
            shadow_text = font.render("🌟 NEW SCHOLARLY ACHIEVEMENT! 🌟", True, BLACK)
            shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 1, SCREEN_HEIGHT//2 - 4))
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(high_score_text, high_score_rect)
        
        # Restart instruction with scholarly language
        font = pygame.font.Font(None, 24)
        restart_text = font.render("R: Begin Anew | ESC: Return to Main Hall", True, GOLD)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
        shadow_text = font.render("R: Begin Anew | ESC: Return to Main Hall", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 1, SCREEN_HEIGHT//2 + 31))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(restart_text, restart_rect)
        
        # Decorative elements
        # Corner ornaments
        pygame.draw.circle(self.screen, GOLD, (70, 120), 8)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 70, 120), 8)
        pygame.draw.circle(self.screen, GOLD, (70, SCREEN_HEIGHT - 120), 8)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 70, SCREEN_HEIGHT - 120), 8)
    
    def draw_settings(self):
        # Dark academia settings screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(DARK_BROWN)
        self.screen.blit(overlay, (0, 0))
        
        # Ornate border
        pygame.draw.rect(self.screen, GOLD, (100, 80, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 160), 4)
        pygame.draw.rect(self.screen, RICH_BROWN, (105, 85, SCREEN_WIDTH - 210, SCREEN_HEIGHT - 170), 3)
        
        # Title
        font = pygame.font.Font(None, 48)
        title_text = font.render("SCHOLARLY CONTROLS", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 130))
        shadow_text = font.render("SCHOLARLY CONTROLS", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 2, 132))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Key binding display
        font = pygame.font.Font(None, 24)
        y_offset = 180
        
        key_names = {
            'shoot': 'Cast Tomes',
            'shush': 'Invoke Silence', 
            'move_up': 'Move Up',
            'move_down': 'Move Down',
            'move_left': 'Move Left',
            'move_right': 'Move Right'
        }
        
        instructions = [
            "Press ESC to return to game",
            "Press number keys to rebind:",
            "",
            "1. Cast Tomes: " + pygame.key.name(self.key_bindings['shoot']).upper(),
            "2. Invoke Silence: " + pygame.key.name(self.key_bindings['shush']).upper(),
            "3. Move Up: " + pygame.key.name(self.key_bindings['move_up']).upper(),
            "4. Move Down: " + pygame.key.name(self.key_bindings['move_down']).upper(),
            "5. Move Left: " + pygame.key.name(self.key_bindings['move_left']).upper(),
            "6. Move Right: " + pygame.key.name(self.key_bindings['move_right']).upper(),
        ]
        
        if self.setting_key:
            instructions.append("")
            instructions.append(f"Press any key to bind to {key_names.get(self.setting_key, self.setting_key)}...")
        
        for i, instruction in enumerate(instructions):
            color = AMBER if instruction.startswith(("1.", "2.", "3.", "4.", "5.", "6.")) else CREAM
            if self.setting_key and instruction.endswith("..."):
                color = GOLD
            
            text = font.render(instruction, True, color)
            shadow = font.render(instruction, True, BLACK)
            self.screen.blit(shadow, (SCREEN_WIDTH//2 - text.get_width()//2 + 1, y_offset + i * 30 + 1))
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_offset + i * 30))
        
        # Decorative elements
        pygame.draw.circle(self.screen, GOLD, (120, 100), 6)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 120, 100), 6)
        pygame.draw.circle(self.screen, GOLD, (120, SCREEN_HEIGHT - 100), 6)
        pygame.draw.circle(self.screen, GOLD, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 100), 6)
    
    def restart_game(self):
        self.score = 0
        self.is_new_high_score = False
        self.reset_game()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

class Librarian:
    def __init__(self, maze, sprite_manager=None):
        self.x = TILE_SIZE * 2  # Start in entrance area
        self.y = TILE_SIZE * 2
        self.width = 30
        self.height = 35
        self.speed = 3
        self.maze = maze
        self.sprite_manager = sprite_manager
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.facing_direction = 'down'  # up, down, left, right
        self.is_moving = False
    
    def update(self, key_bindings):
        keys = pygame.key.get_pressed()
        old_x, old_y = self.x, self.y
        new_x, new_y = self.x, self.y
        
        self.is_moving = False
        
        if keys[key_bindings['move_up']]:
            new_y -= self.speed
            self.facing_direction = 'up'
            self.is_moving = True
        if keys[key_bindings['move_down']]:
            new_y += self.speed
            self.facing_direction = 'down'
            self.is_moving = True
        if keys[key_bindings['move_left']]:
            new_x -= self.speed
            self.facing_direction = 'left'
            self.is_moving = True
        if keys[key_bindings['move_right']]:
            new_x += self.speed
            self.facing_direction = 'right'
            self.is_moving = True
        
        # Check collision with maze walls
        if self.can_move_to(new_x, new_y):
            self.x, self.y = new_x, new_y
        elif self.can_move_to(new_x, old_y):  # Try horizontal movement only
            self.x = new_x
        elif self.can_move_to(old_x, new_y):  # Try vertical movement only
            self.y = new_y
        
        # Update animation
        if self.is_moving:
            self.animation_timer += 1
            if self.animation_timer >= 10:  # Change frame every 10 ticks
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0
        else:
            self.animation_frame = 0
    
    def can_move_to(self, x, y):
        """Check if the librarian can move to the given position"""
        # Check all four corners of the librarian
        corners = [
            (x, y),                           # Top-left
            (x + self.width, y),              # Top-right
            (x, y + self.height),             # Bottom-left
            (x + self.width, y + self.height) # Bottom-right
        ]
        
        for corner_x, corner_y in corners:
            if not self.maze.is_walkable(corner_x, corner_y):
                return False
        
        return True
    
    def draw(self, screen):
        # Try to use sprite first, fall back to procedural graphics
        if self.sprite_manager and self.sprite_manager.has_sprites():
            self.draw_sprite(screen)
        else:
            self.draw_procedural(screen)
    
    def draw_sprite(self, screen):
        """Draw using sprite images"""
        # Determine which sprite to use based on facing direction and movement
        if self.is_moving:
            direction = self.facing_direction
        else:
            direction = "idle"
        
        sprite = self.sprite_manager.get_current_character_sprite(direction)
        
        # Fall back to idle sprite if specific direction not found
        if not sprite:
            sprite = self.sprite_manager.get_current_character_sprite("idle")
        
        # Fall back to down sprite if idle not found
        if not sprite:
            sprite = self.sprite_manager.get_current_character_sprite("down")
        
        if sprite:
            # Add walking animation by slightly offsetting the sprite
            offset_y = 0
            if self.is_moving:
                offset_y = int(2 * math.sin(self.animation_frame * math.pi / 2))
            
            # Draw shadow
            shadow_y = self.y + self.height - 2
            pygame.draw.ellipse(screen, (0, 0, 0, 80), (self.x + 2, shadow_y, self.width - 4, 6))
            
            # Draw the sprite
            screen.blit(sprite, (self.x, self.y + offset_y))
            
            # Add power-up aura effects
            self.draw_power_up_effects(screen)
        else:
            # Fall back to procedural drawing
            self.draw_procedural(screen)
    
    def draw_procedural(self, screen):
        """Draw using procedural graphics (enhanced cute version)"""
        # Ultra-cute enhanced librarian with better proportions and details
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Animation offset for walking
        walk_offset = 0
        bounce_offset = 0
        if self.is_moving:
            walk_offset = 1.5 * math.sin(self.animation_frame * math.pi / 2)
            bounce_offset = 1 * abs(math.sin(self.animation_frame * math.pi / 2))
        
        # Cute shadow with rounded edges
        shadow_y = self.y + self.height - 1
        pygame.draw.ellipse(screen, (0, 0, 0, 80), (self.x + 2, shadow_y, self.width - 4, 6))
        
        # Body position with cute bouncing
        body_y = center_y - 2 + walk_offset - bounce_offset
        
        # Cute legs with walking animation
        leg_offset = 0
        if self.is_moving:
            leg_offset = 2 * math.sin(self.animation_frame * math.pi)
        
        # Adorable rounded legs
        leg_y = body_y + 8
        pygame.draw.circle(screen, NAVY, (center_x - 3 + int(leg_offset), leg_y), 4)  # Left leg
        pygame.draw.circle(screen, NAVY, (center_x + 3 - int(leg_offset), leg_y), 4)  # Right leg
        
        # Cute shoes
        pygame.draw.ellipse(screen, BLACK, (center_x - 5 + int(leg_offset), leg_y + 3, 4, 6))
        pygame.draw.ellipse(screen, BLACK, (center_x + 1 - int(leg_offset), leg_y + 3, 4, 6))
        
        # Adorable rounded torso with vest
        torso_y = body_y - 8
        # Main robe
        pygame.draw.ellipse(screen, RICH_BROWN, (center_x - 10, torso_y, 20, 16))
        # Cute vest with buttons
        pygame.draw.ellipse(screen, DARK_BROWN, (center_x - 8, torso_y + 2, 16, 12))
        # Golden buttons
        pygame.draw.circle(screen, GOLD, (center_x, torso_y + 5), 1)
        pygame.draw.circle(screen, GOLD, (center_x, torso_y + 8), 1)
        pygame.draw.circle(screen, GOLD, (center_x, torso_y + 11), 1)
        
        # Cute arms with proper positioning
        arm_y = torso_y + 3
        if self.facing_direction == 'left':
            # Left arm forward, right arm back
            pygame.draw.circle(screen, (245, 222, 179), (center_x - 11, arm_y), 3)
            pygame.draw.circle(screen, (245, 222, 179), (center_x + 9, arm_y + 1), 3)
        elif self.facing_direction == 'right':
            # Right arm forward, left arm back  
            pygame.draw.circle(screen, (245, 222, 179), (center_x - 9, arm_y + 1), 3)
            pygame.draw.circle(screen, (245, 222, 179), (center_x + 11, arm_y), 3)
        else:
            # Both arms at sides
            pygame.draw.circle(screen, (245, 222, 179), (center_x - 10, arm_y), 3)
            pygame.draw.circle(screen, (245, 222, 179), (center_x + 10, arm_y), 3)
        
        # Adorable oversized head
        head_y = torso_y - 8 + bounce_offset * 0.5
        pygame.draw.circle(screen, (255, 228, 196), (center_x, int(head_y)), 10)  # Slightly peachy skin
        
        # Cute fluffy hair with highlights
        pygame.draw.circle(screen, (139, 139, 139), (center_x, int(head_y - 2)), 9)  # Base hair
        pygame.draw.circle(screen, (169, 169, 169), (center_x - 2, int(head_y - 4)), 4)  # Hair highlight
        pygame.draw.circle(screen, (169, 169, 169), (center_x + 3, int(head_y - 3)), 3)  # Hair highlight
        
        # Stylish round glasses with reflection
        pygame.draw.circle(screen, GOLD, (center_x - 4, int(head_y)), 5, 2)
        pygame.draw.circle(screen, GOLD, (center_x + 4, int(head_y)), 5, 2)
        pygame.draw.line(screen, GOLD, (center_x - 1, int(head_y)), (center_x + 1, int(head_y)), 2)
        # Lens reflections
        pygame.draw.circle(screen, WHITE, (center_x - 5, int(head_y - 1)), 2)
        pygame.draw.circle(screen, WHITE, (center_x + 3, int(head_y - 1)), 2)
        
        # Large expressive eyes (direction-aware)
        eye_offset_x = 0
        eye_offset_y = 0
        if self.facing_direction == 'left':
            eye_offset_x = -1
        elif self.facing_direction == 'right':
            eye_offset_x = 1
        elif self.facing_direction == 'up':
            eye_offset_y = -1
        elif self.facing_direction == 'down':
            eye_offset_y = 1
        
        # Eye whites
        pygame.draw.ellipse(screen, WHITE, (center_x - 6 + eye_offset_x, int(head_y) - 1 + eye_offset_y, 4, 3))
        pygame.draw.ellipse(screen, WHITE, (center_x + 2 + eye_offset_x, int(head_y) - 1 + eye_offset_y, 4, 3))
        # Eye pupils
        pygame.draw.circle(screen, BLACK, (center_x - 4 + eye_offset_x, int(head_y) + eye_offset_y), 2)
        pygame.draw.circle(screen, BLACK, (center_x + 4 + eye_offset_x, int(head_y) + eye_offset_y), 2)
        # Eye shine
        pygame.draw.circle(screen, WHITE, (center_x - 3 + eye_offset_x, int(head_y) - 1 + eye_offset_y), 1)
        pygame.draw.circle(screen, WHITE, (center_x + 5 + eye_offset_x, int(head_y) - 1 + eye_offset_y), 1)
        
        # Cute rosy cheeks
        pygame.draw.circle(screen, (255, 182, 193), (center_x - 7, int(head_y) + 2), 2)
        pygame.draw.circle(screen, (255, 182, 193), (center_x + 7, int(head_y) + 2), 2)
        
        # Small cute smile
        pygame.draw.arc(screen, BLACK, (center_x - 2, int(head_y) + 3, 4, 3), 0, math.pi, 1)
        
        # Adorable book with sparkles (changes position based on direction)
        book_x = center_x + 12
        book_y = arm_y - 3
        if self.facing_direction == 'left':
            book_x = center_x - 16
        
        # Magical book with glow
        pygame.draw.rect(screen, BURGUNDY, (book_x, book_y, 10, 8))
        pygame.draw.rect(screen, GOLD, (book_x, book_y, 10, 8), 1)
        pygame.draw.line(screen, GOLD, (book_x + 2, book_y + 2), (book_x + 8, book_y + 2), 1)
        pygame.draw.line(screen, GOLD, (book_x + 2, book_y + 4), (book_x + 8, book_y + 4), 1)
        pygame.draw.line(screen, GOLD, (book_x + 2, book_y + 6), (book_x + 8, book_y + 6), 1)
        
        # Sparkles around the book
        sparkle_offset = math.sin(pygame.time.get_ticks() * 0.01) * 2
        pygame.draw.circle(screen, GOLD, (book_x - 3, book_y + int(sparkle_offset)), 1)
        pygame.draw.circle(screen, GOLD, (book_x + 13, book_y + 4 - int(sparkle_offset)), 1)
        
        # Power-up aura effects
        self.draw_power_up_effects(screen)
    
    def draw_power_up_effects(self, screen):
        """Draw power-up aura effects around the character"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        current_time = pygame.time.get_ticks()
        
        # Note: We would need a reference to the game to check power-up timers
        # For now, this is a placeholder - we'll need to pass game reference or timers

class NoisyMonster:
    def __init__(self, monster_type=None, maze=None):
        self.maze = maze
        self.width = 25
        self.height = 25
        self.monster_type = monster_type or random.choice([
            "student", "animal", "ghost", "chaos_lord", 
            "literary_villain", "book_worm", "noise_demon",
            "boss_monster", "swarm_enemy", "teleporting_ghost", 
            "shielded_knight", "exploding_bomb"
        ])
        self.health = 1  # Most enemies die in one hit
        
        # Find a valid spawn position near the edges
        self.find_spawn_position()
        
        # Different colors and properties for different monster types
        if self.monster_type == "student":
            self.color = (255, 200, 200)  # Light pink
            self.noise_value = random.randint(8, 12)
            self.speed = random.uniform(2.0, 3.0)  # Faster
        elif self.monster_type == "animal":
            self.color = (200, 150, 100)  # Brown
            self.noise_value = random.randint(5, 10)
            self.speed = random.uniform(1.5, 2.5)  # Faster
        elif self.monster_type == "ghost":
            self.color = (200, 200, 255)  # Light blue
            self.noise_value = random.randint(10, 15)
            self.speed = random.uniform(2.5, 3.5)  # Much faster
        elif self.monster_type == "chaos_lord":
            self.color = (255, 100, 100)  # Dark red
            self.noise_value = random.randint(20, 25)
            self.speed = random.uniform(0.5, 1.0)
            self.health = 3  # Takes 3 hits
            self.width = 35
            self.height = 35
        elif self.monster_type == "literary_villain":
            self.color = (75, 0, 130)  # Dark purple
            self.noise_value = random.randint(15, 20)
            self.speed = random.uniform(0.8, 1.3)
            self.health = 2  # Tougher than normal enemies
            self.width = 30
            self.height = 30
        elif self.monster_type == "book_worm":
            self.color = (139, 69, 19)  # Saddle brown
            self.noise_value = random.randint(6, 12)
            self.speed = random.uniform(3.0, 4.0)  # Very fast
            self.health = 1
            self.width = 20
            self.height = 20
        elif self.monster_type == "noise_demon":
            self.color = (255, 0, 255)  # Magenta
            self.noise_value = random.randint(25, 30)
            self.speed = random.uniform(0.3, 0.8)
            self.health = 4  # Very tough
            self.width = 40
            self.height = 40
        elif self.monster_type == "boss_monster":
            self.color = (139, 0, 0)  # Dark red
            self.noise_value = random.randint(30, 40)
            self.speed = random.uniform(0.5, 1.0)
            self.health = 8  # Boss health
            self.width = 50
            self.height = 50
        elif self.monster_type == "swarm_enemy":
            self.color = (255, 165, 0)  # Orange
            self.noise_value = random.randint(3, 6)
            self.speed = random.uniform(4.0, 5.0)  # Very fast
            self.health = 1
            self.width = 15
            self.height = 15
        elif self.monster_type == "teleporting_ghost":
            self.color = (128, 0, 128)  # Purple
            self.noise_value = random.randint(12, 18)
            self.speed = random.uniform(1.0, 2.0)
            self.health = 2
            self.width = 25
            self.height = 25
            self.teleport_timer = 0
            self.teleport_delay = 3000  # 3 seconds
        elif self.monster_type == "shielded_knight":
            self.color = (70, 70, 70)  # Dark gray
            self.noise_value = random.randint(10, 15)
            self.speed = random.uniform(0.8, 1.2)
            self.health = 3
            self.shield_health = 2  # Shield takes 2 hits
            self.width = 30
            self.height = 30
        elif self.monster_type == "exploding_bomb":
            self.color = (255, 69, 0)  # Red-orange
            self.noise_value = random.randint(15, 20)
            self.speed = random.uniform(1.5, 2.5)
            self.health = 1
            self.width = 20
            self.height = 20
            self.explosion_timer = 0
            self.explosion_delay = 5000  # 5 seconds before explosion
        else:
            # Default fallback for any unknown monster types
            self.color = (128, 128, 128)  # Gray
            self.noise_value = random.randint(8, 12)
            self.speed = random.uniform(1.0, 1.5)
            self.health = 1
        
        # AI pathfinding - will be set to chase player
        self.target_x = SCREEN_WIDTH // 2  # Start by heading to center
        self.target_y = SCREEN_HEIGHT // 2
        self.path_update_timer = 0
        self.player_x = 0  # Player position for chasing
        self.player_y = 0
    
    def find_spawn_position(self):
        """Find a valid spawn position in walkable areas"""
        attempts = 0
        while attempts < 50:  # Prevent infinite loop
            # Try to spawn near the edges of walkable areas
            if random.choice([True, False]):
                # Spawn from right side
                self.x = SCREEN_WIDTH - 50
                self.y = random.randint(TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE - self.height)
            else:
                # Spawn from bottom
                self.x = random.randint(TILE_SIZE, SCREEN_WIDTH - TILE_SIZE - self.width)
                self.y = SCREEN_HEIGHT - 50
            
            # Check if spawn position is valid
            if self.maze and self.can_move_to(self.x, self.y):
                break
            elif not self.maze:  # Fallback if no maze
                self.x = SCREEN_WIDTH + 50
                self.y = random.randint(50, SCREEN_HEIGHT - 50)
                break
            
            attempts += 1
        
        if attempts >= 50:  # Fallback spawn
            self.x = SCREEN_WIDTH - TILE_SIZE
            self.y = SCREEN_HEIGHT // 2
    
    def can_move_to(self, x, y):
        """Check if the enemy can move to the given position"""
        if not self.maze:
            return True
            
        # Check all four corners of the enemy
        corners = [
            (x, y),
            (x + self.width, y),
            (x, y + self.height),
            (x + self.width, y + self.height)
        ]
        
        for corner_x, corner_y in corners:
            if not self.maze.is_walkable(corner_x, corner_y):
                return False
        
        return True
    
    def can_move_to_simple(self, x, y):
        """Simplified collision detection - only avoid walls, allow movement through most areas"""
        if not self.maze:
            return True
            
        # Check if position is within screen bounds
        if x < 0 or x > SCREEN_WIDTH or y < 0 or y > SCREEN_HEIGHT:
            return False
            
        # Only check for walls, allow movement through other areas
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        
        if tile_x < 0 or tile_x >= self.maze.width or tile_y < 0 or tile_y >= self.maze.height:
            return False
            
        tile_type = self.maze.tiles[tile_y][tile_x]
        # Only block movement on walls, allow everything else
        return tile_type != WALL
    
    def update(self):
        # Handle special enemy behaviors
        current_time = pygame.time.get_ticks()
        
        # Teleporting ghost special ability
        if self.monster_type == "teleporting_ghost":
            self.teleport_timer += 16  # Approximate frame time
            if self.teleport_timer >= self.teleport_delay:
                # Teleport to a random position near player
                if hasattr(self, 'player_x') and hasattr(self, 'player_y'):
                    offset_x = random.randint(-100, 100)
                    offset_y = random.randint(-100, 100)
                    self.x = self.player_x + offset_x
                    self.y = self.player_y + offset_y
                    self.teleport_timer = 0
        
        # Exploding bomb special ability
        elif self.monster_type == "exploding_bomb":
            self.explosion_timer += 16
            if self.explosion_timer >= self.explosion_delay:
                # Explode - damage nearby enemies and player
                # This will be handled in the game's collision detection
                self.health = 0  # Mark for destruction
                return
        
        # Simple direct movement towards player
        self.path_update_timer += 1
        
        # Update target frequently (chase player)
        if self.path_update_timer % 5 == 0:  # Every 5 frames (very responsive)
            # Try to get player position for chasing
            if hasattr(self, 'player_x') and hasattr(self, 'player_y') and self.player_x != 0 and self.player_y != 0:
                self.target_x = self.player_x
                self.target_y = self.player_y
            else:
                # Fallback to center if no player position available
                self.target_x = SCREEN_WIDTH // 2
                self.target_y = SCREEN_HEIGHT // 2
        
        # Move towards target with simplified collision detection
        old_x, old_y = self.x, self.y
        
        # Calculate direction to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 2:  # Don't jitter when very close
            # Normalize and apply speed
            if distance > 0:  # Avoid division by zero
                move_x = (dx / distance) * self.speed
                move_y = (dy / distance) * self.speed
            else:
                move_x = 0
                move_y = 0
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            # Simplified movement - just move towards player, ignore most obstacles
            # Only avoid walls, but allow movement through other areas
            if self.can_move_to_simple(new_x, new_y):
                self.x, self.y = new_x, new_y
            elif self.can_move_to_simple(new_x, old_y):  # Try horizontal only
                self.x = new_x
            elif self.can_move_to_simple(old_x, new_y):  # Try vertical only
                self.y = new_y
            else:
                # If completely stuck, move anyway (enemies are aggressive!)
                self.x = new_x
                self.y = new_y
    
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
            
        elif self.monster_type == "ghost":
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
            
        elif self.monster_type == "literary_villain":
            # Literary villain - dark academic antagonist
            # Main body - dark purple robe
            pygame.draw.ellipse(screen, self.color, (self.x - 12, self.y - 5, 24, 30))
            
            # Head - pale and menacing
            pygame.draw.circle(screen, (220, 220, 220), (int(self.x), int(self.y - 8)), 10)
            
            # Dark hood
            pygame.draw.arc(screen, (50, 0, 80), (self.x - 12, self.y - 20, 24, 20), 0, 3.14159, 3)
            
            # Glowing red eyes
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x - 4), int(self.y - 8)), 3)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + 4), int(self.y - 8)), 3)
            
            # Evil grimoire
            pygame.draw.rect(screen, (100, 0, 0), (self.x - 15, self.y - 2, 8, 12))
            pygame.draw.line(screen, (255, 215, 0), (self.x - 15, self.y + 2), (self.x - 7, self.y + 2), 2)
            
            # Health bar for tougher enemy
            if self.health < 2:
                health_bar_width = 25
                health_bar_height = 3
                health_x = self.x - health_bar_width // 2
                health_y = self.y - 25
                
                pygame.draw.rect(screen, BLACK, (health_x, health_y, health_bar_width, health_bar_height))
                health_width = (self.health / 2) * health_bar_width
                pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width, health_bar_height))
            
        elif self.monster_type == "boss_monster":
            # Massive boss enemy - ultimate challenge
            # Main body - huge and menacing
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 25)
            pygame.draw.circle(screen, (100, 0, 0), (int(self.x), int(self.y)), 25, 4)
            
            # Multiple horns
            for i, (horn_x, horn_y) in enumerate([(-20, -20), (20, -20), (-10, -25), (10, -25)]):
                pygame.draw.polygon(screen, (50, 0, 0), [
                    (self.x + horn_x, self.y + horn_y),
                    (self.x + horn_x - 3, self.y + horn_y - 8),
                    (self.x + horn_x + 3, self.y + horn_y - 8)
                ])
            
            # Glowing eyes
            for i, (eye_x, eye_y) in enumerate([(-12, -8), (12, -8), (-6, 2), (6, 2)]):
                pygame.draw.circle(screen, (255, 0, 0), (int(self.x + eye_x), int(self.y + eye_y)), 5)
                pygame.draw.circle(screen, (255, 100, 100), (int(self.x + eye_x), int(self.y + eye_y)), 2)
            
            # Health bar
            health_bar_width = 40
            health_bar_height = 5
            health_x = self.x - health_bar_width // 2
            health_y = self.y - 40
            pygame.draw.rect(screen, BLACK, (health_x, health_y, health_bar_width, health_bar_height))
            health_width = (self.health / 8) * health_bar_width
            pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width, health_bar_height))
            
        elif self.monster_type == "swarm_enemy":
            # Small, fast swarm enemy
            # Body - small and agile
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 8)
            # Wings
            pygame.draw.ellipse(screen, (255, 200, 0), (self.x - 12, self.y - 4, 8, 4))
            pygame.draw.ellipse(screen, (255, 200, 0), (self.x + 4, self.y - 4, 8, 4))
            # Eyes
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x - 2), int(self.y - 2)), 2)
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x + 2), int(self.y - 2)), 2)
            
        elif self.monster_type == "teleporting_ghost":
            # Ghost that can teleport
            # Main body - wavy and ethereal
            points = [
                (self.x - 10, self.y - 6),
                (self.x + 10, self.y - 6),
                (self.x + 8, self.y + 2),
                (self.x + 4, self.y + 6),
                (self.x, self.y + 3),
                (self.x - 4, self.y + 6),
                (self.x - 8, self.y + 2)
            ]
            pygame.draw.polygon(screen, self.color, points)
            # Teleportation sparkles
            for i in range(3):
                sparkle_x = self.x + random.randint(-15, 15)
                sparkle_y = self.y + random.randint(-15, 15)
                pygame.draw.circle(screen, (255, 255, 255), (int(sparkle_x), int(sparkle_y)), 1)
            # Glowing purple eyes
            pygame.draw.circle(screen, (255, 0, 255), (int(self.x - 3), int(self.y - 3)), 2)
            pygame.draw.circle(screen, (255, 0, 255), (int(self.x + 3), int(self.y - 3)), 2)
            
        elif self.monster_type == "shielded_knight":
            # Knight with protective shield
            # Body - armored
            pygame.draw.rect(screen, self.color, (self.x - 10, self.y - 8, 20, 16))
            # Shield
            if hasattr(self, 'shield_health') and self.shield_health > 0:
                pygame.draw.circle(screen, (200, 200, 255), (int(self.x - 15), int(self.y)), 8)
                pygame.draw.circle(screen, (100, 100, 255), (int(self.x - 15), int(self.y)), 8, 2)
            # Helmet
            pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y - 8)), 8)
            # Eyes
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x - 2), int(self.y - 8)), 2)
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x + 2), int(self.y - 8)), 2)
            
        elif self.monster_type == "exploding_bomb":
            # Bomb that explodes after time
            # Main body - bomb shape
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)
            # Fuse
            pygame.draw.line(screen, (255, 255, 0), (self.x, self.y - 10), (self.x, self.y - 15), 2)
            # Warning light
            if hasattr(self, 'explosion_timer'):
                if (self.explosion_timer // 500) % 2:  # Blink every 500ms
                    pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 3)
            # Danger symbol
            pygame.draw.line(screen, (255, 255, 255), (self.x - 3, self.y - 3), (self.x + 3, self.y + 3), 2)
            pygame.draw.line(screen, (255, 255, 255), (self.x + 3, self.y - 3), (self.x - 3, self.y + 3), 2)
            
        else:  # chaos_lord
            # Powerful boss enemy - larger and more menacing
            # Main body - dark and imposing
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 20)
            pygame.draw.circle(screen, (150, 0, 0), (int(self.x), int(self.y)), 20, 3)
            
            # Crown of chaos
            crown_points = [
                (self.x - 15, self.y - 15),
                (self.x - 10, self.y - 25),
                (self.x - 5, self.y - 20),
                (self.x, self.y - 30),
                (self.x + 5, self.y - 20),
                (self.x + 10, self.y - 25),
                (self.x + 15, self.y - 15)
            ]
            pygame.draw.polygon(screen, (100, 0, 0), crown_points)
            
            # Multiple glowing eyes
            for i, (eye_x, eye_y) in enumerate([(-8, -8), (8, -8), (-4, 0), (4, 0)]):
                pygame.draw.circle(screen, (255, 50, 50), (int(self.x + eye_x), int(self.y + eye_y)), 4)
                pygame.draw.circle(screen, (255, 150, 150), (int(self.x + eye_x), int(self.y + eye_y)), 2)
            
            # Health indicator
            health_bar_width = 30
            health_bar_height = 4
            health_x = self.x - health_bar_width // 2
            health_y = self.y - 35
            
            # Background
            pygame.draw.rect(screen, BLACK, (health_x, health_y, health_bar_width, health_bar_height))
            # Health
            health_width = (self.health / 3) * health_bar_width
            pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width, health_bar_height))

class Book:
    def __init__(self, x, y, target_pos, is_mega=False, genre=None, book_type=None):
        self.x = x
        self.y = y
        self.is_mega = is_mega
        
        # Book type determines base properties
        self.book_type = book_type or random.choice(["paperback", "hardcover", "encyclopedia", "magical_tome"])
        self.set_book_type_properties()
        
        # Adjust size for mega books
        if is_mega:
            self.width = int(self.width * 1.5)
            self.height = int(self.height * 1.5)
            self.speed *= 1.2
            self.damage *= 2
        
        # Literary genres with special properties
        if genre:
            self.genre = genre
        else:
            self.genre = random.choice([
                "classic", "mystery", "fantasy", "romance", "horror", 
                "poetry", "philosophy", "history", "science"
            ])
        
        # Genre-specific properties
        self.set_genre_properties()
        
        if is_mega:
            self.color = (255, 165, 0)  # Golden mega book
        else:
            self.color = self.genre_color
        
        # Calculate direction towards target
        dx = target_pos[0] - x
        dy = target_pos[1] - y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:  # Avoid division by zero
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx = 0
            self.dy = 0
    
    def set_genre_properties(self):
        """Set genre-specific properties and famous quotes"""
        genre_data = {
            "classic": {
                "color": (139, 69, 19),  # Brown leather
                "damage": 2,
                "effect": "wisdom",
                "quotes": [
                    "It was the best of times, it was the worst of times",
                    "To be or not to be, that is the question",
                    "All happy families are alike",
                    "It is a truth universally acknowledged"
                ],
                "authors": ["Dickens", "Shakespeare", "Tolstoy", "Austen"]
            },
            "mystery": {
                "color": (47, 79, 79),  # Dark slate gray
                "damage": 3,
                "effect": "investigation",
                "quotes": [
                    "Elementary, my dear Watson",
                    "The butler did it",
                    "Ten little Indians",
                    "Murder on the Orient Express"
                ],
                "authors": ["Doyle", "Christie", "Poe", "Chandler"]
            },
            "fantasy": {
                "color": (138, 43, 226),  # Blue violet
                "damage": 4,
                "effect": "magic",
                "quotes": [
                    "You shall not pass!",
                    "Winter is coming",
                    "A wizard is never late",
                    "Not all those who wander are lost"
                ],
                "authors": ["Tolkien", "Martin", "Rowling", "Lewis"]
            },
            "romance": {
                "color": (255, 20, 147),  # Deep pink
                "damage": 1,
                "effect": "charm",
                "quotes": [
                    "Reader, I married him",
                    "You have bewitched me, body and soul",
                    "Whatever our souls are made of",
                    "I am no bird; and no net ensnares me"
                ],
                "authors": ["Brontë", "Austen", "E. Brontë", "C. Brontë"]
            },
            "horror": {
                "color": (139, 0, 0),  # Dark red
                "damage": 5,
                "effect": "fear",
                "quotes": [
                    "Here's Johnny!",
                    "All work and no play...",
                    "The call is coming from inside the house",
                    "We all float down here"
                ],
                "authors": ["King", "Poe", "Lovecraft", "Shelley"]
            },
            "poetry": {
                "color": (255, 215, 0),  # Gold
                "damage": 1,
                "effect": "inspiration",
                "quotes": [
                    "Two roads diverged in a yellow wood",
                    "Shall I compare thee to a summer's day?",
                    "Because I could not stop for Death",
                    "I took the one less traveled by"
                ],
                "authors": ["Frost", "Shakespeare", "Dickinson", "Whitman"]
            },
            "philosophy": {
                "color": (75, 0, 130),  # Indigo
                "damage": 2,
                "effect": "enlightenment",
                "quotes": [
                    "I think, therefore I am",
                    "The unexamined life is not worth living",
                    "God is dead",
                    "Man is condemned to be free"
                ],
                "authors": ["Descartes", "Socrates", "Nietzsche", "Sartre"]
            },
            "history": {
                "color": (160, 82, 45),  # Saddle brown
                "damage": 3,
                "effect": "knowledge",
                "quotes": [
                    "Those who cannot remember the past...",
                    "History is written by the victors",
                    "The only thing we learn from history...",
                    "A people without history..."
                ],
                "authors": ["Santayana", "Churchill", "Hegel", "Baldwin"]
            },
            "science": {
                "color": (0, 100, 0),  # Dark green
                "damage": 3,
                "effect": "logic",
                "quotes": [
                    "The important thing is not to stop questioning",
                    "Science is a way of thinking",
                    "Any sufficiently advanced technology...",
                    "The cosmos is within us"
                ],
                "authors": ["Einstein", "Sagan", "Clarke", "Hawking"]
            }
        }
        
        data = genre_data.get(self.genre, genre_data["classic"])
        self.genre_color = data["color"]
        self.damage = data["damage"]
        self.effect = data["effect"]
        self.quote = random.choice(data["quotes"])
        self.author = random.choice(data["authors"])
    
    def set_book_type_properties(self):
        """Set properties based on book type"""
        book_type_data = {
            "paperback": {
                "width": 15,
                "height": 20,
                "speed": 10,
                "damage": 1,
                "color": (200, 150, 100),  # Light brown
                "description": "Fast and light"
            },
            "hardcover": {
                "width": 18,
                "height": 22,
                "speed": 7,
                "damage": 2,
                "color": (139, 69, 19),  # Saddle brown
                "description": "Heavy and powerful"
            },
            "encyclopedia": {
                "width": 25,
                "height": 30,
                "speed": 4,
                "damage": 4,
                "color": (75, 0, 130),  # Indigo
                "description": "Massive damage, slow"
            },
            "magical_tome": {
                "width": 20,
                "height": 25,
                "speed": 8,
                "damage": 2,
                "color": (128, 0, 128),  # Purple
                "description": "Special effects"
            }
        }
        
        data = book_type_data.get(self.book_type, book_type_data["paperback"])
        self.width = data["width"]
        self.height = data["height"]
        self.speed = data["speed"]
        self.damage = data["damage"]
        self.book_color = data["color"]
        self.description = data["description"]
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
    
    def draw(self, screen):
        # Draw book with type-specific styling
        if self.is_mega:
            # Mega book - enhanced version of book type
            pygame.draw.rect(screen, self.book_color, (self.x, self.y, self.width, self.height))
            # Gold binding for mega books
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
            # Book type and genre styling
            # Use book type color as base, genre color for accents
            pygame.draw.rect(screen, self.book_color, (self.x, self.y, self.width, self.height))
            # Add genre color border
            pygame.draw.rect(screen, self.genre_color, (self.x, self.y, self.width, self.height), 1)
            
            # Genre-specific decorations
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            if self.genre == "fantasy":
                # Magical sparkles
                pygame.draw.circle(screen, GOLD, (center_x - 3, center_y - 3), 1)
                pygame.draw.circle(screen, GOLD, (center_x + 3, center_y + 3), 1)
            elif self.genre == "mystery":
                # Magnifying glass symbol
                pygame.draw.circle(screen, GOLD, (center_x, center_y), 3, 1)
                pygame.draw.line(screen, GOLD, (center_x + 2, center_y + 2), (center_x + 4, center_y + 4), 1)
            elif self.genre == "horror":
                # Ominous symbol
                pygame.draw.line(screen, GOLD, (center_x - 2, center_y - 2), (center_x + 2, center_y + 2), 1)
                pygame.draw.line(screen, GOLD, (center_x + 2, center_y - 2), (center_x - 2, center_y + 2), 1)
            elif self.genre == "romance":
                # Heart symbol
                pygame.draw.circle(screen, GOLD, (center_x - 1, center_y), 2, 1)
                pygame.draw.circle(screen, GOLD, (center_x + 1, center_y), 2, 1)
            elif self.genre == "poetry":
                # Quill symbol
                pygame.draw.line(screen, GOLD, (center_x - 2, center_y + 2), (center_x + 2, center_y - 2), 1)
            elif self.genre == "philosophy":
                # Yin-yang like symbol
                pygame.draw.circle(screen, GOLD, (center_x, center_y), 3, 1)
            elif self.genre == "history":
                # Scroll symbol
                pygame.draw.line(screen, GOLD, (center_x - 3, center_y), (center_x + 3, center_y), 1)
            elif self.genre == "science":
                # Atom symbol
                pygame.draw.circle(screen, GOLD, (center_x, center_y), 1)
                pygame.draw.circle(screen, GOLD, (center_x, center_y), 3, 1)
            else:  # classic
                # Classic binding lines
                pygame.draw.line(screen, GOLD, (self.x + 2, self.y + 5), (self.x + self.width - 2, self.y + 5), 1)
                pygame.draw.line(screen, GOLD, (self.x + 2, self.y + 8), (self.x + self.width - 2, self.y + 8), 1)
            
            # Leather binding effect
            pygame.draw.rect(screen, tuple(max(0, c - 30) for c in self.color), (self.x, self.y, self.width, self.height), 1)

class PowerUp:
    def __init__(self):
        self.x = SCREEN_WIDTH + 50
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.width = 25
        self.height = 25
        self.speed = 2
        self.type = random.choice([
            "coffee", "mega_book", "silence_aura", "time_freeze",
            "rare_manuscript", "reading_glasses", "bookworm_blessing",
            "shield", "multi_shot", "magnet", "freeze_time"
        ])
        
        # Set colors based on type
        color_map = {
            "coffee": (139, 69, 19),           # Brown
            "mega_book": (255, 165, 0),        # Orange
            "silence_aura": (100, 149, 237),   # Cornflower blue
            "time_freeze": (255, 215, 0),      # Gold
            "rare_manuscript": (128, 0, 128),  # Purple
            "reading_glasses": (192, 192, 192), # Silver
            "bookworm_blessing": (34, 139, 34), # Forest green
            "shield": (255, 255, 255),         # White
            "multi_shot": (255, 100, 0),       # Red-orange
            "magnet": (75, 0, 130),            # Indigo
            "freeze_time": (0, 255, 255)       # Cyan
        }
        self.color = color_map.get(self.type, (255, 255, 255))
    
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
        elif self.type == "mega_book":
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
        elif self.type == "silence_aura":
            # Mystical orb of silence
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 12)
            pygame.draw.circle(screen, (150, 200, 255), (int(self.x), int(self.y)), 12, 2)
            # Floating runes
            for i, angle in enumerate([0, 60, 120, 180, 240, 300]):
                rune_x = self.x + 8 * math.cos(math.radians(angle))
                rune_y = self.y + 8 * math.sin(math.radians(angle))
                pygame.draw.circle(screen, WHITE, (int(rune_x), int(rune_y)), 2)
            # Pulsing effect
            pygame.draw.circle(screen, (200, 220, 255), (int(self.x), int(self.y)), 15, 1)
        elif self.type == "shield":
            # Protective shield
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 12)
            pygame.draw.circle(screen, (200, 200, 255), (int(self.x), int(self.y)), 12, 2)
            # Shield cross
            pygame.draw.line(screen, (100, 100, 255), (self.x - 6, self.y), (self.x + 6, self.y), 2)
            pygame.draw.line(screen, (100, 100, 255), (self.x, self.y - 6), (self.x, self.y + 6), 2)
            # Glow effect
            pygame.draw.circle(screen, (150, 150, 255), (int(self.x), int(self.y)), 15, 1)
        elif self.type == "multi_shot":
            # Multiple arrows
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 12)
            # Three arrows pointing outward
            pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x - 8, self.y - 4), 2)
            pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x + 8, self.y - 4), 2)
            pygame.draw.line(screen, WHITE, (self.x, self.y), (self.x, self.y + 8), 2)
            # Glow effect
            pygame.draw.circle(screen, (255, 150, 0), (int(self.x), int(self.y)), 15, 1)
        elif self.type == "magnet":
            # Magnetic field
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 12)
            # Magnetic field lines
            for i in range(6):
                angle = i * 60
                start_x = self.x + 6 * math.cos(math.radians(angle))
                start_y = self.y + 6 * math.sin(math.radians(angle))
                end_x = self.x + 10 * math.cos(math.radians(angle))
                end_y = self.y + 10 * math.sin(math.radians(angle))
                pygame.draw.line(screen, WHITE, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 1)
            # Glow effect
            pygame.draw.circle(screen, (100, 0, 200), (int(self.x), int(self.y)), 15, 1)
        elif self.type == "freeze_time":
            # Ice crystal
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 12)
            # Ice spikes
            for i in range(6):
                angle = i * 60
                spike_x = self.x + 8 * math.cos(math.radians(angle))
                spike_y = self.y + 8 * math.sin(math.radians(angle))
                pygame.draw.line(screen, WHITE, (self.x, self.y), (int(spike_x), int(spike_y)), 2)
            # Glow effect
            pygame.draw.circle(screen, (0, 200, 255), (int(self.x), int(self.y)), 15, 1)
        else:  # time_freeze
            # Clockwork mechanism
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 12)
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 12, 2)
            # Clock hands
            pygame.draw.line(screen, BLACK, (self.x, self.y), (self.x, self.y - 8), 2)
            pygame.draw.line(screen, BLACK, (self.x, self.y), (self.x + 6, self.y), 2)
            # Clock numbers
            for i in range(4):
                angle = i * 90
                num_x = self.x + 8 * math.cos(math.radians(angle))
                num_y = self.y + 8 * math.sin(math.radians(angle))
                pygame.draw.circle(screen, BLACK, (int(num_x), int(num_y)), 1)
            # Glowing effect
            pygame.draw.circle(screen, AMBER, (int(self.x), int(self.y)), 16, 1)

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
