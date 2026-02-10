"""Sidebar with player stats."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual.reactive import reactive

from models.player import Player


class Sidebar(Container):
    """Displays player resources and stats."""

    coins = reactive(0)
    level = reactive(1)
    experience = reactive(0)
    xp_for_next = reactive(100)
    ready_count = reactive(0)

    def compose(self) -> ComposeResult:
        """Create sidebar content."""
        yield Static(id="stats-display")

    def render_stats(self) -> str:
        """Render stats content."""
        xp_progress = int((self.experience / self.xp_for_next) * 20) if self.xp_for_next > 0 else 0
        xp_bar = "█" * xp_progress + "░" * (20 - xp_progress)

        return (
            f"[bold cyan]💰 Coins:[/bold cyan] {self.coins}\n"
            f"[bold yellow]⭐ Level:[/bold yellow] {self.level}\n"
            f"[bold magenta]XP:[/bold magenta] {self.experience}/{self.xp_for_next}\n"
            f"[yellow]{xp_bar}[/yellow]\n"
            f"\n"
            f"[bold green]✨ Ready:[/bold green] {self.ready_count}\n"
            f"\n"
            f"[dim]─────────────────[/dim]\n"
            f"[bold]Controls:[/bold]\n"
            f"[dim]hjkl/Arrows - Navigate[/dim]\n"
            f"[dim]Enter/Space - Select[/dim]\n"
            f"[dim]Esc - Cancel[/dim]\n"
            f"[dim]? - Help | S - Shop[/dim]\n"
            f"[dim]Q - Quit[/dim]\n"
        )

    def watch_coins(self, old_value: int, new_value: int) -> None:
        """Update display when coins change."""
        self._update_display()

    def watch_level(self, old_value: int, new_value: int) -> None:
        """Update display when level changes."""
        self._update_display()

    def watch_experience(self, old_value: int, new_value: int) -> None:
        """Update display when XP changes."""
        self._update_display()

    def watch_xp_for_next(self, old_value: int, new_value: int) -> None:
        """Update display when XP requirement changes."""
        self._update_display()

    def watch_ready_count(self, old_value: int, new_value: int) -> None:
        """Update display when ready count changes."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the stats display."""
        stats_display = self.query_one("#stats-display", Static)
        stats_display.update(self.render_stats())

    def update_from_player(self, player: Player, ready_count: int) -> None:
        """
        Update sidebar from player state.

        Args:
            player: Player object
            ready_count: Number of ready crops
        """
        self.coins = player.coins
        self.level = player.level
        self.experience = player.experience
        self.xp_for_next = player.xp_for_next_level
        self.ready_count = ready_count
