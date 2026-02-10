#!/usr/bin/env python3
"""Unit tests for game components using pytest."""

import pytest
import time
from models.crop import Crop
from models.farm import Farm
from models.player import Player
from systems.save_system import SaveSystem
from config import CROPS, XP_PER_LEVEL, SAVE_FILE


class TestCrop:
    """Test crop growth system."""

    def test_crop_creation(self):
        """Test basic crop creation."""
        radish = Crop('RADISH')
        assert radish.crop_type == 'RADISH'
        assert radish.config.growth_time == 30
        assert radish.growth_progress >= 0.0
        assert not radish.is_ready

    def test_crop_invalid_type(self):
        """Test that invalid crop type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown crop type"):
            Crop('INVALID_CROP')

    def test_crop_negative_timestamp(self):
        """Test that negative timestamp raises ValueError."""
        with pytest.raises(ValueError, match="Invalid planted_at timestamp"):
            Crop('RADISH', planted_at=-100)

    def test_crop_serialization(self):
        """Test crop serialization and deserialization."""
        radish = Crop('RADISH')
        data = radish.to_dict()
        radish2 = Crop.from_dict(data)

        assert radish2.crop_type == radish.crop_type
        assert radish2.planted_at == radish.planted_at

    def test_crop_growth_over_time(self):
        """Test that crops actually grow over time."""
        crop = Crop('RADISH')
        initial_progress = crop.growth_progress

        # Wait a moment
        time.sleep(0.5)

        new_progress = crop.growth_progress
        assert new_progress > initial_progress, "Crop should have grown"

    def test_crop_ready_state(self):
        """Test that crop becomes ready after growth time."""
        # Create crop planted in the past
        past_time = time.time() - 100  # 100 seconds ago
        crop = Crop('RADISH', planted_at=past_time)

        assert crop.is_ready
        assert crop.time_remaining == "Ready!"

    def test_crop_stage_progression(self):
        """Test that growth stages progress correctly."""
        current_time = time.time()

        # Just planted (0% progress)
        crop1 = Crop('RADISH', planted_at=current_time)
        assert crop1.current_stage.value == "PLANTED"

        # 50% progress
        crop2 = Crop('RADISH', planted_at=current_time - 15)
        assert crop2.current_stage.value in ["SPROUTING", "GROWING", "FLOWERING"]

        # Ready (100% progress)
        crop3 = Crop('RADISH', planted_at=current_time - 35)
        assert crop3.current_stage.value == "READY"


class TestFarm:
    """Test farm management."""

    @pytest.fixture
    def farm(self):
        """Create a farm for testing."""
        return Farm(4, 4)

    def test_farm_creation(self, farm):
        """Test basic farm creation."""
        assert farm.width == 4
        assert farm.height == 4
        assert len(farm.plots) == 16

    def test_plant_crop(self, farm):
        """Test planting a crop."""
        assert farm.plant_crop(0, 0, 'RADISH')
        assert farm.get_crop(0, 0) is not None

    def test_plant_on_occupied_plot(self, farm):
        """Test that planting on occupied plot fails."""
        farm.plant_crop(0, 0, 'RADISH')
        assert not farm.plant_crop(0, 0, 'CARROT')

    def test_plant_out_of_bounds(self, farm):
        """Test that planting out of bounds fails."""
        assert not farm.plant_crop(-1, 0, 'RADISH')
        assert not farm.plant_crop(0, -1, 'RADISH')
        assert not farm.plant_crop(10, 0, 'RADISH')
        assert not farm.plant_crop(0, 10, 'RADISH')

    def test_harvest_crop(self, farm):
        """Test harvesting a crop."""
        farm.plant_crop(0, 0, 'RADISH')
        crop = farm.harvest_crop(0, 0)

        assert crop is not None
        assert farm.get_crop(0, 0) is None

    def test_harvest_empty_plot(self, farm):
        """Test that harvesting empty plot returns None."""
        crop = farm.harvest_crop(0, 0)
        assert crop is None

    def test_get_ready_crops(self, farm):
        """Test getting ready crops."""
        # Plant some crops
        farm.plant_crop(0, 0, 'RADISH')
        farm.plant_crop(1, 1, 'CARROT')

        # Make them ready by manipulating time
        past_time = time.time() - 100
        farm.plots[(0, 0)].planted_at = past_time
        farm.plots[(1, 1)].planted_at = past_time

        ready_crops = farm.get_ready_crops()
        assert len(ready_crops) == 2

    def test_farm_expansion(self, farm):
        """Test farm expansion."""
        assert farm.expand(6, 6)
        assert farm.width == 6
        assert farm.height == 6
        assert len(farm.plots) == 36

    def test_farm_cannot_shrink(self, farm):
        """Test that farm cannot shrink."""
        assert not farm.expand(2, 2)
        assert farm.width == 4
        assert farm.height == 4

    def test_farm_serialization(self, farm):
        """Test farm serialization and deserialization."""
        farm.plant_crop(1, 1, 'WHEAT')
        data = farm.to_dict()
        farm2 = Farm.from_dict(data)

        assert farm2.width == farm.width
        assert farm2.height == farm.height
        assert farm2.get_crop(1, 1) is not None
        assert farm2.get_crop(1, 1).crop_type == 'WHEAT'


class TestPlayer:
    """Test player progression."""

    @pytest.fixture
    def player(self):
        """Create a player for testing."""
        return Player()

    def test_player_creation(self, player):
        """Test basic player creation."""
        assert player.coins == 100
        assert player.level == 1
        assert player.experience == 0

    def test_spend_coins_success(self, player):
        """Test spending coins successfully."""
        assert player.spend_coins(50)
        assert player.coins == 50

    def test_spend_coins_failure(self, player):
        """Test spending more coins than available."""
        assert not player.spend_coins(200)
        assert player.coins == 100  # Unchanged

    def test_add_coins(self, player):
        """Test adding coins."""
        player.add_coins(50)
        assert player.coins == 150

    def test_add_experience_single_level(self, player):
        """Test gaining a single level."""
        levels = player.add_experience(XP_PER_LEVEL)
        assert levels == 1
        assert player.level == 2
        assert player.experience == 0

    def test_add_experience_multiple_levels(self, player):
        """Test gaining multiple levels."""
        # Level 1 needs 100 XP, Level 2 needs 200 XP, Level 3 needs 300 XP
        # So to gain 3 levels, we need 100 + 200 + 300 = 600 XP
        levels = player.add_experience(600)
        assert levels == 3
        assert player.level == 4
        assert player.experience == 0

    def test_add_experience_partial(self, player):
        """Test adding partial experience."""
        levels = player.add_experience(50)
        assert levels == 0
        assert player.level == 1
        assert player.experience == 50

    def test_xp_progress(self, player):
        """Test XP progress calculation."""
        assert player.xp_progress == 0.0
        player.add_experience(50)
        assert player.xp_progress == 0.5
        player.add_experience(50)
        assert player.xp_progress == 0.0  # Leveled up

    def test_unlock_crop(self, player):
        """Test crop unlocking."""
        player.unlock_crop('WHEAT')
        assert player.has_crop_unlocked('WHEAT')

    def test_player_serialization(self, player):
        """Test player serialization and deserialization."""
        player.spend_coins(10)
        player.add_experience(50)
        player.unlock_crop('WHEAT')

        data = player.to_dict()
        player2 = Player.from_dict(data)

        assert player2.level == player.level
        assert player2.coins == player.coins
        assert player2.experience == player.experience
        assert player2.has_crop_unlocked('WHEAT')


class TestSaveSystem:
    """Test save/load system."""

    @pytest.fixture
    def game_state(self):
        """Create a game state for testing."""
        farm = Farm(4, 4)
        player = Player()
        farm.plant_crop(0, 0, 'RADISH')
        player.spend_coins(10)
        return farm, player

    def test_save_game(self, game_state):
        """Test saving game."""
        farm, player = game_state
        assert SaveSystem.save_game(farm, player)

    def test_load_game(self, game_state):
        """Test loading game."""
        farm, player = game_state
        SaveSystem.save_game(farm, player)

        result = SaveSystem.load_game()
        assert result is not None

        loaded_farm, loaded_player, summary = result
        assert loaded_farm.width == 4
        assert loaded_player.coins == 90
        assert loaded_farm.get_crop(0, 0) is not None

    def test_offline_progression(self, game_state):
        """Test offline progression calculation."""
        farm, player = game_state

        # Make crop ready by manipulating planted_at
        crop = farm.get_crop(0, 0)
        past_time = time.time() - 100  # 100 seconds ago
        crop.planted_at = past_time

        # Save with old timestamp to simulate offline time
        SaveSystem.save_game(farm, player)

        # Manually manipulate save file timestamp to simulate 20 seconds offline
        import json
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        data['last_save'] = time.time() - 20  # 20 seconds ago
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)

        result = SaveSystem.load_game()
        assert result is not None

        loaded_farm, loaded_player, summary = result

        # Crop should have been auto-harvested (planted 100s ago, ready at 30s)
        assert loaded_farm.get_crop(0, 0) is None
        assert summary['auto_harvested']
        assert summary['total_coins'] > 0
        assert loaded_player.coins > player.coins

    def test_create_new_game(self):
        """Test creating a new game."""
        farm, player = SaveSystem.create_new_game()

        assert farm.width == 4
        assert farm.height == 4
        assert player.coins == 100
        assert player.level == 1


@pytest.mark.parametrize("crop_type,expected_growth_time", [
    ('RADISH', 30),
    ('CARROT', 60),
    ('WHEAT', 120),
    ('TOMATO', 180),
    ('CORN', 300),
    ('PUMPKIN', 600),
])
def test_crop_configurations(crop_type, expected_growth_time):
    """Test that crop configurations are correct."""
    config = CROPS[crop_type]
    assert config.growth_time == expected_growth_time
    assert config.seed_cost > 0
    assert config.sell_price > 0
    assert config.profit >= 0  # Should be profitable


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
