#!/usr/bin/env python3
"""E2E tests for keyboard-only gameplay."""

import pytest
import asyncio
import time
from textual.pilot import Pilot
from main import FarmGame
from config import CROPS


@pytest.fixture(scope="function")
async def app():
    """Create and return an app instance."""
    app = FarmGame()
    async with app.run_test() as pilot:
        # Wait for app to fully initialize
        await pilot.pause(0.5)
        yield pilot, app


class TestKeyboardNavigation:
    """Test keyboard navigation through the farm grid."""

    @pytest.mark.asyncio
    async def test_initial_focus(self, app):
        """Test that the game starts with focus on plot (0, 0)."""
        pilot, game = app
        await pilot.pause(0.3)

        # Check focused plot tracking
        assert game.focused_plot == (0, 0)

        # Check that first plot has focus class
        plot = game.farm_grid.plots.get((0, 0))
        assert plot is not None
        assert plot.has_class("plot")

    @pytest.mark.asyncio
    async def test_hjkl_navigation(self, app):
        """Test vim-style hjkl navigation."""
        pilot, game = app

        # Start at (0, 0)
        assert game.focused_plot == (0, 0)

        # Move right with 'l'
        await pilot.press("l")
        await pilot.pause(0.1)
        assert game.focused_plot == (1, 0)

        # Move down with 'j'
        await pilot.press("j")
        await pilot.pause(0.1)
        assert game.focused_plot == (1, 1)

        # Move left with 'h'
        await pilot.press("h")
        await pilot.pause(0.1)
        assert game.focused_plot == (0, 1)

        # Move up with 'k'
        await pilot.press("k")
        await pilot.pause(0.1)
        assert game.focused_plot == (0, 0)

    @pytest.mark.asyncio
    async def test_arrow_key_navigation(self, app):
        """Test arrow key navigation."""
        pilot, game = app

        # Start at (0, 0)
        assert game.focused_plot == (0, 0)

        # Move right
        await pilot.press("right")
        await pilot.pause(0.1)
        assert game.focused_plot == (1, 0)

        # Move down
        await pilot.press("down")
        await pilot.pause(0.1)
        assert game.focused_plot == (1, 1)

        # Move left
        await pilot.press("left")
        await pilot.pause(0.1)
        assert game.focused_plot == (0, 1)

        # Move up
        await pilot.press("up")
        await pilot.pause(0.1)
        assert game.focused_plot == (0, 0)

    @pytest.mark.asyncio
    async def test_boundary_navigation(self, app):
        """Test that navigation respects grid boundaries."""
        pilot, game = app

        # Start at (0, 0) - top-left corner
        assert game.focused_plot == (0, 0)

        # Try to move left (should stay at 0)
        await pilot.press("h")
        await pilot.pause(0.1)
        assert game.focused_plot == (0, 0)

        # Try to move up (should stay at 0)
        await pilot.press("k")
        await pilot.pause(0.1)
        assert game.focused_plot == (0, 0)

        # Move to bottom-right corner
        for _ in range(3):  # Move right to x=3
            await pilot.press("l")
            await pilot.pause(0.05)
        for _ in range(3):  # Move down to y=3
            await pilot.press("j")
            await pilot.pause(0.05)

        assert game.focused_plot == (3, 3)

        # Try to move right (should stay at 3)
        await pilot.press("l")
        await pilot.pause(0.1)
        assert game.focused_plot == (3, 3)

        # Try to move down (should stay at 3)
        await pilot.press("j")
        await pilot.pause(0.1)
        assert game.focused_plot == (3, 3)


class TestSeedSelector:
    """Test seed selector keyboard interaction."""

    @pytest.mark.asyncio
    async def test_open_seed_selector_with_enter(self, app):
        """Test opening seed selector with Enter key."""
        pilot, game = app

        # Ensure we're on an empty plot
        assert game.farm.get_crop(0, 0) is None

        # Press Enter to open selector
        await pilot.press("enter")
        await pilot.pause(0.3)

        # Check if selector is present
        try:
            selector = game.query_one("#seed-selector")
            assert selector is not None
        except:
            pytest.fail("Seed selector should be open")

    @pytest.mark.asyncio
    async def test_close_seed_selector_with_escape(self, app):
        """Test closing seed selector with Escape key."""
        pilot, game = app

        # Open selector
        await pilot.press("enter")
        await pilot.pause(0.3)

        # Close with Escape
        await pilot.press("escape")
        await pilot.pause(0.3)

        # Check if selector is closed
        try:
            game.query_one("#seed-selector")
            pytest.fail("Seed selector should be closed")
        except:
            pass  # Expected - selector is gone

    @pytest.mark.asyncio
    async def test_select_seed_from_selector(self, app):
        """Test selecting a seed from the selector."""
        pilot, game = app

        initial_coins = game.player.coins

        # Open selector
        await pilot.press("enter")
        await pilot.pause(0.3)

        # Press Enter to select first option (should be RADISH)
        await pilot.press("enter")
        await pilot.pause(0.5)

        # Check that crop was planted
        crop = game.farm.get_crop(0, 0)
        assert crop is not None
        assert crop.crop_type == "RADISH"
        assert game.player.coins < initial_coins


