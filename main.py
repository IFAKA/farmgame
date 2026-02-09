#!/usr/bin/env python3
"""TUI Farming Game - Main application."""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, Center, Middle
from textual.widgets import Static, Button, Header, Footer
from textual.reactive import reactive
from textual.binding import Binding
from textual import work

from models.farm import Farm
from models.player import Player
from systems.save_system import SaveSystem
from widgets.farm_grid import FarmGrid
from widgets.sidebar import Sidebar
from widgets.plot import PlotClicked
from config import (
    AUTO_SAVE_INTERVAL, GROWTH_UPDATE_INTERVAL, CROPS,
    XP_PER_HARVEST
)


class SeedSelector(Container):
    """Modal for selecting seeds to plant."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True, show=False),
        Binding("up", "focus_previous", "Previous", priority=True, show=False),
        Binding("down", "focus_next", "Next", priority=True, show=False),
        Binding("k", "focus_previous", "Previous", priority=True, show=False),
        Binding("j", "focus_next", "Next", priority=True, show=False),
        Binding("tab", "focus_next", "Next", priority=True, show=False),
        Binding("shift+tab", "focus_previous", "Previous", priority=True, show=False),
    ]

    def __init__(self, player: Player, on_select, on_cancel):
        super().__init__(id="seed-selector")
        self.player = player
        self.on_select = on_select
        self.on_cancel = on_cancel

    def compose(self) -> ComposeResult:
        """Create seed selector content."""
        with Center():
            with Middle():
                with Vertical(id="seed-content"):
                    yield Static("🌱 Select Seed to Plant", id="seed-selector-title")

                    with Vertical(id="seed-list"):
                        for crop_type, config in CROPS.items():
                            if config.unlock_level > self.player.level:
                                # Locked crop
                                yield Static(
                                    f"[dim]{config.emoji} {config.name} - 🔒 Level {config.unlock_level}[/dim]",
                                    classes="seed-option seed-option-locked"
                                )
                            else:
                                can_afford = self.player.coins >= config.seed_cost
                                color = "green" if can_afford else "red"
                                yield Button(
                                    f"{config.emoji} {config.name} - {config.seed_cost}💰 ({config.growth_time}s)",
                                    id=f"seed-{crop_type}",
                                    classes="seed-option"
                                )

                    yield Button("Cancel", id="seed-cancel", variant="error")

    async def on_mount(self) -> None:
        """Focus first button when mounted."""
        # Prevent focus from going to elements behind the modal
        self.can_focus = True
        # Focus the first button
        buttons = self.query("Button")
        if buttons:
            buttons.first().focus()

    def action_cancel(self) -> None:
        """Handle cancel action."""
        self.on_cancel()

    def action_focus_previous(self) -> None:
        """Focus previous button, cycling within modal."""
        buttons = list(self.query("Button"))
        if not buttons:
            return

        # Find currently focused button
        focused = self.screen.focused
        if focused in buttons:
            current_idx = buttons.index(focused)
            # Cycle to previous (or wrap to last)
            prev_idx = (current_idx - 1) % len(buttons)
            buttons[prev_idx].focus()
        else:
            # No button focused, focus first
            buttons[0].focus()

    def action_focus_next(self) -> None:
        """Focus next button, cycling within modal."""
        buttons = list(self.query("Button"))
        if not buttons:
            return

        # Find currently focused button
        focused = self.screen.focused
        if focused in buttons:
            current_idx = buttons.index(focused)
            # Cycle to next (or wrap to first)
            next_idx = (current_idx + 1) % len(buttons)
            buttons[next_idx].focus()
        else:
            # No button focused, focus first
            buttons[0].focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "seed-cancel":
            self.on_cancel()
        elif button_id and button_id.startswith("seed-"):
            crop_type = button_id[5:]  # Remove "seed-" prefix
            self.on_select(crop_type)


class OfflineSummary(Container):
    """Modal showing offline progression summary."""

    BINDINGS = [
        Binding("escape", "close", "Close", priority=True, show=False),
        Binding("enter", "close", "Close", priority=True, show=False),
        Binding("space", "close", "Close", priority=True, show=False),
    ]

    def __init__(self, summary: dict, on_close):
        super().__init__(id="offline-summary")
        self.summary = summary
        self.on_close = on_close

    def compose(self) -> ComposeResult:
        """Create offline summary content."""
        with Center():
            with Middle():
                with Vertical(id="offline-content-container"):
                    yield Static("🌙 Welcome Back!", id="offline-title")

                    # Format offline time
                    hours = int(self.summary['offline_time'] // 3600)
                    minutes = int((self.summary['offline_time'] % 3600) // 60)
                    time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                    content = f"[bold]You were away for {time_str}[/bold]\n\n"

                    if self.summary['auto_harvested']:
                        content += "[green]Auto-harvested crops (70% value):[/green]\n"
                        for crop_name, coins in self.summary['auto_harvested']:
                            content += f"  • {crop_name}: +{coins}💰\n"
                        content += f"\n[bold green]Total earned: {self.summary['total_coins']}💰[/bold green]"
                    else:
                        content += "[dim]No crops were ready to harvest.[/dim]"

                    yield Static(content, id="offline-content")
                    yield Static("[dim]Press Escape, Enter, or Space to continue[/dim]", id="offline-footer")

    async def on_mount(self) -> None:
        """Focus modal when mounted to capture keyboard input."""
        self.can_focus = True
        self.focus()

    def action_close(self) -> None:
        """Handle close action."""
        self.on_close()

    async def on_key(self, event) -> None:
        """Close on any key press (fallback for other keys)."""
        # Allow specific keys through bindings, but also accept any other key
        if event.key not in ["escape", "enter", "space"]:
            self.on_close()
            event.prevent_default()
            event.stop()


class FarmGame(App):
    """Main farming game application."""

    CSS_PATH = "styles/farmgame.tcss"
    TITLE = "🌱 TUI Farm Game"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("s", "shop", "Shop"),
        Binding("?", "help", "Help"),
        # Vim-style navigation
        Binding("h", "focus_left", "Left", show=False),
        Binding("j", "focus_down", "Down", show=False),
        Binding("k", "focus_up", "Up", show=False),
        Binding("l", "focus_right", "Right", show=False),
        # Arrow key navigation
        Binding("left", "focus_left", "Left", show=False),
        Binding("down", "focus_down", "Down", show=False),
        Binding("up", "focus_up", "Up", show=False),
        Binding("right", "focus_right", "Right", show=False),
    ]

    # Reactive state
    coins = reactive(0)
    level = reactive(1)
    experience = reactive(0)

    def __init__(self):
        super().__init__()
        self.farm: Farm = None
        self.player: Player = None
        self.farm_grid: FarmGrid = None
        self.sidebar: Sidebar = None
        self._save_worker = None
        self._update_worker = None
        self.focused_plot = (0, 0)  # Track focused plot coordinates

    def compose(self) -> ComposeResult:
        """Create main layout."""
        yield Header()

        with Container(id="main-container"):
            # Will be populated in on_mount
            yield Container(id="farm-container")
            yield Sidebar(id="sidebar")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize game on mount."""
        # Load or create game
        save_data = SaveSystem.load_game()

        if save_data:
            self.farm, self.player, offline_summary = save_data

            # Show offline summary if significant (>5 min OR crops were harvested)
            if offline_summary['offline_time'] > 300 or offline_summary['auto_harvested']:
                await self._show_offline_summary(offline_summary)
            elif offline_summary['offline_time'] > 60:
                # Short offline time - just show a toast
                minutes = int(offline_summary['offline_time'] // 60)
                self.notify(f"🌙 Welcome back! You were away for {minutes}m", timeout=3)
        else:
            self.farm, self.player = SaveSystem.create_new_game()
            self.notify("🌱 Welcome to TUI Farm! Plant your first crop!", severity="information", timeout=5)

        # Build UI now that we have farm data
        farm_container = self.query_one("#farm-container")
        self.farm_grid = FarmGrid(self.farm)
        await farm_container.mount(self.farm_grid)

        # Get sidebar reference
        self.sidebar = self.query_one("#sidebar", Sidebar)

        # Update UI
        await self._refresh_ui()

        # Set initial focus to first plot (with small delay to ensure plots are ready)
        self.set_timer(0.1, lambda: self._set_plot_focus(0, 0))

        # Start background workers
        self._start_workers()

    def _start_workers(self) -> None:
        """Start background worker tasks."""
        self.set_interval(AUTO_SAVE_INTERVAL, self._auto_save)
        self.set_interval(GROWTH_UPDATE_INTERVAL, self._growth_update)

    def _auto_save(self) -> None:
        """Auto-save game every 30 seconds."""
        if self.farm and self.player:
            SaveSystem.save_game(self.farm, self.player)
            self.notify("💾 Auto-saved", timeout=2)

    def _growth_update(self) -> None:
        """Update crop growth every second."""
        if self.farm_grid:
            self.farm_grid.update_all_plots()
            self._update_sidebar_sync()

    async def _refresh_ui(self) -> None:
        """Refresh entire UI."""
        if self.farm_grid:
            self.farm_grid.update_all_plots()
        await self._update_sidebar()

    async def _update_sidebar(self) -> None:
        """Update sidebar stats."""
        if self.sidebar and self.player and self.farm:
            ready_count = len(self.farm.get_ready_crops())
            self.sidebar.update_from_player(self.player, ready_count)

    def _update_sidebar_sync(self) -> None:
        """Synchronous version of _update_sidebar for thread workers."""
        if self.sidebar and self.player and self.farm:
            ready_count = len(self.farm.get_ready_crops())
            self.sidebar.update_from_player(self.player, ready_count)

    def _set_plot_focus(self, x: int, y: int) -> None:
        """Set focus to a specific plot."""
        if not self.farm_grid:
            return

        plot = self.farm_grid.plots.get((x, y))
        if plot:
            self.focused_plot = (x, y)
            plot.focus()

    def action_focus_left(self) -> None:
        """Move focus left."""
        x, y = self.focused_plot
        new_x = max(0, x - 1)
        if new_x != x:
            self._set_plot_focus(new_x, y)

    def action_focus_right(self) -> None:
        """Move focus right."""
        x, y = self.focused_plot
        new_x = min(self.farm.width - 1, x + 1)
        if new_x != x:
            self._set_plot_focus(new_x, y)

    def action_focus_up(self) -> None:
        """Move focus up."""
        x, y = self.focused_plot
        new_y = max(0, y - 1)
        if new_y != y:
            self._set_plot_focus(x, new_y)

    def action_focus_down(self) -> None:
        """Move focus down."""
        x, y = self.focused_plot
        new_y = min(self.farm.height - 1, y + 1)
        if new_y != y:
            self._set_plot_focus(x, new_y)

    def action_cancel(self) -> None:
        """Cancel/close modals."""
        # Try to close seed selector if open
        try:
            selector = self.query_one("#seed-selector")
            selector.remove()
        except:
            pass

        # Try to close offline summary if open
        try:
            summary = self.query_one("#offline-summary")
            summary.remove()
        except:
            pass

    async def on_plot_clicked(self, message: PlotClicked) -> None:
        """Handle plot click."""
        if message.crop is None:
            # Empty plot - show seed selector
            await self._show_seed_selector(message.x, message.y)
        elif message.crop.is_ready:
            # Ready crop - harvest
            await self._harvest_crop(message.x, message.y)
        else:
            # Growing crop - show info
            crop = message.crop
            time_left = crop.time_remaining
            self.notify(
                f"🌱 {crop.config.name} growing... {time_left} remaining",
                timeout=2
            )

    async def _show_seed_selector(self, x: int, y: int) -> None:
        """Show seed selection modal."""
        # Remove existing selector if present
        try:
            existing = self.query_one("#seed-selector")
            await existing.remove()
        except:
            pass

        def on_select(crop_type: str):
            self.app.call_later(self._plant_crop, x, y, crop_type)
            selector.remove()
            # Restore focus to the plot after closing modal
            self.set_timer(0.05, lambda: self._set_plot_focus(x, y))

        def on_cancel():
            selector.remove()
            # Restore focus to the plot after closing modal
            self.set_timer(0.05, lambda: self._set_plot_focus(x, y))

        selector = SeedSelector(self.player, on_select, on_cancel)
        await self.mount(selector)

    async def _plant_crop(self, x: int, y: int, crop_type: str) -> None:
        """Plant a crop at the given position."""
        config = CROPS[crop_type]

        # Check if player can afford
        if not self.player.spend_coins(config.seed_cost):
            self.notify(f"⚠️ Not enough coins! Need {config.seed_cost}💰", severity="warning")
            return

        # Plant the crop
        if self.farm.plant_crop(x, y, crop_type):
            self.player.total_crops_planted += 1
            self.notify(f"🌱 Planted {config.name}!", severity="information")
            await self._refresh_ui()
        else:
            # Refund if planting failed
            self.player.add_coins(config.seed_cost)
            self.notify("⚠️ Could not plant here", severity="error")

    async def _harvest_crop(self, x: int, y: int) -> None:
        """Harvest a crop."""
        crop = self.farm.harvest_crop(x, y)

        if crop is None:
            return

        # Add coins and XP
        self.player.add_coins(crop.config.sell_price)
        self.player.total_crops_harvested += 1

        levels_gained = self.player.add_experience(XP_PER_HARVEST)

        # Notifications
        self.notify(
            f"✨ Harvested {crop.config.emoji}! +{crop.config.sell_price}💰 +{XP_PER_HARVEST}✨",
            severity="information"
        )

        # Handle level ups
        if levels_gained > 0:
            await self._handle_level_up(levels_gained)

        await self._refresh_ui()

    async def _handle_level_up(self, levels_gained: int) -> None:
        """Handle level up rewards."""
        for _ in range(levels_gained):
            # Check for crop unlocks
            for crop_type, config in CROPS.items():
                if config.unlock_level == self.player.level:
                    self.player.unlock_crop(crop_type)
                    self.notify(
                        f"🎉 Level {self.player.level}! {config.name} unlocked!",
                        severity="information",
                        timeout=5
                    )
                    return

            # Generic level up
            self.notify(
                f"🎉 Level {self.player.level}!",
                severity="information",
                timeout=3
            )

    async def _show_offline_summary(self, summary: dict) -> None:
        """Show offline progression summary modal."""
        # Remove existing modal if present
        try:
            existing = self.query_one("#offline-summary")
            await existing.remove()
        except:
            pass

        def on_close():
            modal.remove()
            # Restore focus to the current plot
            x, y = self.focused_plot
            self.set_timer(0.05, lambda: self._set_plot_focus(x, y))

        modal = OfflineSummary(summary, on_close)
        await self.mount(modal)

    def action_shop(self) -> None:
        """Open shop (placeholder)."""
        self.notify("🏪 Shop coming soon!", timeout=2)

    def action_help(self) -> None:
        """Show help."""
        help_text = (
            "[bold]TUI Farm Game Help[/bold]\n\n"
            "[bold]Keyboard Controls:[/bold]\n"
            "hjkl or Arrow Keys: Navigate plots\n"
            "Enter/Space: Interact with plot\n"
            "q: Quit | ?: Help | s: Shop\n\n"
            "[bold]Gameplay:[/bold]\n"
            "🌱 Plant crops on empty plots\n"
            "✨ Harvest ready crops (green border)\n"
            "💰 Earn coins by harvesting\n"
            "⭐ Gain XP to level up and unlock new crops\n\n"
            "[bold]Crops:[/bold]\n"
        )

        for crop_type, config in CROPS.items():
            profit = config.profit
            help_text += f"{config.emoji} {config.name}: {config.growth_time}s, {config.seed_cost}💰 → {config.sell_price}💰 ({profit} profit)\n"

        self.notify(help_text, timeout=10)

    async def on_unmount(self) -> None:
        """Save game on exit."""
        if self.farm and self.player:
            SaveSystem.save_game(self.farm, self.player)


def main():
    """Entry point."""
    app = FarmGame()
    app.run()


if __name__ == "__main__":
    main()
