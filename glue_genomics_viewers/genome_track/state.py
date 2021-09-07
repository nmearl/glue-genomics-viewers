import numpy as np
import pandas as pd

from glue.core import BaseData, Subset

from echo import delay_callback
from glue.viewers.matplotlib.state import (MatplotlibDataViewerState,
                                           MatplotlibLayerState,
                                           DeferredDrawCallbackProperty as DDCProperty,
                                           DeferredDrawSelectionCallbackProperty as DDSCProperty)
from glue.core.state_objects import (StateAttributeLimitsHelper,
                                     StateAttributeHistogramHelper)
from glue.core.exceptions import IncompatibleAttribute, IncompatibleDataException
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.utils import defer_draw, datetime64_to_mpl
from glue.utils.decorators import avoid_circular
from glue.utils import defer_draw, decorate_all_methods

from ..subsets import GenomicRangeSubsetState
from ..data import BedPeData

__all__ = ['GenomeTrackState']


@decorate_all_methods(defer_draw)
class GenomeTrackState(MatplotlibDataViewerState):
    """
    Encapsulates all state for a Genome Track Viewer
    """
    chr = DDCProperty(docstring='The Chromosome to view')
    start = DDCProperty(docstring="Left edge of the window")
    end = DDCProperty(docstring="Right edge of the window")
    loop_count = DDCProperty(docstring="Number of loops to display")

    # TODO: Include a configurable list of tracks. For now hardcode

    def __init__(self, **kwargs):
        super().__init__()

        self.add_callback('start', self.update_view_to_range)
        self.add_callback('end', self.update_view_to_range)

        self.add_callback('x_min', self.update_range_to_view)
        self.add_callback('x_max', self.update_range_to_view)

        self.chr = '3'
        self.start = 100_000
        self.end = 500_000
        self.loop_count = 100

    @avoid_circular
    def update_view_to_range(self, *args):
        with delay_callback(self, 'x_min', 'x_max'):
            self.x_min = self.start
            self.x_max = self.end

    @avoid_circular
    def update_range_to_view(self, *args):
        with delay_callback(self, 'start', 'end'):
            self.start = self.x_min
            self.end = self.x_max

    def expand_y_limits(self, y_min, y_max):
        if y_min is None or y_max is None or not np.isfinite(y_min) or not np.isfinite(y_max):
            return

        if self.y_min is None:
            self.y_min = y_min
        else:
            self.y_min = min(self.y_min, y_min)

        if self.y_max is None:
            self.y_max = y_max
        else:
            self.y_max = max(self.y_min or -np.inf, y_max)


class GenomeTrackLayerState(MatplotlibLayerState):

    _cache = None, None

    def reset_cache(self, *args):
        self._cache = None, None

    @property
    def viewer_state(self) -> GenomeTrackState:
        return self._viewer_state

    @viewer_state.setter
    def viewer_state(self, viewer_state: GenomeTrackState):
        self._viewer_state = viewer_state

    @property
    def viz_data(self) -> pd.DataFrame:
        key = self.viewer_state.chr, int(max(self.viewer_state.start, 0)), int(max(self.viewer_state.end, 0)), self.viewer_state.loop_count
        if key == self._cache[0]:
            return self._cache[1]
        chr, start, end, loop_count = key

        if isinstance(self.layer, Subset):
            data = self.layer.data
            subset_state = self.layer.subset_state
        else:
            data = self.layer
            subset_state = None

        if isinstance(data, BedPeData):
            df = data.profile(chr, start, end, target=loop_count, subset_state=subset_state)
            self.viewer_state.expand_y_limits(0, end - start)
        else:
            df = data.profile(chr, start, end, subset_state=subset_state)
            self.viewer_state.expand_y_limits(df.value.min(), df.value.max(), subset_state=subset_state)

        self._cache = key, df
        return df
