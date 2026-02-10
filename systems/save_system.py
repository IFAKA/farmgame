"""Save/load system with offline progression."""

import json
import os
import time
import logging
from typing import Optional, Tuple, Dict, Any

from config import (
    SAVE_DIR, SAVE_FILE, OFFLINE_REWARD_MULTIPLIER,
    MAX_OFFLINE_TIME, STARTING_FARM_SIZE, CROPS,
    MIN_OFFLINE_TIME_TO_PROCESS
)
from models.farm import Farm
from models.player import Player

logger = logging.getLogger(__name__)


class SaveSystem:
    """Handles game persistence and offline progression."""

    @staticmethod
    def ensure_save_directory() -> None:
        """Create save directory if it doesn't exist."""
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    @staticmethod
    def save_game(farm: Farm, player: Player) -> bool:
        """
        Save game state to disk.

        Args:
            farm: Farm object to save
            player: Player object to save

        Returns:
            True if saved successfully
        """
        SaveSystem.ensure_save_directory()

        data = {
            'version': 1,
            'last_save': time.time(),
            'farm': farm.to_dict(),
            'player': player.to_dict(),
        }

        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Game saved successfully")
            return True
        except (IOError, OSError) as e:
            logger.error(f"Error saving game: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving game: {e}")
            return False

    @staticmethod
    def load_game() -> Optional[Tuple[Farm, Player, Dict[str, Any]]]:
        """
        Load game state from disk.

        Returns:
            Tuple of (farm, player, offline_summary) or None if no save
            offline_summary contains: {
                'offline_time': seconds,
                'auto_harvested': [(crop_type, coins), ...],
                'total_coins': int
            }
        """
        if not os.path.exists(SAVE_FILE):
            return None

        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)

            # Validate save file structure
            if not all(key in data for key in ['version', 'last_save', 'farm', 'player']):
                logger.error("Save file missing required fields")
                return None

            farm = Farm.from_dict(data['farm'])
            player = Player.from_dict(data['player'])
            last_save = data['last_save']

            # Calculate offline progression
            offline_summary = SaveSystem._process_offline_time(
                farm, player, last_save
            )

            logger.info("Game loaded successfully")
            return farm, player, offline_summary

        except json.JSONDecodeError as e:
            logger.error(f"Corrupted save file (invalid JSON): {e}")
            return None
        except (IOError, OSError) as e:
            logger.error(f"Error reading save file: {e}")
            return None
        except KeyError as e:
            logger.error(f"Save file missing required field: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading game: {e}")
            return None

    @staticmethod
    def _process_offline_time(
        farm: Farm,
        player: Player,
        last_save: float
    ) -> Dict[str, Any]:
        """
        Process crops that grew while offline.

        Args:
            farm: Farm to process
            player: Player to update
            last_save: Unix timestamp of last save

        Returns:
            Dictionary with offline summary
        """
        offline_time = min(time.time() - last_save, MAX_OFFLINE_TIME)

        if offline_time < MIN_OFFLINE_TIME_TO_PROCESS:
            return {
                'offline_time': 0,
                'auto_harvested': [],
                'total_coins': 0
            }

        auto_harvested = []
        total_coins = 0

        # Check all crops
        for (x, y), crop in list(farm.plots.items()):
            if crop is None:
                continue

            # Check if crop finished during offline time
            time_since_plant = time.time() - crop.planted_at
            if time_since_plant >= crop.config.growth_time:
                # Auto-harvest at 70% value
                coins_earned = int(crop.config.sell_price * OFFLINE_REWARD_MULTIPLIER)
                player.add_coins(coins_earned)
                player.total_crops_harvested += 1
                total_coins += coins_earned

                auto_harvested.append((crop.config.name, coins_earned))

                # Clear the plot
                farm.plots[(x, y)] = None

        return {
            'offline_time': offline_time,
            'auto_harvested': auto_harvested,
            'total_coins': total_coins
        }

    @staticmethod
    def create_new_game() -> Tuple[Farm, Player]:
        """
        Create a new game with default state.

        Returns:
            Tuple of (farm, player)
        """
        farm = Farm(width=STARTING_FARM_SIZE[0], height=STARTING_FARM_SIZE[1])
        player = Player()
        return farm, player
