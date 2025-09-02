# Library Defender 📚

A pygame-based game where you play as a librarian defending the library from noisy monsters!

## Game Concept

You are a librarian, and your goal is to keep the library quiet. Noisy monsters try to sneak in and make noise. Your job is to silence them before the noise meter fills up!

## Controls

- **Arrow Keys**: Move the librarian
- **Spacebar**: Throw books at enemies (click to shoot)
- **Spacebar (hold)**: Shush attack (AOE silence)
- **R**: Restart game (when game over)

## Gameplay Features

- **Player**: Librarian that can move around the library
- **Enemies**: Noisy creatures that spawn randomly and move toward the shelves
- **Attacks**: 
  - Throw books at enemies to silence them 📕
  - "Shush!" attack (AOE – press space to silence everything nearby) 🤫
- **Noise Meter**: If too many monsters make noise, the meter fills up → Game Over
- **Score System**: Survive as long as possible, or silence as many monsters as possible

## Installation

1. Install Python 3.7+
2. Install pygame:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Development Status

- ✅ Basic game structure
- ✅ Player movement (arrow keys)
- ✅ Enemy spawning and movement
- ✅ Book throwing (mouse click to aim and shoot)
- ✅ Collision detection
- ✅ Noise meter
- ✅ Game over and restart
- ✅ Scoring system
- ✅ AOE shush attack (spacebar with cooldown)
- ✅ Power-ups (Coffee ☕ for speed, Mega Book 📖 for area damage)
- ✅ Three enemy types (students, animals, ghosts)
- ✅ Particle effects
- ✅ Difficulty progression
- ✅ Visual polish and animations

## Game Features

### Enemy Types
- **Students** (pink): Medium noise level, moderate speed
- **Animals** (brown): Low noise level, slower speed  
- **Ghosts** (blue): High noise level, faster speed

### Power-ups
- **Coffee ☕**: Doubles player speed for 5 seconds
- **Mega Book 📖**: Creates area damage books for 3 seconds

### Combat System
- **Book Throwing**: Click to aim and throw books at enemies
- **Shush Attack**: Spacebar for AOE silence (1 second cooldown)
- **Particle Effects**: Visual feedback when enemies are defeated

### Difficulty
- Enemies spawn faster over time (2 minutes to reach maximum difficulty)
- Different enemy types have varying noise levels and speeds

## Future Features

- Silent Reading Mode (dark screen with glowing eyes)
- Sound effects ("shhh", monster laughs, book throwing)
- More power-up types
- High score system
- Multiple levels/rooms
