"""Crop system implementation."""

from enum import Enum
from typing import Optional, Dict, Any
import time

from config import CROPS, STAGE_EMOJIS, CropConfig


class GrowthStage(Enum):
    """Visual growth stages for crops."""
    EMPTY = "EMPTY"
    PLANTED = "PLANTED"
    SPROUTING = "SPROUTING"
    GROWING = "GROWING"
    FLOWERING = "FLOWERING"
    READY = "READY"


class Crop:
    """Represents a single growing crop."""

    def __init__(self, crop_type: str, planted_at: Optional[float] = None) -> None:
        """
        Initialize a crop.

        Args:
            crop_type: Key from CROPS config (e.g., 'RADISH')
            planted_at: Unix timestamp when planted (defaults to now)

        Raises:
            ValueError: If crop_type is not in CROPS config
            ValueError: If planted_at is negative
        """
        if crop_type not in CROPS:
            raise ValueError(f"Unknown crop type: {crop_type}")

        self.crop_type = crop_type
        self.config: CropConfig = CROPS[crop_type]

        # Validate planted_at timestamp
        plant_time = planted_at if planted_at is not None else time.time()
        if plant_time < 0:
            raise ValueError(f"Invalid planted_at timestamp: {plant_time}")

        self.planted_at = plant_time

    @property
    def growth_progress(self) -> float:
        """
        Calculate growth progress from 0.0 to 1.0.

        Returns:
            Float between 0.0 (just planted) and 1.0+ (ready)
        """
        elapsed = time.time() - self.planted_at
        progress = elapsed / self.config.growth_time
        return max(0.0, progress)  # Don't return negative

    @property
    def is_ready(self) -> bool:
        """Check if crop is ready to harvest."""
        return self.growth_progress >= 1.0

    @property
    def current_stage(self) -> GrowthStage:
        """
        Determine current visual growth stage based on progress.

        Returns:
            GrowthStage enum value
        """
        if self.is_ready:
            return GrowthStage.READY

        progress = self.growth_progress

        if progress < 0.2:
            return GrowthStage.PLANTED
        elif progress < 0.4:
            return GrowthStage.SPROUTING
        elif progress < 0.6:
            return GrowthStage.GROWING
        elif progress < 0.8:
            return GrowthStage.FLOWERING
        else:
            return GrowthStage.FLOWERING  # Almost ready

    @property
    def time_remaining(self) -> str:
        """
        Get human-readable time remaining until ready.

        Returns:
            String like "Ready!", "30s", "2m 15s", "1h 5m"
        """
        if self.is_ready:
            return "Ready!"

        remaining_seconds = int(self.config.growth_time * (1.0 - self.growth_progress))

        if remaining_seconds < 60:
            return f"{remaining_seconds}s"
        elif remaining_seconds < 3600:
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            return f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
        else:
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"

    @property
    def stage_emoji(self) -> str:
        """Get emoji for current growth stage."""
        return STAGE_EMOJIS[self.current_stage.value]

    @property
    def progress_bar(self) -> str:
        """
        Generate a visual progress bar (8 characters).

        Returns:
            String like "████░░░░" showing growth progress
        """
        if self.is_ready:
            return "████████"

        filled = int(self.growth_progress * 8)
        return "█" * filled + "░" * (8 - filled)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize crop to dictionary for saving."""
        return {
            'crop_type': self.crop_type,
            'planted_at': self.planted_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Crop':
        """Deserialize crop from dictionary."""
        return cls(
            crop_type=data['crop_type'],
            planted_at=data['planted_at']
        )
