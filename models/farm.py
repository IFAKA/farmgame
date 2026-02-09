"""Farm state management."""

from typing import Optional, Dict, Tuple, List
from models.crop import Crop


class Farm:
    """Manages the farm grid and crops."""

    def __init__(self, width: int = 4, height: int = 4):
        """
        Initialize farm.

        Args:
            width: Grid width
            height: Grid height
        """
        self.width = width
        self.height = height
        self.plots: Dict[Tuple[int, int], Optional[Crop]] = {}

        # Initialize empty plots
        for x in range(width):
            for y in range(height):
                self.plots[(x, y)] = None

    def plant_crop(self, x: int, y: int, crop_type: str) -> bool:
        """
        Plant a crop at the given position.

        Args:
            x: X coordinate
            y: Y coordinate
            crop_type: Type of crop to plant

        Returns:
            True if planted successfully, False if plot occupied
        """
        if not self._is_valid_position(x, y):
            return False

        if self.plots[(x, y)] is not None:
            return False  # Plot already occupied

        self.plots[(x, y)] = Crop(crop_type)
        return True

    def harvest_crop(self, x: int, y: int) -> Optional[Crop]:
        """
        Harvest crop at the given position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            The harvested Crop object, or None if no crop
        """
        if not self._is_valid_position(x, y):
            return None

        crop = self.plots[(x, y)]
        if crop is None:
            return None

        # Clear the plot
        self.plots[(x, y)] = None
        return crop

    def get_crop(self, x: int, y: int) -> Optional[Crop]:
        """
        Get crop at the given position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Crop object or None
        """
        if not self._is_valid_position(x, y):
            return None
        return self.plots.get((x, y))

    def get_ready_crops(self) -> List[Tuple[int, int, Crop]]:
        """
        Get all crops that are ready to harvest.

        Returns:
            List of (x, y, crop) tuples
        """
        ready = []
        for (x, y), crop in self.plots.items():
            if crop is not None and crop.is_ready:
                ready.append((x, y, crop))
        return ready

    def expand(self, new_width: int, new_height: int) -> bool:
        """
        Expand the farm to a new size.

        Args:
            new_width: New grid width
            new_height: New grid height

        Returns:
            True if expanded successfully
        """
        if new_width < self.width or new_height < self.height:
            return False  # Can't shrink

        # Add new empty plots
        for x in range(new_width):
            for y in range(new_height):
                if (x, y) not in self.plots:
                    self.plots[(x, y)] = None

        self.width = new_width
        self.height = new_height
        return True

    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within farm bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def to_dict(self) -> dict:
        """Serialize farm to dictionary for saving."""
        return {
            'width': self.width,
            'height': self.height,
            'plots': {
                f"{x},{y}": crop.to_dict() if crop else None
                for (x, y), crop in self.plots.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Farm':
        """Deserialize farm from dictionary."""
        farm = cls(width=data['width'], height=data['height'])

        # Restore crops
        for coord_str, crop_data in data['plots'].items():
            x, y = map(int, coord_str.split(','))
            if crop_data is not None:
                farm.plots[(x, y)] = Crop.from_dict(crop_data)

        return farm
