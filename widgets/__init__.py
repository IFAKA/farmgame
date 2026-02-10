"""
Widgets package.

Contains Textual UI components:
- PlotWidget: Individual farm plot display
- FarmGrid: Grid container for all plots
- Sidebar: Player stats and controls display
- PlotClicked: Message sent when plot is interacted with
"""

__all__ = ['PlotWidget', 'FarmGrid', 'Sidebar', 'PlotClicked']

from widgets.plot import PlotWidget, PlotClicked
from widgets.farm_grid import FarmGrid
from widgets.sidebar import Sidebar
