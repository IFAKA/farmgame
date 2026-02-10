# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TUI Farm Game is an ADHD-friendly terminal farming game built with [Textual](https://textual.textualize.io/), a modern Python TUI framework. Players plant crops, harvest them for coins, level up, and unlock new crop types. The game includes auto-save, offline progression (70% value for auto-harvested crops), and keyboard-first navigation.

## Development Commands

### Installation
```bash
# Install from local editable mode
pipx install -e .

# Uninstall (including save data)
pipx uninstall farmgame && rm -rf ~/.farmgame
```

### Running
```bash
# Run the game
farm
# or
farmgame
# or directly
python main.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest test_game.py

# Run specific test
pytest test_game.py::test_name

# Verbose output with print statements
pytest -v -s
```

Note: Tests use `pytest-asyncio` (configured to auto mode in `pytest.ini`) since Textual is async-based.

## Architecture

### High-Level Structure

The codebase follows a clean separation of concerns:

- **models/**: Pure game logic and state (Farm, Player, Crop)
- **widgets/**: Textual UI components (Plot, FarmGrid, Sidebar)
- **systems/**: Cross-cutting concerns (SaveSystem with offline progression)
- **main.py**: FarmGame app class that orchestrates everything
- **config.py**: Game balance, crop definitions, constants
- **styles/**: Textual CSS for UI styling

### Key Architectural Patterns

**Models are the source of truth**: The `Farm` and `Player` models hold all game state. Widgets display this state but don't own it.

**Reactive updates**: The main app uses Textual's reactive system and worker intervals to:
- Auto-save every 30 seconds (`AUTO_SAVE_INTERVAL`)
- Update crop growth UI every second (`GROWTH_UPDATE_INTERVAL`)

**Modal system**: Two modal types are defined as Container widgets in main.py:
- `SeedSelector`: Crop selection when planting
- `OfflineSummary`: Shows what happened while player was offline

Both modals handle their own keyboard navigation and focus management. They're mounted to the app, then removed when dismissed. Focus is restored to the farm grid after closing.

**Message passing**: Widgets communicate via Textual messages. For example, `PlotClicked` message (defined in widgets/plot.py) is sent when a plot is clicked, and main.py handles it via `on_plot_clicked()`.

**Serialization**: Farm and Player models implement `to_dict()` and `from_dict()` class methods for JSON persistence.

### Important Implementation Details

**Focus and navigation**: The app tracks `focused_plot` (x, y tuple) and implements vim-style (hjkl) and arrow key navigation. When modals open/close, focus must be explicitly restored to the plot.

**Crop growth**: Crops store `planted_at` timestamp and calculate `is_ready` based on elapsed time vs `config.growth_time`. The UI polls every second to update progress indicators.

**Offline progression**: On load, `SaveSystem._process_offline_time()` checks all crops against elapsed time since last save. Ready crops are auto-harvested at 70% value (configurable via `OFFLINE_REWARD_MULTIPLIER`), capped at 24 hours.

**Modal centering**: Modals are styled with CSS to center them. Per Textual documentation, they must be direct children of the app/screen and use absolute positioning with proper alignment.

## Configuration

All game balance lives in `config.py`:
- `CROPS`: Dict of crop configurations (growth time, cost, sell price, unlock level)
- `STARTING_COINS`, `STARTING_FARM_SIZE`: Initial player state
- `XP_PER_LEVEL`, `XP_PER_HARVEST`: Progression rates
- `OFFLINE_REWARD_MULTIPLIER`: 0.7 (70% value for offline harvests)

Use dataclasses (e.g., `CropConfig`) for structured config.

## Save System

- Save location: `~/.farmgame/savegame.json`
- Format: JSON with version, last_save timestamp, farm dict, player dict
- On app unmount (quit), game saves automatically
- Auto-saves every 30 seconds while running

When adding new fields to models, ensure backward compatibility by providing defaults in `from_dict()`.

## Textual-Specific Notes

- CSS lives in `styles/farmgame.tcss` and is referenced via `CSS_PATH` in FarmGame
- Use `@work` decorator for async background tasks that need to interact with UI
- Use `set_interval()` for recurring tasks (auto-save, growth updates)
- Widget bindings (BINDINGS class variable) define keyboard shortcuts
- Use `can_focus = True` on containers that need to capture keyboard input

## Common Gotchas

- When a widget sends a message, the handler method must be `async` even if it doesn't use `await`
- Textual CSS uses a subset of CSS properties - check docs for supported properties
- Modal focus management: Always call `.focus()` on modals after mounting and restore focus to original widget after removal
- Time calculations: Use `time.time()` for timestamps (floats), not datetime objects
