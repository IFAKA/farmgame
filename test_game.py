#!/usr/bin/env python3
"""Simple test script to verify game functionality."""

import sys
import time
from models.crop import Crop
from models.farm import Farm
from models.player import Player
from systems.save_system import SaveSystem
from config import CROPS

def test_crops():
    """Test crop growth system."""
    print("Testing crops...")

    # Create a radish
    radish = Crop('RADISH')
    assert radish.crop_type == 'RADISH'
    assert radish.config.growth_time == 30
    assert radish.growth_progress >= 0.0
    assert not radish.is_ready

    # Test serialization
    data = radish.to_dict()
    radish2 = Crop.from_dict(data)
    assert radish2.crop_type == radish.crop_type

    print("✓ Crops working")

def test_farm():
    """Test farm management."""
    print("Testing farm...")

    farm = Farm(4, 4)
    assert farm.width == 4
    assert farm.height == 4
    assert len(farm.plots) == 16

    # Plant a crop
    assert farm.plant_crop(0, 0, 'RADISH')
    assert farm.get_crop(0, 0) is not None

    # Can't plant on occupied plot
    assert not farm.plant_crop(0, 0, 'CARROT')

    # Harvest
    crop = farm.harvest_crop(0, 0)
    assert crop is not None
    assert farm.get_crop(0, 0) is None

    # Test serialization
    farm.plant_crop(1, 1, 'WHEAT')
    data = farm.to_dict()
    farm2 = Farm.from_dict(data)
    assert farm2.width == farm.width
    assert farm2.get_crop(1, 1) is not None

    print("✓ Farm working")

def test_player():
    """Test player progression."""
    print("Testing player...")

    player = Player()
    assert player.coins == 100
    assert player.level == 1

    # Spend coins
    assert player.spend_coins(50)
    assert player.coins == 50
    assert not player.spend_coins(100)

    # Add XP
    player.add_coins(50)
    levels = player.add_experience(100)
    assert levels == 1
    assert player.level == 2

    # Test serialization
    data = player.to_dict()
    player2 = Player.from_dict(data)
    assert player2.level == player.level

    print("✓ Player working")

def test_save_system():
    """Test save/load system."""
    print("Testing save system...")

    farm = Farm(4, 4)
    player = Player()
    farm.plant_crop(0, 0, 'RADISH')
    player.spend_coins(10)

    # Save
    assert SaveSystem.save_game(farm, player)

    # Load
    result = SaveSystem.load_game()
    assert result is not None

    loaded_farm, loaded_player, summary = result
    assert loaded_farm.width == 4
    assert loaded_player.coins == 90
    assert loaded_farm.get_crop(0, 0) is not None

    print("✓ Save system working")

def test_crop_growth():
    """Test that crops actually grow over time."""
    print("Testing crop growth over time...")

    # Create a crop with very short growth time
    crop = Crop('RADISH')
    initial_progress = crop.growth_progress

    # Wait a moment
    time.sleep(1)

    new_progress = crop.growth_progress
    assert new_progress > initial_progress, "Crop should have grown"

    print(f"  Progress: {initial_progress:.2%} -> {new_progress:.2%}")
    print("✓ Crop growth working")

def main():
    """Run all tests."""
    print("=" * 50)
    print("TUI Farm Game - Component Tests")
    print("=" * 50)

    try:
        test_crops()
        test_farm()
        test_player()
        test_save_system()
        test_crop_growth()

        print("=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        print("\nYou can now run the game with: python main.py")
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
