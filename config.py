"""Game configuration and balance settings."""

from dataclasses import dataclass

# Initial state
STARTING_COINS = 100
STARTING_FARM_SIZE = (4, 4)
STARTING_UNLOCKED_CROPS = ['RADISH', 'CARROT']

# Progression
XP_PER_LEVEL = 100  # Linear: 100, 200, 300...
XP_PER_HARVEST = 10

# Timing
AUTO_SAVE_INTERVAL = 30  # seconds
GROWTH_UPDATE_INTERVAL = 1  # seconds
OFFLINE_REWARD_MULTIPLIER = 0.7  # 70% value
MAX_OFFLINE_TIME = 86400  # 24 hours


@dataclass
class CropConfig:
    """Configuration for a single crop type."""
    name: str
    emoji: str
    growth_time: int  # seconds
    seed_cost: int
    sell_price: int
    unlock_level: int

    @property
    def profit(self) -> int:
        return self.sell_price - self.seed_cost


# Crop balance
CROPS = {
    'RADISH': CropConfig('Radish', '🔴', 30, 10, 15, 1),
    'CARROT': CropConfig('Carrot', '🥕', 60, 20, 35, 1),
    'WHEAT': CropConfig('Wheat', '🌾', 120, 30, 60, 2),
    'TOMATO': CropConfig('Tomato', '🍅', 180, 50, 100, 3),
    'CORN': CropConfig('Corn', '🌽', 300, 80, 180, 5),
    'PUMPKIN': CropConfig('Pumpkin', '🎃', 600, 150, 400, 7),
}

# Growth stage emojis
STAGE_EMOJIS = {
    'EMPTY': '⬛',
    'PLANTED': '🌱',
    'SPROUTING': '🌿',
    'GROWING': '🪴',
    'FLOWERING': '🌺',
    'READY': '✨',
}

# Save location
import os
SAVE_DIR = os.path.expanduser('~/.farmgame')
SAVE_FILE = os.path.join(SAVE_DIR, 'savegame.json')
