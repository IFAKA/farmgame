# 🌱 TUI Farm Game

ADHD-friendly terminal farming game. Quick dopamine hits, zero commitment.

## Three Commands You Need

### Install
```bash
pipx install git+https://github.com/IFAKA/farmgame.git
```

### Play
```bash
farm
```

### Uninstall (no traces)
```bash
pipx uninstall farmgame && rm -rf ~/.farmgame
```

---

## Don't have pipx?
```bash
brew install pipx
```

---

## Features

- 🌾 **Grow Crops**: Plant seeds and watch them grow in real-time
- 💰 **Economy**: Buy seeds, sell harvests, and earn coins
- ⭐ **Progression**: Level up to unlock new crop types
- 💾 **Auto-Save**: Game saves automatically every 30 seconds
- 🌙 **Offline Progress**: Crops auto-harvest when you're away (70% value)
- 🎨 **Visual Feedback**: Color-coded plots, progress bars, and emojis

## How to Play

### Controls
- **Click empty plot** - Select seed to plant
- **Click ready crop** (green border) - Harvest
- **Click growing crop** - View growth status
- **S** - Open shop (coming soon)
- **H** - Show help
- **Q** - Quit game

### Crops

| Crop | Time | Cost | Sell | Profit | Unlock |
|------|------|------|------|--------|--------|
| 🔴 Radish | 30s | 10💰 | 15💰 | 5💰 | Level 1 |
| 🥕 Carrot | 1m | 20💰 | 35💰 | 15💰 | Level 1 |
| 🌾 Wheat | 2m | 30💰 | 60💰 | 30💰 | Level 2 |
| 🍅 Tomato | 3m | 50💰 | 100💰 | 50💰 | Level 3 |
| 🌽 Corn | 5m | 80💰 | 180💰 | 100💰 | Level 5 |
| 🎃 Pumpkin | 10m | 150💰 | 400💰 | 250💰 | Level 7 |

### Plot Colors
- **Gray** - Empty plot (click to plant)
- **Yellow border** - Crop growing
- **Green border** - Ready to harvest!
- **Red border** - Plot hovered

### Progression
- Earn **10 XP** per harvest
- Level up at **100 XP** per level (linear)
- Unlock new crops as you level up
- Start with 100💰 and a 4×4 farm

## Game Strategy

1. **Start Fast**: Plant Radishes (30s) for quick returns
2. **Reinvest**: Use profits to plant higher-value crops
3. **Mix Timing**: Combine fast and slow crops for steady income
4. **Level Up**: Focus on harvests to unlock better crops
5. **Offline Gains**: Leave crops growing when you step away

## Save File

Game saves automatically to `~/.farmgame/savegame.json`

Offline crops auto-harvest at 70% value (capped at 24 hours).

## Development / Local Install

```bash
# Clone and install in editable mode
git clone https://github.com/IFAKA/farmgame.git
cd farmgame
pipx install -e .

# Now you can edit code and changes apply immediately
# Uninstall same way: pipx uninstall farmgame && rm -rf ~/.farmgame
```

## ADHD-Friendly Design

- ⚡ Quick rewards (30s crops)
- 🎯 Clear visual feedback
- 🔄 Flexible play sessions (30s to 30m)
- 📊 Simple, not overwhelming
- 🎨 Rich colors and emojis
- 🌙 No pressure, no timers

## Development

Built with [Textual](https://textual.textualize.io/) - a modern TUI framework for Python.

### Project Structure
```
farmgame/
├── main.py              # Main application
├── config.py            # Game configuration
├── models/              # Game logic
│   ├── crop.py         # Crop system
│   ├── farm.py         # Farm grid
│   └── player.py       # Player state
├── widgets/             # UI components
│   ├── plot.py         # Individual plot
│   ├── farm_grid.py    # Grid container
│   └── sidebar.py      # Stats display
├── systems/             # Game systems
│   └── save_system.py  # Save/load + offline progression
└── styles/              # CSS styling
    └── farmgame.tcss   # Textual CSS
```

## Future Features (Not Yet Implemented)

- 🏪 Shop screen with seed buying
- 🌦️ Weather and seasons
- 🐄 Animals and livestock
- 🏆 Achievement system
- 🔧 Tools and upgrades
- 🎨 Decorations
- 💬 NPCs and trading
- 📈 Farm expansion (4×4 → 8×8)

## License

MIT

## Credits

Made for casual farming fun! 🌱✨