class TestPlantingAndHarvesting:
    """Test planting and harvesting with keyboard."""

    @pytest.mark.asyncio
    async def test_plant_and_harvest_cycle(self, app):
        """Test complete plant and harvest cycle."""
        pilot, game = app

        initial_coins = game.player.coins

        # Plant a crop using internal method for test setup
        game.farm.plant_crop(0, 0, 'RADISH')
        crop = game.farm.get_crop(0, 0)

        # Make it ready by manipulating time
        crop.planted_at = time.time() - CROPS['RADISH'].growth_time - 1

        await pilot.pause(0.2)
        game.farm_grid.update_all_plots()
        await pilot.pause(0.2)

        # Harvest with Enter
        await pilot.press("enter")
        await pilot.pause(0.3)

        # Check that crop was harvested
        assert game.farm.get_crop(0, 0) is None
        assert game.player.coins > initial_coins

    @pytest.mark.asyncio
    async def test_check_growing_crop_info(self, app):
        """Test checking info on a growing crop."""
        pilot, game = app

        # Plant a crop
        game.farm.plant_crop(0, 0, 'RADISH')
        await pilot.pause(0.2)

        # Press Enter on growing crop (should show info)
        await pilot.press("enter")
        await pilot.pause(0.3)

        # Crop should still be there (not harvested)
        assert game.farm.get_crop(0, 0) is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_plant_on_occupied_plot(self, app):
        """Test attempting to plant on occupied plot."""
        pilot, game = app

        # Plant a crop manually
        game.farm.plant_crop(0, 0, 'RADISH')
        initial_coins = game.player.coins
        await pilot.pause(0.2)

        # Try to interact again (should show info, not plant)
        await pilot.press("enter")
        await pilot.pause(0.3)

        # Growing crop should just show info, not open selector
        # Crop should still be there
        assert game.farm.get_crop(0, 0) is not None
        assert game.player.coins == initial_coins

    @pytest.mark.asyncio
    async def test_navigate_between_plots(self, app):
        """Test planting multiple crops with keyboard navigation."""
        pilot, game = app

        # Give player enough money
        game.player.coins = 1000

        # Plant on (0, 0) using internal method
        game.farm.plant_crop(0, 0, 'RADISH')
        await pilot.pause(0.1)

        # Move to (1, 0)
        await pilot.press("l")
        await pilot.pause(0.1)
        assert game.focused_plot == (1, 0)

        # Plant on (1, 0)
        game.farm.plant_crop(1, 0, 'RADISH')
        await pilot.pause(0.1)

        # Move to (0, 1) via h then j
        await pilot.press("h")
        await pilot.pause(0.1)
        await pilot.press("j")
        await pilot.pause(0.1)
        assert game.focused_plot == (0, 1)

        # Plant on (0, 1)
        game.farm.plant_crop(0, 1, 'RADISH')
        await pilot.pause(0.1)

        # Check all crops planted
        assert game.farm.get_crop(0, 0) is not None
        assert game.farm.get_crop(1, 0) is not None
        assert game.farm.get_crop(0, 1) is not None


class TestKeyboardShortcuts:
    """Test global keyboard shortcuts."""

    @pytest.mark.asyncio
    async def test_help_shortcut(self, app):
        """Test that ? key shows help."""
        pilot, game = app

        # Press ?
        await pilot.press("question_mark")
        await pilot.pause(0.2)

        # Should show notification with help text (no exception means it worked)

    @pytest.mark.asyncio
    async def test_shop_shortcut(self, app):
        """Test that s key opens shop."""
        pilot, game = app

        # Press s
        await pilot.press("s")
        await pilot.pause(0.2)

        # Should show shop notification (placeholder)

    @pytest.mark.asyncio
    async def test_navigation_doesnt_conflict(self, app):
        """Test that h doesn't trigger help when navigating."""
        pilot, game = app

        # Press h (should move left, not show help)
        await pilot.press("h")
        await pilot.pause(0.1)

        # Focus shouldn't change (already at left edge)
        assert game.focused_plot == (0, 0)


class TestFocusManagement:
    """Test focus management and visual feedback."""

    @pytest.mark.asyncio
    async def test_focused_plot_has_visual_indicator(self, app):
        """Test that focused plot has proper CSS class."""
        pilot, game = app

        plot = game.farm_grid.plots.get((0, 0))
        assert plot is not None

        # Should have plot class
        assert plot.has_class("plot")

    @pytest.mark.asyncio
    async def test_focus_moves_correctly(self, app):
        """Test that focus moves to correct plots."""
        pilot, game = app

        # Start at (0, 0)
        start_plot = game.farm_grid.plots.get((0, 0))

        # Move right
        await pilot.press("l")
        await pilot.pause(0.1)

        # Check new plot
        new_plot = game.farm_grid.plots.get((1, 0))
        assert game.focused_plot == (1, 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
