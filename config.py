"""Game configuration and balance settings."""

from dataclasses import dataclass
from typing import Dict
import logging

logger = logging.getLogger(__name__)

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

# UI Timing (delays for focus restoration, etc.)
MODAL_CLOSE_DELAY = 0.05  # seconds
PLOT_FOCUS_DELAY = 0.1  # seconds
MODAL_ANIMATION_DELAY = 0.3  # seconds

# UI Messages
MIN_OFFLINE_TIME_FOR_TOAST = 60  # Show toast for offline > 1 min
MIN_OFFLINE_TIME_FOR_MODAL = 300  # Show modal for offline > 5 min
MIN_OFFLINE_TIME_TO_PROCESS = 10  # Process offline progression > 10 sec


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


def validate_config() -> bool:
    """
    Validate game configuration for errors.

    Returns:
        True if configuration is valid, False otherwise
    """
    is_valid = True

    # Validate CROPS
    if not CROPS:
        logger.error("CROPS configuration is empty")
        return False

    for crop_key, config in CROPS.items():
        # Check for negative or zero values
        if config.growth_time <= 0:
            logger.error(f"Crop '{crop_key}' has invalid growth_time: {config.growth_time}")
            is_valid = False

        if config.seed_cost < 0:
            logger.error(f"Crop '{crop_key}' has negative seed_cost: {config.seed_cost}")
            is_valid = False

        if config.sell_price < 0:
            logger.error(f"Crop '{crop_key}' has negative sell_price: {config.sell_price}")
            is_valid = False

        if config.unlock_level < 1:
            logger.error(f"Crop '{crop_key}' has invalid unlock_level: {config.unlock_level}")
            is_valid = False

        # Check for unprofitable crops
        if config.profit < 0:
            logger.warning(f"Crop '{crop_key}' is unprofitable (profit: {config.profit})")

    # Validate progression settings
    if XP_PER_LEVEL <= 0:
        logger.error(f"XP_PER_LEVEL must be positive: {XP_PER_LEVEL}")
        is_valid = False

    if XP_PER_HARVEST <= 0:
        logger.error(f"XP_PER_HARVEST must be positive: {XP_PER_HARVEST}")
        is_valid = False

    # Validate timing
    if AUTO_SAVE_INTERVAL <= 0:
        logger.error(f"AUTO_SAVE_INTERVAL must be positive: {AUTO_SAVE_INTERVAL}")
        is_valid = False

    if OFFLINE_REWARD_MULTIPLIER < 0 or OFFLINE_REWARD_MULTIPLIER > 1:
        logger.error(f"OFFLINE_REWARD_MULTIPLIER must be between 0 and 1: {OFFLINE_REWARD_MULTIPLIER}")
        is_valid = False

    if is_valid:
        logger.info("Configuration validated successfully")
    else:
        logger.error("Configuration validation failed")

    return is_valid
