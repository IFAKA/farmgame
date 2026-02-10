"""Individual farm plot widget."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, Label
from textual.reactive import reactive
from textual.message import Message
from typing import Optional

from models.crop import Crop


class PlotWidget(Static, can_focus=True):
    """A single farm plot that can contain a crop."""

    crop: reactive[Optional[Crop]] = reactive(None)

    def __init__(self, x: int, y: int, **kwargs) -> None:
        """
        Initialize plot widget.

        Args:
            x: X coordinate in farm grid
            y: Y coordinate in farm grid
        """
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.add_class("plot")

    def render(self) -> str:
        """Render the plot content."""
        if self.crop is None:
            return self._render_empty()
        else:
            return self._render_crop()

    def _render_empty(self) -> str:
        """Render an empty plot."""
        return (
            "[dim]⬛[/dim]\n"
            "[dim]Empty[/dim]\n"
            "[dim]Press Enter[/dim]"
        )

    def _render_crop(self) -> str:
        """Render a growing or ready crop."""
        crop = self.crop
        emoji = crop.config.emoji
        stage_emoji = crop.stage_emoji
        progress_bar = crop.progress_bar
        time_remaining = crop.time_remaining

        # Combine crop emoji with stage emoji
        display_emoji = f"{emoji}{stage_emoji}"

        if crop.is_ready:
            return (
                f"[green bold]{display_emoji}[/green bold]\n"
                f"[green]{crop.config.name}[/green]\n"
                f"[green bold]READY![/green bold]"
            )
        else:
            return (
                f"{display_emoji}\n"
                f"[yellow]{progress_bar}[/yellow]\n"
                f"[dim]{time_remaining}[/dim]"
            )

    def watch_crop(self, old_crop: Optional[Crop], new_crop: Optional[Crop]) -> None:
        """React to crop changes."""
        self.update_border_color()
        self.refresh()

    def update_border_color(self) -> None:
        """Update border color based on crop state."""
        # Remove all state classes
        self.remove_class("empty")
        self.remove_class("growing")
        self.remove_class("ready")

        if self.crop is None:
            self.add_class("empty")
        elif self.crop.is_ready:
            self.add_class("ready")
        else:
            self.add_class("growing")

    def update_display(self) -> None:
        """Refresh the display (called periodically)."""
        if self.crop is not None:
            self.watch_crop(self.crop, self.crop)

    async def on_click(self) -> None:
        """Handle click on plot."""
        # Post custom message for parent to handle
        self.post_message(PlotClicked(self.x, self.y, self.crop))

    async def on_key(self, event) -> None:
        """Handle keyboard input."""
        if event.key in ("enter", "space"):
            # Trigger same action as click
            self.post_message(PlotClicked(self.x, self.y, self.crop))
            event.prevent_default()
            event.stop()


class PlotClicked(Message):
    """Message sent when a plot is clicked."""

    def __init__(self, x: int, y: int, crop: Optional[Crop]):
        super().__init__()
        self.x = x
        self.y = y
        self.crop = crop
