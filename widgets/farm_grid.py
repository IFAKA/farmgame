"""Farm grid container widget."""

from textual.app import ComposeResult
from textual.containers import Container, Grid
from typing import Dict, Tuple, Optional

from widgets.plot import PlotWidget
from models.farm import Farm


class FarmGrid(Container):
    """Container for all farm plots in a grid layout."""

    def __init__(self, farm: Farm, **kwargs) -> None:
        """
        Initialize farm grid.

        Args:
            farm: Farm model to display
        """
        super().__init__(**kwargs)
        self.farm = farm
        self.plots: Dict[Tuple[int, int], PlotWidget] = {}

    def compose(self) -> ComposeResult:
        """Create the grid of plots."""
        with Grid(id="farm-grid") as grid:
            grid.styles.grid_size_columns = self.farm.width
            grid.styles.grid_size_rows = self.farm.height

            for y in range(self.farm.height):
                for x in range(self.farm.width):
                    plot = PlotWidget(x, y)
                    plot.crop = self.farm.get_crop(x, y)
                    self.plots[(x, y)] = plot
                    yield plot

    def update_all_plots(self) -> None:
        """Update all plots (called every second by game loop)."""
        for (x, y), plot in self.plots.items():
            crop = self.farm.get_crop(x, y)
            plot.crop = crop
            plot.update_display()

    def get_plot(self, x: int, y: int) -> Optional[PlotWidget]:
        """Get plot widget at coordinates."""
        return self.plots.get((x, y))
