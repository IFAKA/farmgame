# Quick Start Guide

## Installation (30 seconds)

```bash
cd farmgame
./run.sh
```

That's it! The script will:
1. Create a virtual environment (if needed)
2. Install dependencies (if needed)
3. Launch the game

## Your First 5 Minutes

### 1. Plant Your First Crop (0:00)
- Click any empty plot (gray border)
- Select **Radish** (costs 10💰)
- Watch it grow with a progress bar

### 2. Harvest (0:30)
- When the plot turns **green**, click it
- You'll earn **15💰** and **10 XP**
- The plot becomes empty again

### 3. Expand Your Farm (0:30 - 2:00)
- Plant multiple crops at once
- Try **Carrot** (1 minute, better profit)
- Mix fast and slow crops

### 4. Level Up (2:00 - 5:00)
- Harvest 10 crops to reach **Level 2**
- **Wheat** unlocks! (2 min, 30💰 profit)
- Keep harvesting to unlock more crops

### 5. Walk Away (any time)
- Press **Q** to quit
- Game auto-saves every 30s
- Crops continue growing offline
- Return later to auto-harvested crops (70% value)

## Tips for ADHD Players

**Short Bursts:**
- Just plant Radishes (30s each)
- Check every 30-60 seconds
- Quick dopamine hits!

**Medium Sessions:**
- Plant a mix of Radish, Carrot, Wheat
- Stagger planting times
- Always something ready to harvest

**Deep Focus:**
- Optimize planting schedules
- Maximize profit per minute
- Strategic crop rotation

**Hyperfocus Mode:**
- Fill entire farm with synchronized crops
- Plan multi-stage expansion strategy
- Calculate optimal XP farming routes

## Keyboard Shortcuts

- **Q** - Quit (auto-saves)
- **H** - Help (crop info)
- **S** - Shop (coming soon)
- **Mouse** - Click plots to interact

## Visual Cues

- 🔴🥕🌾🍅🌽🎃 - Crop types
- 🌱🌿🪴🌺✨ - Growth stages
- Gray border = Empty
- Yellow border = Growing
- Green border = Ready!
- Red border = Hover

## Game Saves

Location: `~/.farmgame/savegame.json`

The game:
- Auto-saves every 30 seconds
- Saves on quit
- Shows offline summary on return

## Performance

The game runs at 60fps and uses very little CPU when idle. Perfect for keeping running in a terminal tab!

## Troubleshooting

**Game won't start:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install textual rich
python main.py
```

**Terminal too small:**
- Minimum size: 80x24
- Recommended: 100x30 or larger

**Weird characters:**
- Your terminal needs Unicode support
- Use Terminal.app, iTerm2, or similar modern terminal

## Have Fun!

This game is designed to be relaxing and rewarding. There's no wrong way to play. Plant crops, watch them grow, and enjoy the casual farming experience! 🌱✨
