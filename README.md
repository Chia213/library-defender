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
- ✅ Player movement
- ✅ Enemy spawning and movement
- ✅ Book throwing (click to shoot)
- ✅ Collision detection
- ✅ Noise meter
- ✅ Game over and restart
- ✅ Basic scoring system
- 🔄 AOE shush attack (in progress)
- ⏳ Power-ups
- ⏳ Sound effects
- ⏳ Visual polish

## Future Features

- Different enemy types with varying noise levels
- Power-ups (Coffee ☕ for speed, Mega Book 📖 for area damage)
- Silent Reading Mode (dark screen with glowing eyes)
- Sound effects ("shhh", monster laughs)
- Better graphics and animations
