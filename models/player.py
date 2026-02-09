"""Player state and progression."""

from typing import Set
from config import STARTING_COINS, STARTING_UNLOCKED_CROPS, XP_PER_LEVEL


class Player:
    """Manages player resources, XP, and unlocks."""

    def __init__(
        self,
        coins: int = STARTING_COINS,
        experience: int = 0,
        level: int = 1,
        total_crops_planted: int = 0,
        total_crops_harvested: int = 0,
        unlocked_crops: Set[str] = None
    ):
        """Initialize player state."""
        self.coins = coins
        self.experience = experience
        self.level = level
        self.total_crops_planted = total_crops_planted
        self.total_crops_harvested = total_crops_harvested
        self.unlocked_crops = unlocked_crops or set(STARTING_UNLOCKED_CROPS)

    @property
    def xp_for_next_level(self) -> int:
        """Calculate XP needed for next level."""
        return self.level * XP_PER_LEVEL

    @property
    def xp_progress(self) -> float:
        """Get XP progress toward next level (0.0 to 1.0)."""
        return min(1.0, self.experience / self.xp_for_next_level)

    def add_coins(self, amount: int) -> None:
        """Add coins to player."""
        self.coins += amount

    def spend_coins(self, amount: int) -> bool:
        """
        Spend coins.

        Args:
            amount: Amount to spend

        Returns:
            True if had enough coins, False otherwise
        """
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def add_experience(self, amount: int) -> int:
        """
        Add experience and handle level ups.

        Args:
            amount: XP to add

        Returns:
            Number of levels gained
        """
        self.experience += amount
        levels_gained = 0

        while self.experience >= self.xp_for_next_level:
            self.experience -= self.xp_for_next_level
            self.level += 1
            levels_gained += 1

        return levels_gained

    def unlock_crop(self, crop_type: str) -> None:
        """Unlock a new crop type."""
        self.unlocked_crops.add(crop_type)

    def has_crop_unlocked(self, crop_type: str) -> bool:
        """Check if player has unlocked a crop."""
        return crop_type in self.unlocked_crops

    def to_dict(self) -> dict:
        """Serialize player to dictionary for saving."""
        return {
            'coins': self.coins,
            'experience': self.experience,
            'level': self.level,
            'total_crops_planted': self.total_crops_planted,
            'total_crops_harvested': self.total_crops_harvested,
            'unlocked_crops': list(self.unlocked_crops),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Deserialize player from dictionary."""
        return cls(
            coins=data['coins'],
            experience=data['experience'],
            level=data['level'],
            total_crops_planted=data['total_crops_planted'],
            total_crops_harvested=data['total_crops_harvested'],
            unlocked_crops=set(data['unlocked_crops']),
        )
